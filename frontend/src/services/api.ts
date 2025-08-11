import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
}

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/login', formData);
    return response.data;
  },

  register: async (data: RegisterData) => {
    const response = await api.post('/register', data);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};
