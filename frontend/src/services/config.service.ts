/**
 * System configuration API service
 */
import api from './api'
import type { APIResponse, SystemConfig } from '@/types'

export interface ConfigUpdateData {
  value: string | null
}

export const configService = {
  /**
   * Get all system configurations
   */
  getAll: async (): Promise<APIResponse<SystemConfig[]>> => {
    return api.get('/config')
  },

  /**
   * Get configuration by key
   */
  getByKey: async (key: string): Promise<APIResponse<SystemConfig>> => {
    return api.get(`/config/${key}`)
  },

  /**
   * Update configuration
   */
  update: async (key: string, data: ConfigUpdateData): Promise<APIResponse<SystemConfig>> => {
    return api.put(`/config/${key}`, data)
  },
}
