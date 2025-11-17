import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { login as loginAPI, getProfile } from "../api/auth";
import { jwtDecode } from "jwt-decode";
import API_URL from "../api/config";

// Create authentication context
export const AuthContext = createContext();

// Provider
export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null); // The access JWT token (does not include the refresh token, which is stored in a cookie)
  const [user, setUser] = useState(null); // Authenticated user data (name, email, role…)
  const [isLoading, setIsLoading] = useState(true); // Becomes false after verifying if the user is logged in
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false); // Prevents actions while logging out

  // Automatic token refresh
  let refreshTimeout;

  const getTokenExpiration = (token) => {
    try {
      const decoded = jwtDecode(token);
      if (!decoded.exp) return null;

      const expTime = decoded.exp * 1000; // in milliseconds
      const currentTime = Date.now();
      const timeLeft = expTime - currentTime;

      return timeLeft; // time left in ms
    } catch (err) {
      console.error("Error decoding token:", err);
      return null;
    }
  };

  const scheduleTokenRefresh = (token) => {
    clearTimeout(refreshTimeout); // Clear any pending refresh
    const expiresInMs = getTokenExpiration(token);
    const refreshTime = expiresInMs - 5 * 60 * 1000; // 5 minutes before expiration
    if (refreshTime > 0) {
      refreshTimeout = setTimeout(refreshAccessToken, refreshTime);
    } else {
      refreshAccessToken();
    }
  };

  const refreshAccessToken = async () => {
    /* Calls the backend (/auth/refresh) which uses the HttpOnly cookie to generate a new access token. */
    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) throw new Error("Failed to refresh token");

      const data = await response.json();
      setAccessToken(data.access_token);
      scheduleTokenRefresh(data.access_token);

      const userData = await getProfile(data.access_token);
      setUser({
        id: userData.id,
        role: userData.role,
        name: userData.name,
        email: userData.email,
      });
      setIsLoading(false);
    } catch (error) {
      console.error("Could not refresh token:", error);
      setAccessToken(null);
      setUser(null);
      clearTimeout(refreshTimeout);
      setIsLoading(false);
    }
  };

  // Login
  const login = async (email, password) => {
    const data = await loginAPI({ email, password });
    setAccessToken(data.access_token);
    scheduleTokenRefresh(data.access_token);

    const userData = await getProfile(data.access_token);
    setUser({
      id: userData.id,
      role: userData.role,
      name: userData.name,
      email: userData.email,
    });

    navigate("/dashboard");
    localStorage.setItem("login-event", Date.now()); // trigger login event
  };

  // Logout
  const logout = async () => {
    try {
      setIsLoggingOut(true);
      // Call backend to delete the cookie
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include", // Needed to send the cookie
      });
    } catch (error) {
      console.error("Error logging out from backend:", error);
    }

    // Local session cleanup
    localStorage.setItem("logout-event", Date.now()); // trigger logout event
    setAccessToken(null);
    setUser(null);
    clearTimeout(refreshTimeout);
    navigate("/login");
  };

  useEffect(() => {
    refreshAccessToken();
  }, []); // Run once when the app loads

  /* Sync login/logout between tabs:
  Since AuthContext lives inside each tab, if the user logs out from one,
  the others won’t "know" unless synced manually.
  */

  useEffect(() => {
    const syncLogout = (event) => {
      // Log out in all tabs
      if (event.key === "logout-event") {
        setAccessToken(null);
        setUser(null);
        clearTimeout(refreshTimeout);
        navigate("/login");
      }
    };

    window.addEventListener("storage", syncLogout);
    return () => {
      window.removeEventListener("storage", syncLogout);
    };
  }, []);

  useEffect(() => {
    const syncLogin = (event) => {
      // Sync login across tabs
      if (event.key === "login-event") {
        refreshAccessToken(); // Update token and user data
      }
    };

    window.addEventListener("storage", syncLogin);
    return () => window.removeEventListener("storage", syncLogin);
  }, []);

  /*
  Any component wrapped inside AuthProvider will have access to these values.
  isAuthenticated is true if there is a token, false otherwise.
  */

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        user,
        isAuthenticated: !!accessToken,
        login,
        logout,
        isLoading,
        isLoggingOut,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
