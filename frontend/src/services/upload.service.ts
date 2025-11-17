/**
 * File upload API service
 */
import api from './api'
import type { APIResponse } from '@/types'

export interface ImageUploadResponse {
  url: string
  filename: string
  size: number
}

export interface MultiImageUploadResponse {
  images: ImageUploadResponse[]
  total: number
}

export const uploadService = {
  /**
   * Upload single image
   */
  uploadImage: async (file: File): Promise<APIResponse<ImageUploadResponse>> => {
    const formData = new FormData()
    formData.append('file', file)

    return api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  /**
   * Upload multiple images
   */
  uploadImages: async (files: File[]): Promise<APIResponse<MultiImageUploadResponse>> => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    return api.post('/upload/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}
