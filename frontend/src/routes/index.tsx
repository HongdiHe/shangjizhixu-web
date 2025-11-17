/**
 * Application routes
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth.store'
import MainLayout from '@/components/layout/MainLayout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import QuestionListPage from '@/pages/QuestionListPage'
import QuestionDetailPage from '@/pages/QuestionDetailPage'
import QuestionNewPage from '@/pages/QuestionNewPage'
import QuestionOCREditPage from '@/pages/QuestionOCREditPage'
import QuestionOCRReviewPage from '@/pages/QuestionOCRReviewPage'
import QuestionRewriteEditPage from '@/pages/QuestionRewriteEditPage'
import QuestionRewriteReviewPage from '@/pages/QuestionRewriteReviewPage'
import MyTasksPage from '@/pages/MyTasksPage'
import SystemConfigPage from '@/pages/SystemConfigPage'
import { ROUTES } from '@/config/constants'

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  return <>{children}</>
}

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.QUESTIONS} element={<QuestionListPage />} />
        <Route path={ROUTES.QUESTION_DETAIL} element={<QuestionDetailPage />} />
        <Route path={ROUTES.QUESTION_NEW} element={<QuestionNewPage />} />
        <Route path={ROUTES.QUESTION_OCR_EDIT} element={<QuestionOCREditPage />} />
        <Route path={ROUTES.QUESTION_OCR_REVIEW} element={<QuestionOCRReviewPage />} />
        <Route path={ROUTES.QUESTION_REWRITE_EDIT} element={<QuestionRewriteEditPage />} />
        <Route path={ROUTES.QUESTION_REWRITE_REVIEW} element={<QuestionRewriteReviewPage />} />
        <Route path={ROUTES.MY_TASKS} element={<MyTasksPage />} />
        <Route path={ROUTES.SYSTEM_CONFIG} element={<SystemConfigPage />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    </Routes>
  )
}

export default AppRoutes
