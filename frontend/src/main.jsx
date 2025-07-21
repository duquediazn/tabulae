//Entry Point: main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
// Component that enables routing similar to how URLs work in a traditional web app.
// It is the main router component provided by React Router.
import { BrowserRouter } from "react-router-dom";
// Imports the authentication context, which creates a "global state" to track if a user
// is logged in, who they are, their token, etc. Any part of the app can access this data without passing it down through props.
import { AuthProvider } from "./context/AuthProvider";

/*
The following block wraps the app with several providers that give it special capabilities:
* <React.StrictMode>: Strict mode that helps detect potential issues in development. It only affects the development environment.
* <BrowserRouter>: Enables routing functionality (<Route>, useNavigate, etc.) throughout the app.
* <AuthProvider>: Provides an authentication context available across the entire app. This allows, for example, accessing the
current user in any component using useAuth().
* <App />: The main component where routes are defined (<Routes>, <Route>, etc.).
*/

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
