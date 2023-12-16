import { Navigate, Route, Routes } from "react-router-dom";

import AccountLayout from "../Layouts/AccountLayout";
import Login from "../Pages/Login";

import DashboardLayout from "../Layouts/DashboardLayout";
import Dashboard from "../Pages/Dashboard";
import Hardware from "../Pages/Hardware";
import QuickSetup from "../Pages/QuickSetup";
import Software from "../Pages/Software";
import DeviceStatus from "../Pages/DeviceStatus";
import Uploads from "../Pages/Uploads";
import ErrorLogs from "../Pages/ErrorLogs";
import Profile from "../Pages/Profile";

import AuthProvider from "../Providers/AuthProvider";
import Charging from "../Pages/Charging";
import LoginProvider from "../Providers/LoginProvider";

const RouteList = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      <Route path="" element={<LoginProvider />}>
        <Route path="account" element={<AccountLayout />}>
          <Route path="login" element={<Login />} />
        </Route>
      </Route>

      <Route path="" element={<AuthProvider />}>
        <Route path="admin" element={<DashboardLayout />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="quick-setup" element={<QuickSetup />} />
          <Route path="software" element={<Software />} />
          <Route path="status" element={<DeviceStatus />} />
          <Route path="profile" element={<Profile />} />
          <Route path="uploads" element={<Uploads />} />
          <Route path="charging" element={<Charging />} />
          <Route path="hardware" element={<Hardware />} />
          <Route path="error-logs" element={<ErrorLogs />} />
        </Route>
      </Route>

      {/* <Route path="401" element={<UnAuthorized />} />
      <Route path="404" element={<Notfound />} />
      <Route path="500" element={<ServerError />} /> */}
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default RouteList;
