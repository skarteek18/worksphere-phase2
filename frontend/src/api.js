import axios from "axios";

const api = axios.create({
baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
headers: {
"Content-Type": "application/json",
},
});

// Add JWT token to requests when available
api.interceptors.request.use(
(config) => {
const token = localStorage.getItem("token");

if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}

return config;

},
(error) => Promise.reject(error)
);

export default api;

// Authentication APIs
export const loginUser = (data) =>
api.post("/auth/login", data);

export const registerUser = (data) =>
api.post("/auth/register", data);

// Employee APIs
export const getEmployees = () =>
api.get("/employees");

export const createEmployee = (data) =>
api.post("/employees", data);

// Attendance APIs
export const getAttendance = () =>
api.get("/attendance");

export const markAttendance = (data) =>
api.post("/attendance", data);

// Leave APIs
export const getLeaves = () =>
api.get("/leaves");

export const applyLeave = (data) =>
api.post("/leaves", data);

// Payroll APIs
export const getPayroll = () =>
api.get("/payroll");