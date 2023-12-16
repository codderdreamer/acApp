import axios from "axios";

let servicesBaseUrl: string | undefined = "/";

if (process.env.NODE_ENV || process.env.NODE_ENV === "development") {
  servicesBaseUrl = process.env.REACT_APP_DEVELOPMENT_API_BASE_URL;
} else {
  servicesBaseUrl = "http://34.77.149.60/api/v1";
}
const axiosInstance = axios.create({
  baseURL: servicesBaseUrl,
});

axiosInstance.interceptors.request.use(
  (config: any) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;
