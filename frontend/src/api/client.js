import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const setToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
};

export const setupUnauthorizedHandler = (onUnauthorized) => {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setToken(null);
        onUnauthorized();
      }

      return Promise.reject(error);
    }
  );
};

const savedToken = localStorage.getItem("token");
if (savedToken) {
  setToken(savedToken);
}

export default api;