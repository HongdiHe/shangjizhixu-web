/**
 * Authentication hooks
 */
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/store/auth.store'
import { ROUTES } from '@/config/constants'
import type { LoginRequest } from '@/types'

export const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, setUser, setTokens, clearAuth, setLoading } = useAuthStore()

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await authService.login(data)
      if (response.success && response.data) {
        const { access_token, refresh_token } = response.data
        setTokens(access_token, refresh_token)

        // Fetch user info
        const userResponse = await authService.getCurrentUser()
        if (userResponse.success && userResponse.data) {
          setUser(userResponse.data)
          navigate(ROUTES.DASHBOARD)
        }
      }
      return response
    },
  })

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSettled: () => {
      clearAuth()
      queryClient.clear()
      navigate(ROUTES.LOGIN)
    },
  })

  const login = async (data: LoginRequest) => {
    setLoading(true)
    try {
      await loginMutation.mutateAsync(data)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    logoutMutation.mutate()
  }

  return {
    user,
    isAuthenticated: !!user,
    isLoading: useAuthStore((state) => state.isLoading) || loginMutation.isPending,
    login,
    logout,
    loginError: loginMutation.error,
  }
}
