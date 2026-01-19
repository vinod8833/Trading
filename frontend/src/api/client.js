import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      try {
        const refresh_token = localStorage.getItem("refresh_token");
        const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: refresh_token,
        });

        localStorage.setItem("access_token", response.data.access);
        api.defaults.headers.common["Authorization"] = `Bearer ${response.data.access}`;
        return api(original);
      } catch (err) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
