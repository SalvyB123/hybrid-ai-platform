// frontend/src/main.tsx (example)
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ProtectedRoute from "@/routes/ProtectedRoute";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";

const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      { path: "/dashboard", element: <Dashboard /> },
      // add other protected routes here
    ],
  },
]);

createRoot(document.getElementById("root")!).render(<RouterProvider router={router} />);