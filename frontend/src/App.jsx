// Main App Component: App.jsx
import AppRouter from "./router/AppRouter";

/*
<AppRouter /> is rendered inside this container, which means that 
everything displayed in the app is controlled by the routes defined there.
*/

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <AppRouter />
    </div>
  );
}

export default App;
