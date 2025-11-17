// Allows easy access to the authentication context (AuthContext) from any component in the app
import { useContext } from "react"; // Imports the useContext hook from React.
import { AuthContext } from "./AuthProvider"; // Imports the AuthContext, created in AuthProvider.jsx

export function useAuth() {
  return useContext(AuthContext);
}

/*
This function returns the current value of the AuthContext.

Why is this approach useful?
- Avoids repeating useContext(AuthContext) in every component.
- Allows centralizing additional logic (e.g., transforming data before returning it).
- Makes the code cleaner and easier to maintain.
*/
