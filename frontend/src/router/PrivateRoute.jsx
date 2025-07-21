import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/useAuth"; // Custom hook useAuth that accesses the authentication context

export default function PrivateRoute() {
  const { isAuthenticated, isLoading, isLoggingOut } = useAuth();

  if (isLoading) return null;

  // If not authenticated AND not logging out → redirect to login
  if (!isAuthenticated && !isLoggingOut) {
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
