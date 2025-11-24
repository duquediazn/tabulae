import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/useAuth"; // Custom hook useAuth that accesses the authentication context

export default function PrivateRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      /> // `replace` prevents this redirect from being added to browser history,
      // so going "back" won't return to the protected route.
    );
  }

  return <Outlet />; // Render the protected content
}
