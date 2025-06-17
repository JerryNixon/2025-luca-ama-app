import apiClient from '@/lib/api';
import { User, LoginForm, ApiResponse } from '@/types';
import { setCookie, removeCookie } from 'js-cookie';

export const authService = {
  // Login user
  async login(credentials: LoginForm): Promise<{ user: User; token: string }> {
    const response = await apiClient.post<ApiResponse<{ user: User; token: string }>>('/auth/login/', credentials);
    const { user, token } = response.data.data;
    
    // Store token in cookie
    setCookie('access_token', token, { expires: 7 }); // 7 days
    
    return { user, token };
  },

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeCookie('access_token');
    }
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>('/auth/me/');
    return response.data.data;
  },

  // Refresh token
  async refreshToken(): Promise<string> {
    const response = await apiClient.post<ApiResponse<{ token: string }>>('/auth/refresh/');
    const { token } = response.data.data;
    setCookie('access_token', token, { expires: 7 });
    return token;
  },

  // Microsoft OAuth login (for tenant validation)
  async microsoftLogin(code: string): Promise<{ user: User; token: string }> {
    const response = await apiClient.post<ApiResponse<{ user: User; token: string }>>('/auth/microsoft/', { code });
    const { user, token } = response.data.data;
    
    setCookie('access_token', token, { expires: 7 });
    
    return { user, token };
  },
};
