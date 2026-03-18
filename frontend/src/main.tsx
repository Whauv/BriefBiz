import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";

import { router } from "./router";
import { AppStoreProvider } from "./store/AppStore";
import "./index.css";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppStoreProvider>
        <RouterProvider router={router} />
      </AppStoreProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
