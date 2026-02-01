import type { RouteObject } from "react-router-dom";
import NotFound from "../pages/NotFound";
import Home from "../pages/home/page";
import Interview from "../pages/interview/page";
import Analysis from "../pages/analysis/page";

const routes: RouteObject[] = [
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/interview",
    element: <Interview />,
  },
  {
    path: "/analysis",
    element: <Analysis />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
];

export default routes;
