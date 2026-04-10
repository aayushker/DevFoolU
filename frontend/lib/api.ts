import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor to add Auth0 token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth0_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth0_token");
        localStorage.removeItem("auth0_user");
        // Don't auto-redirect, let the app handle it
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  getProfile: () => api.get("/auth/me"),

  verifyToken: () => api.get("/auth/verify"),

  getConfig: () => api.get("/auth/config"),
};

// Projects API
export const projectsAPI = {
  getAll: () => api.get("/projects"),

  getById: (id: string) => api.get(`/projects/${id}`),

  create: (projectData: { name: string; description?: string }) =>
    api.post("/projects", projectData),

  update: (id: string, projectData: { name?: string; description?: string }) =>
    api.put(`/projects/${id}`, projectData),

  delete: (id: string) => api.delete(`/projects/${id}`),
};

// Tasks API
export const tasksAPI = {
  getAll: (projectId: string) => api.get(`/projects/${projectId}/tasks`),

  getById: (projectId: string, taskId: string) =>
    api.get(`/projects/${projectId}/tasks/${taskId}`),

  create: (
    projectId: string,
    taskData: {
      title: string;
      description?: string;
      status?: string;
      priority?: string;
      due_date?: string;
    }
  ) => api.post(`/projects/${projectId}/tasks`, taskData),

  update: (projectId: string, taskId: string, taskData: any) =>
    api.put(`/projects/${projectId}/tasks/${taskId}`, taskData),

  delete: (projectId: string, taskId: string) =>
    api.delete(`/projects/${projectId}/tasks/${taskId}`),
};

// Similarity API
export const similarityAPI = {
  searchByUrl: (url: string) => api.post("/similarity/search-by-url", { url }),

  searchByText: (text: string) =>
    api.post("/similarity/search-by-text", { text }),
};

export default api;
