import { Link, useLocation } from "react-router-dom";
import { Breadcrumbs } from "@material-tailwind/react";

// Main mapping: route -> breadcrumb label
const breadcrumbNameMap = {
  "/dashboard": "Dashboard",

  // Products
  "/products": "Products",
  "/products/list": "Product List",
  "/products/new": "New Product",
  "/products/:id": "Product Detail",
  "/products/:id/edit": "Edit Product",
  "/products/:id/stock": "Product Stock",
  "/products/:id/history": "Product History",

  // Expiring stock
  "/expiring": "Expiring Products",

  // Categories
  "/categories": "Manage Categories",

  // Warehouses
  "/warehouses": "Warehouses",
  "/warehouses/list": "Warehouse List",
  "/warehouses/new": "New Warehouse",
  "/warehouses/:id": "Warehouse Detail",
  "/warehouses/:id/edit": "Edit Warehouse",

  // Stock by warehouse
  "/stock/warehouse/:warehouse_code": "Warehouse Stock",
  "/stock/warehouse/:warehouse_code/product/:product_code": "Product Stock by Warehouse",
  "/stock/warehouse/:warehouse_code/history": "Warehouse Stock History",
  "/stock/warehouse/:warehouse_id/products/:product_id/history": "Product History by Warehouse",

  // Movements
  "/stock-movements": "Stock Movements",
  "/stock-movements/list": "Movement List",
  "/stock-movements/new": "New Movement",
  "/stock-movements/:id": "Movement Detail",

  // Users
  "/users": "Users",
  "/users/new": "New User",
  "/users/:id/edit": "Edit User",

  // Profile
  "/profile": "User Profile",
};

// Manual overrides for paths with unclear hierarchy
const breadcrumbOverrides = {
  "/stock/warehouse/:warehouse_code": [
    { path: "/warehouses", label: "Warehouses" },
    { path: "/warehouses/list", label: "Warehouse List" },
    { path: null, label: "Warehouse Stock" },
  ],
  "/stock/warehouse/:warehouse_code/product/:product_code": [
    { path: "/products", label: "Products" },
    { path: null, label: "Product Stock by Warehouse" },
  ],
};

const matchOverride = (pathname) => {
  for (const pattern in breadcrumbOverrides) {
    const regex = new RegExp(
      "^" + pattern.replace(/:[^/]+/g, "[^/]+").replace(/\//g, "\\/") + "$"
    );
    if (regex.test(pathname)) return breadcrumbOverrides[pattern];
  }
  return null;
};

const getBreadcrumbLabel = (path) => {
  for (const pattern in breadcrumbNameMap) {
    const regex = new RegExp(
      "^" + pattern.replace(/:[^/]+/g, "[^/]+").replace(/\//g, "\\/") + "$"
    );
    if (regex.test(path)) return breadcrumbNameMap[pattern];
  }
  return null;
};

export default function Breadcrumb() {
  const location = useLocation();
  const pathname = location.pathname;

  const override = matchOverride(pathname);
  const items = [];

  if (override) {
    override.forEach((item, index) => {
      items.push({
        path: item.path,
        label: item.label,
        isLast: index === override.length - 1,
      });
    });
  } else {
    const segments = pathname.split("/").filter(Boolean);
    let pathAccumulator = "";

    segments.forEach((segment, index) => {
      pathAccumulator += `/${segment}`;
      const label = getBreadcrumbLabel(pathAccumulator);
      if (label) {
        items.push({
          path: pathAccumulator,
          label,
          isLast: index === segments.length - 1,
        });
      }
    });
  }

  return (
    <Breadcrumbs className="bg-white px-4 py-2">
      <Link to="/dashboard" className="opacity-60 flex items-center gap-1 mr-1">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
        </svg>
        Home
      </Link>

      {items.map(({ path, label, isLast }) =>
        isLast || !path ? (
          <span key={label}>{label}</span>
        ) : (
          <Link key={path} to={path} className="opacity-60">
            {label}
          </Link>
        )
      )}
    </Breadcrumbs>
  );
}
