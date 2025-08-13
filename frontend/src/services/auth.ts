import api from './api';

export interface LoginCredentials {
  username: string; // Backend expects email as username
  password: string;
}

export interface RegisterData {
  email: string;
  full_name?: string;
  password: string;
  is_active?: boolean;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  token: AuthToken;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Backend expects form data for OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<AuthToken>('/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const token = response.data;
    
    // Store token
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token.access_token);
    }

    // Get user profile with the token
    const userResponse = await api.get<User>('/users/me');
    const user = userResponse.data;

    // Store user data
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }

    return { user, token };
  }

  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/register', data);
    return response.data;
  }

  async logout(): Promise<void> {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  getCurrentUser(): User | null {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      return userData ? JSON.parse(userData) : null;
    }
    return null;
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }
}

export const authService = new AuthService();
export default authService;