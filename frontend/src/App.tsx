import { createBrowserRouter, RouterProvider } from "react-router";
import { Layout } from "./components/Layout";
import About from "./pages/About";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Plan from "./pages/Plan";
import Planner from "./pages/Planner";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/planner", element: <Planner /> },
      { path: "/plan/:id", element: <Plan /> },
      { path: "/about", element: <About /> },
      { path: "*", element: <NotFound /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
