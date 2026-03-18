import { createBrowserRouter } from "react-router-dom";

import { App } from "./App";
import { BookmarksPage } from "./pages/BookmarksPage";
import { CompanyProfilePage } from "./pages/CompanyProfilePage";
import { FeedPage } from "./pages/FeedPage";
import { FundingRadarPage } from "./pages/FundingRadarPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SearchPage } from "./pages/SearchPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <FeedPage /> },
      { path: "funding-radar", element: <FundingRadarPage /> },
      { path: "search", element: <SearchPage /> },
      { path: "companies/:slug", element: <CompanyProfilePage /> },
      { path: "bookmarks", element: <BookmarksPage /> },
      { path: "profile", element: <ProfilePage /> },
    ],
  },
]);
