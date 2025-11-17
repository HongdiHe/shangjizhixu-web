/**
 * Application constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const TOKEN_KEY = 'auth_token'
export const REFRESH_TOKEN_KEY = 'refresh_token'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  QUESTIONS: '/questions',
  QUESTION_DETAIL: '/questions/:id',
  QUESTION_NEW: '/questions/new',
  QUESTION_OCR_EDIT: '/questions/:id/ocr/edit',
  QUESTION_OCR_REVIEW: '/questions/:id/ocr/review',
  QUESTION_REWRITE_EDIT: '/questions/:id/rewrite/edit',
  QUESTION_REWRITE_REVIEW: '/questions/:id/rewrite/review',
  MY_TASKS: '/my-tasks',
  SYSTEM_CONFIG: '/config',
  USERS: '/users',
  PROFILE: '/profile',
} as const

export const USER_ROLES = {
  ADMIN: 'admin',
  OCR_EDITOR: 'ocr_editor',
  OCR_REVIEWER: 'ocr_reviewer',
  REWRITE_EDITOR: 'rewrite_editor',
  REWRITE_REVIEWER: 'rewrite_reviewer',
} as const

export const QUESTION_STATUS = {
  NEW: 'NEW',
  OCR_EDITING: 'OCR_编辑中',
  OCR_REVIEWING: 'OCR_待审',
  OCR_APPROVED: 'OCR_通过',
  REWRITE_GENERATING: '改写_生成中',
  REWRITE_EDITING: '改写_编辑中',
  REWRITE_REVIEWING: '改写_复审中',
  DONE: 'DONE',
  ARCHIVED: '废弃',
} as const

export const REVIEW_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  CHANGES_REQUESTED: 'changes_requested',
} as const
