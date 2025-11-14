/**
 * Question API service
 * Updated: 2025-11-14 - Added regenerate rewrite functionality
 */
import api from './api'
import type {
  APIResponse,
  Question,
  QuestionSummary,
  PaginatedResponse,
  QuestionStatus,
  DashboardStats,
} from '@/types'

export interface QuestionCreateData {
  subject: string
  grade: string
  question_type: string
  source?: string
  tags?: string[]
  original_images: string[]
}

export interface QuestionUpdateData {
  subject?: string
  grade?: string
  question_type?: string
  source?: string
  tags?: string[]
}

export interface OCRContentUpdate {
  draft_original_question?: string
  draft_original_answer?: string
}

export interface OCRReviewSubmit {
  original_question: string
  original_answer: string
  review_comment?: string
  review_status: string
}

export interface RewritePairUpdate {
  draft_question?: string
  draft_answer?: string
  edit_comment?: string
}

export interface RewriteReviewSubmit {
  question: string
  answer: string
  review_comment?: string
  review_status: string
}

export interface AssignmentUpdate {
  ocr_editor_id?: number
  ocr_reviewer_id?: number
  rewrite_editor_id?: number
  rewrite_reviewer_id?: number
}

export const questionService = {
  /**
   * Create a new question
   */
  create: async (data: QuestionCreateData): Promise<APIResponse<Question>> => {
    return api.post('/questions', data)
  },

  /**
   * Get question by ID
   */
  getById: async (id: number): Promise<APIResponse<Question>> => {
    return api.get(`/questions/${id}`)
  },

  /**
   * Get paginated question list
   */
  getList: async (
    page = 1,
    pageSize = 20,
    statusFilter?: QuestionStatus
  ): Promise<APIResponse<PaginatedResponse<QuestionSummary>>> => {
    const params: any = { page, page_size: pageSize }
    if (statusFilter) {
      params.status_filter = statusFilter
    }
    return api.get('/questions', { params })
  },

  /**
   * Update question metadata
   */
  update: async (id: number, data: QuestionUpdateData): Promise<APIResponse<Question>> => {
    return api.put(`/questions/${id}`, data)
  },

  /**
   * Delete question (admin only)
   */
  delete: async (id: number): Promise<APIResponse<null>> => {
    return api.delete(`/questions/${id}`)
  },

  /**
   * Trigger OCR processing
   */
  triggerOCR: async (id: number): Promise<APIResponse<{ task_id: string; question_id: number }>> => {
    return api.post(`/questions/${id}/ocr/trigger`)
  },

  /**
   * Update OCR draft
   */
  updateOCRDraft: async (
    id: number,
    data: OCRContentUpdate
  ): Promise<APIResponse<Question>> => {
    return api.put(`/questions/${id}/ocr/draft`, data)
  },

  /**
   * Submit OCR edit
   */
  submitOCREdit: async (id: number): Promise<APIResponse<Question>> => {
    return api.post(`/questions/${id}/ocr/submit`)
  },

  /**
   * Submit OCR review
   */
  submitOCRReview: async (
    id: number,
    data: OCRReviewSubmit
  ): Promise<APIResponse<Question>> => {
    return api.post(`/questions/${id}/ocr/review`, data)
  },

  /**
   * Update rewrite draft
   */
  updateRewriteDraft: async (
    id: number,
    index: number,
    data: RewritePairUpdate
  ): Promise<APIResponse<Question>> => {
    return api.put(`/questions/${id}/rewrite/${index}`, data)
  },

  /**
   * Submit rewrite edit
   */
  submitRewriteEdit: async (id: number, index: number): Promise<APIResponse<Question>> => {
    return api.post(`/questions/${id}/rewrite/${index}/submit`)
  },

  /**
   * Submit rewrite review
   */
  submitRewriteReview: async (
    id: number,
    index: number,
    data: RewriteReviewSubmit
  ): Promise<APIResponse<Question>> => {
    return api.post(`/questions/${id}/rewrite/${index}/review`, data)
  },

  /**
   * Assign users to question
   */
  assignUsers: async (
    id: number,
    data: AssignmentUpdate
  ): Promise<APIResponse<Question>> => {
    return api.put(`/questions/${id}/assign`, data)
  },

  /**
   * Get my tasks
   */
  getMyTasks: async (
    page = 1,
    pageSize = 20
  ): Promise<APIResponse<PaginatedResponse<QuestionSummary>>> => {
    return api.get('/questions/my/tasks', {
      params: { page, page_size: pageSize },
    })
  },

  /**
   * Get dashboard statistics
   */
  getDashboardStats: async (): Promise<APIResponse<DashboardStats>> => {
    return api.get('/questions/stats/dashboard')
  },

  /**
   * Regenerate a single rewrite version
   */
  regenerateRewrite: async (id: number, index: number): Promise<APIResponse<{ task_id: string }>> => {
    return api.post(`/questions/${id}/rewrite/${index}/regenerate`)
  },
}
