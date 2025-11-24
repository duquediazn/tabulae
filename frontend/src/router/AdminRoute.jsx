import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function AdminRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  if (user?.role !== "admin") {
    alert("Access denied. You do not have permission to view this page.");
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
