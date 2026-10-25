import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import Attendance from "./pages/Attendance";
import Leaves from "./pages/Leaves";
import Payroll from "./pages/Payroll";
import Admin from "./pages/Admin";

import "./index.css";

function App() {
return (
<BrowserRouter>
<Routes>
<Route path="/" element={<Navigate to="/login" replace />} />
<Route path="/login" element={<Login />} />
<Route path="/dashboard" element={<Dashboard />} />
<Route path="/employees" element={<Employees />} />
<Route path="/attendance" element={<Attendance />} />
<Route path="/leaves" element={<Leaves />} />
<Route path="/payroll" element={<Payroll />} />
<Route path="/admin" element={<Admin />} />
<Route
path="*"
element={<h2>404 - Page Not Found</h2>}
/>
</Routes>
</BrowserRouter>
);
}

export default App;