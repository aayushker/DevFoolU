import { useAuth } from "@/lib/auth0-provider";
import { useEffect } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export const useApi = () => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth();

  const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Request interceptor to add Auth0 token
  api.interceptors.request.use(
    async (config) => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently();
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.error("Error getting access token:", error);
        }
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  return api;
};

// For non-hook usage, create a basic API instance
export const createAuthenticatedApi = async (
  getAccessTokenSilently: () => Promise<string>
) => {
  const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
      "Content-Type": "application/json",
    },
  });

  try {
    const token = await getAccessTokenSilently();
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
  } catch (error) {
    console.error("Error getting access token:", error);
  }

  return api;
};
