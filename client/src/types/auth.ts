export interface User {
  id: number;
  email: string;
  username: string;
  role: 'admin' | 'faculty' | 'student';
  student_id?: string;
  department?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    user: User;
    tokens: {
      access: string;
      refresh: string;
    };
  };
  errors?: Record<string, string[]>;
}
