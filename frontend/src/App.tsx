import { Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import UserExplorer from "./pages/UserExplorer";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/"              element={<Dashboard />} />
        <Route path="/users"         element={<UserExplorer />} />
        <Route path="/alerts"        element={<Alerts />} />
        <Route path="/analytics"     element={<Analytics />} />
      </Routes>
    </Layout>
  );
}
