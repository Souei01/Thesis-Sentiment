import axiosInstance from '@/lib/axios';
import Cookies from 'js-cookie';
import { LoginCredentials, AuthResponse, User } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await axiosInstance.post<AuthResponse>('/auth/login/', credentials);
      
      if (response.data.success && response.data.data) {
        // Store tokens and user data
        Cookies.set('access_token', response.data.data.tokens.access, { expires: 1 / 24 }); // 1 hour
        Cookies.set('refresh_token', response.data.data.tokens.refresh, { expires: 7 }); // 7 days
        Cookies.set('user', JSON.stringify(response.data.data.user), { expires: 7 });
      }
      
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data;
      }
      return {
        success: false,
        message: 'Network error. Please try again.',
        errors: {}
      };
    }
  },

  async logout(): Promise<void> {
    const refreshToken = Cookies.get('refresh_token');
    
    // Clear cookies first
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    Cookies.remove('user');
    
    // Try to blacklist token on server (optional - don't await)
    if (refreshToken) {
      try {
        await axiosInstance.post('/auth/logout/', { refresh_token: refreshToken });
      } catch (error) {
        // Ignore errors - user is already logged out locally
        console.log('Server logout failed, but local logout successful');
      }
    }
  },

  getCurrentUser(): User | null {
    const userStr = Cookies.get('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },

  isAuthenticated(): boolean {
    return !!Cookies.get('access_token');
  },
};
