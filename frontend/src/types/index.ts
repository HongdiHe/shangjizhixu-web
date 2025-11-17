/**
 * TypeScript type definitions
 */

export type UserRole =
  | 'admin'
  | 'question_submitter'
  | 'ocr_editor'
  | 'ocr_reviewer'
  | 'rewrite_editor'
  | 'rewrite_reviewer'

export type QuestionStatus =
  | 'NEW'
  | 'OCR_编辑中'
  | 'OCR_待审'
  | 'OCR_通过'
  | '改写_生成中'
  | '改写_编辑中'
  | '改写_复审中'
  | 'DONE'
  | '废弃'

export type ReviewStatus = 'pending' | 'approved' | 'changes_requested'

export type Subject = '数学' | '物理' | '化学' | '生物' | '语文' | '英语' | '历史' | '地理' | '政治'
export type Grade = '小学' | '初中' | '高中'
export type QuestionType = '选择题' | '判断题' | '填空题' | '简答题' | '论述题' | '计算题' | '证明题'
export type QuestionSource = 'HLE' | '教材' | '考试' | '练习' | '自定义'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: UserRole
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  last_login?: string
  bio?: string
  avatar_url?: string
}

export interface Question {
  id: number
  subject: Subject
  grade: Grade
  question_type: QuestionType
  source: QuestionSource
  tags: string[]
  original_images: string[]

  // OCR fields
  draft_original_question?: string
  draft_original_answer?: string
  original_question?: string
  original_answer?: string
  original_review_comment?: string
  original_review_status: ReviewStatus

  // Rewrite fields
  rewrite_prompt_version: number
  draft_rewrite_question_1?: string
  draft_rewrite_answer_1?: string
  draft_rewrite_question_2?: string
  draft_rewrite_answer_2?: string
  draft_rewrite_question_3?: string
  draft_rewrite_answer_3?: string
  draft_rewrite_question_4?: string
  draft_rewrite_answer_4?: string
  draft_rewrite_question_5?: string
  draft_rewrite_answer_5?: string

  rewrite_question_1?: string
  rewrite_answer_1?: string
  rewrite_question_2?: string
  rewrite_answer_2?: string
  rewrite_question_3?: string
  rewrite_answer_3?: string
  rewrite_question_4?: string
  rewrite_answer_4?: string
  rewrite_question_5?: string
  rewrite_answer_5?: string

  rewrite_edit_comment_1?: string
  rewrite_edit_comment_2?: string
  rewrite_edit_comment_3?: string
  rewrite_edit_comment_4?: string
  rewrite_edit_comment_5?: string

  rewrite_review_comment_1?: string
  rewrite_review_comment_2?: string
  rewrite_review_comment_3?: string
  rewrite_review_comment_4?: string
  rewrite_review_comment_5?: string

  rewrite_review_status_1: ReviewStatus
  rewrite_review_status_2: ReviewStatus
  rewrite_review_status_3: ReviewStatus
  rewrite_review_status_4: ReviewStatus
  rewrite_review_status_5: ReviewStatus

  // Assignments
  ocr_editor_id?: number
  ocr_reviewer_id?: number
  rewrite_editor_id?: number
  rewrite_reviewer_id?: number

  // Status and progress
  status: QuestionStatus
  ocr_progress: number
  rewrite_progress: number

  // Timestamps
  created_at: string
  updated_at: string
  ocr_completed_at?: string
  rewrite_completed_at?: string
}

export interface QuestionSummary {
  id: number
  subject: Subject
  grade: Grade
  question_type: QuestionType
  source: QuestionSource
  status: QuestionStatus
  ocr_progress: number
  rewrite_progress: number
  created_at: string
  updated_at: string
}

export interface APIResponse<T = any> {
  success: boolean
  message?: string
  data?: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface DashboardStats {
  total_questions: number
  completed_questions: number
  in_progress_questions: number
  my_tasks: number
}

export interface SystemConfig {
  id: number
  key: string
  value: string | null
  description: string | null
  is_secret: boolean
  updated_at: string
}
