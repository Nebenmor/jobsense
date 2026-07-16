// src/api/client.ts
// Single axios instance used across all components.
// API URL comes from environment variable — no hardcoded URLs anywhere else.
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export default apiClient;