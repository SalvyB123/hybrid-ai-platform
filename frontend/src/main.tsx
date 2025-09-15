// frontend/src/main.tsx
import "./styles/globals.css";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      // index route so "/" shows something instead of a blank outlet
      { index: true, element: <Dashboard /> },
      { path: "dashboard", element: <Dashboard /> } // relative path = truly nested
    ],
  },
]);

createRoot(document.getElementById("root")!).render(<RouterProvider router={router} />);