/**
 * Authentication API service
 */
import api from './api'
import type { APIResponse, LoginRequest, TokenResponse, User } from '@/types'

export const authService = {
  /**
   * User login
   */
  login: async (data: LoginRequest): Promise<APIResponse<TokenResponse>> => {
    return api.post('/auth/login', data)
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<APIResponse<User>> => {
    return api.get('/auth/me')
  },

  /**
   * Logout
   */
  logout: async (): Promise<APIResponse<null>> => {
    return api.post('/auth/logout')
  },

  /**
   * Refresh token
   */
  refreshToken: async (refreshToken: string): Promise<APIResponse<TokenResponse>> => {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },
}
