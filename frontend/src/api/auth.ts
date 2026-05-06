// src/api/auth.ts
import api from './index';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export const authApi = {
  login(data: LoginRequest) {
    return api.post<LoginResponse>('/auth/login', data);
  },
  register(data: RegisterRequest) {
    return api.post('/auth/register', data);
  },
  getMe() {
    return api.get('/auth/me');
  },
};