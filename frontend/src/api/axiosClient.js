import axios from "axios";

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("pc_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("pc_token");
      localStorage.removeItem("pc_stage");
    }
    return Promise.reject(err);
  }
);

export default axiosClient;
