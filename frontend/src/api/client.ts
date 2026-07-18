import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 60000, // 60 seconds — accounts for Render free tier cold start
});

export default apiClient;