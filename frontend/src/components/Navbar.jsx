import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from "@headlessui/react";
import { Bars3Icon, BellIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useAuth } from "../context/useAuth";
import { useLocation, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useWebSocket from "../hooks/useWebSocket";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [activeNotification, setActiveNotification] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  // Load notification history from localStorage
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("notifications") || "[]");
    setNotifications(stored);
  }, []);

  // WebSocket
  useWebSocket((message) => {
    setNotifications((prev) => {
      const updated = [message, ...prev.slice(0, 4)];
      localStorage.setItem("notifications", JSON.stringify(updated));
      return updated;
    });
    setActiveNotification(true);
  });

  const navigation = [
    { name: "Dashboard", href: "/dashboard" },
    {
      name: "Products",
      href: "/products",
      submenu: [
        { name: "List", href: "/products/list" },
        user?.role === "admin" && {
          name: "Create new",
          href: "/products/new",
        },
        { name: "By expiration", href: "/expiring?from_months=0&range_months=6" },
        user?.role === "admin" && {
          name: "Manage categories",
          href: "/categories",
        },
      ].filter(Boolean),
    },
    {
      name: "Stock movements",
      href: "/stock-movements",
      submenu: [
        { name: "List", href: "/stock-movements/list" },
        { name: "Create new", href: "/stock-movements/new" },
      ],
    },
    {
      name: "Warehouses",
      href: "/warehouses",
      submenu: [
        { name: "List", href: "/warehouses/list" },
        user?.role === "admin" && {
          name: "Create new",
          href: "/warehouses/new",
        },
      ].filter(Boolean),
    },
  ];

  if (user?.role === "admin") {
    navigation.push({
      name: "Users",
      href: "/users",
      submenu: [
        { name: "List", href: "/users" },
        { name: "Create new", href: "/users/new" },
      ],
    });
  }

  return (
    <Disclosure as="nav" className="bg-indigo-600">
      <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
        <div className="relative flex h-16 items-center justify-between">
          {/* Mobile menu button */}
          <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
            <DisclosureButton className="group relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-indigo-700 hover:text-white focus:ring-2 focus:ring-white focus:outline-hidden focus:ring-inset">
              <span className="sr-only">Open main menu</span>
              <Bars3Icon className="block size-6 group-data-open:hidden" />
              <XMarkIcon className="hidden size-6 group-data-open:block" />
            </DisclosureButton>
          </div>

          {/* Main navigation */}
          <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
            <div className="hidden sm:ml-6 sm:block">
              <div className="flex space-x-4">
                {navigation.map((item) => {
                  if (!item.submenu) {
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? "bg-indigo-800 text-white"
                            : "text-gray-300 hover:bg-indigo-700 hover:text-white",
                          "rounded-md px-3 py-2 text-sm font-medium"
                        )}
                      >
                        {item.name}
                      </Link>
                    );
                  }

                  // Render submenu
                  return (
                    <Menu
                      as="div"
                      key={item.name}
                      className="relative inline-block text-left"
                    >
                      <div className="flex items-center">
                        <Link
                          to={item.href}
                          className={classNames(
                            location.pathname === item.href
                              ? "bg-indigo-900 text-white"
                              : "text-gray-300 hover:bg-indigo-700 hover:text-white",
                            "rounded-l-md px-3 py-2 text-sm font-medium"
                          )}
                        >
                          {item.name}
                        </Link>
                        <MenuButton className="rounded-r-md px-2 py-2 text-sm font-medium text-gray-300 hover:bg-indigo-700 hover:text-white">
                          ▾
                        </MenuButton>
                      </div>
                      <MenuItems className="absolute z-10 mt-2 w-48 origin-top-left rounded-md bg-white py-1 shadow-lg ring-1 ring-black/5">
                        {item.submenu.map((subitem) => (
                          <MenuItem key={subitem.href}>
                            <Link
                              to={subitem.href}
                              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              {subitem.name}
                            </Link>
                          </MenuItem>
                        ))}
                      </MenuItems>
                    </Menu>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Notifications and user menu */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
            <button
              role="button"
              className="relative"
              type="button"
              onClick={() => {
                setShowDropdown((prev) => !prev);
                setActiveNotification(false);
              }}
            >
              <span className="sr-only">View notifications</span>
              <BellIcon className="size-6 text-white" />
              {activeNotification && (
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white animate-ping" />
              )}

              {showDropdown && (
                <div className="absolute right-0 mt-2 w-64 bg-white shadow-lg rounded-lg p-4 z-50">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">
                    Notifications
                  </h3>
                  <ul className="space-y-1 text-sm text-gray-600 max-h-48 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <li className="italic text-gray-400">
                        No recent notifications
                      </li>
                    ) : (
                      notifications.map((message, idx) => (
                        <li
                          key={idx}
                          className="flex justify-between items-center cursor-pointer hover:bg-gray-100 p-1 rounded"
                          onClick={() => navigate("/stock-movements/list")}
                        >
                          <span>• {message}</span>
                          <button
                            role="button"
                            className="text-lg text-red-500 hover:text-red-700 ml-2"
                            onClick={(e) => {
                              e.stopPropagation();
                              const updated = notifications.filter(
                                (_, i) => i !== idx
                              );
                              setNotifications(updated);
                              localStorage.setItem(
                                "notifications",
                                JSON.stringify(updated)
                              );
                            }}
                          >
                            ✕
                          </button>
                        </li>
                      ))
                    )}
                  </ul>
                </div>
              )}
            </button>

            <Menu as="div" className="relative ml-3">
              <div>
                <MenuButton className="relative flex items-center rounded-full bg-indigo-600 px-3 py-1 text-sm font-medium text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 focus:outline-hidden hover:bg-indigo-700 hover:text-white">
                  <span className="sr-only">Open user menu</span>
                  {user?.name || "User"}
                </MenuButton>
              </div>
              <MenuItems className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 ring-1 shadow-lg ring-black/5">
                <MenuItem>
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Your profile
                  </Link>
                </MenuItem>
                <MenuItem>
                  <button
                    role="button"
                    onClick={logout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Log out
                  </button>
                </MenuItem>
              </MenuItems>
            </Menu>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <DisclosurePanel className="sm:hidden">
        <div className="space-y-1 px-2 pt-2 pb-3">
          {navigation.map((item) => {
            if (!item.submenu) {
              return (
                <DisclosureButton
                  key={item.name}
                  as={Link}
                  to={item.href}
                  className={classNames(
                    location.pathname === item.href
                      ? "bg-indigo-800 text-white"
                      : "text-gray-300 hover:bg-indigo-700 hover:text-white",
                    "block rounded-md px-3 py-2 text-base font-medium"
                  )}
                >
                  {item.name}
                </DisclosureButton>
              );
            }

            return (
              <Disclosure key={item.name} as="div" className="space-y-1">
                <div className="flex items-center justify-between px-3 py-2">
                  <Link
                    to={item.href}
                    className="text-gray-300 hover:bg-indigo-700 hover:text-white rounded-md text-base font-medium"
                  >
                    {item.name}
                  </Link>
                  <DisclosureButton className="text-gray-300 hover:text-white">
                    <svg
                      className="ml-2 h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </DisclosureButton>
                </div>

                <DisclosurePanel className="space-y-1 pl-4">
                  {item.submenu.map((subitem) => (
                    <Link
                      key={subitem.href}
                      to={subitem.href}
                      className="block text-gray-300 hover:bg-indigo-700 hover:text-white rounded-md px-3 py-2 text-sm"
                    >
                      {subitem.name}
                    </Link>
                  ))}
                </DisclosurePanel>
              </Disclosure>
            );
          })}
        </div>
      </DisclosurePanel>
    </Disclosure>
  );
}
