import api from './api';
import type { User } from './auth';

export interface UserUpdateData {
  full_name?: string;
  email?: string;
}

export interface PasswordChangeData {
  password: string;
}

class UserService {
  async updateProfile(data: UserUpdateData): Promise<User> {
    const response = await api.put<User>('/users/me', data);
    
    // Update stored user data
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    
    return response.data;
  }

  async changePassword(data: PasswordChangeData): Promise<User> {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  }

  async getCurrentProfile(): Promise<User> {
    const response = await api.get<User>('/users/me');
    
    // Update stored user data
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    
    return response.data;
  }
}

export const userService = new UserService();
export default userService;