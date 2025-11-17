/**
 * User API service
 */
import api from './api'
import type { APIResponse, User, UserRole } from '@/types'

export interface UserCreateData {
  username: string
  email: string
  password: string
  full_name?: string
  role: UserRole
}

export interface UserUpdateData {
  email?: string
  full_name?: string
  password?: string
  role?: UserRole
  is_active?: boolean
  bio?: string
  avatar_url?: string
}

export interface PasswordChangeData {
  old_password: string
  new_password: string
}

export const userService = {
  /**
   * Create user (admin only)
   */
  create: async (data: UserCreateData): Promise<APIResponse<User>> => {
    return api.post('/users', data)
  },

  /**
   * Get user by ID
   */
  getById: async (id: number): Promise<APIResponse<User>> => {
    return api.get(`/users/${id}`)
  },

  /**
   * Update user
   */
  update: async (id: number, data: UserUpdateData): Promise<APIResponse<User>> => {
    return api.put(`/users/${id}`, data)
  },

  /**
   * Change password
   */
  changePassword: async (data: PasswordChangeData): Promise<APIResponse<null>> => {
    return api.post('/users/change-password', data)
  },

  /**
   * Get users by role
   */
  getByRole: async (role: UserRole): Promise<APIResponse<User[]>> => {
    return api.get(`/users/by-role/${role}`)
  },
}
