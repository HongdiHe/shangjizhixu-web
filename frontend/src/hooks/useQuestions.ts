/**
 * Question-related hooks
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { questionService, type QuestionCreateData } from '@/services/question.service'
import type { QuestionStatus } from '@/types'

export const useQuestions = (page = 1, pageSize = 20, statusFilter?: QuestionStatus) => {
  return useQuery({
    queryKey: ['questions', page, pageSize, statusFilter],
    queryFn: () => questionService.getList(page, pageSize, statusFilter),
  })
}

export const useQuestion = (id: number) => {
  return useQuery({
    queryKey: ['question', id],
    queryFn: () => questionService.getById(id),
    enabled: !!id,
  })
}

export const useCreateQuestion = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: QuestionCreateData) => questionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useUpdateQuestion = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      questionService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useDeleteQuestion = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => questionService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useTriggerOCR = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => questionService.triggerOCR(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['question', id] })
    },
  })
}

export const useUpdateOCRDraft = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      questionService.updateOCRDraft(id, data),
    onSuccess: (response, variables) => {
      // 使用乐观更新：直接更新缓存中的 draft 字段，不重新获取
      // 这样可以避免触发 question 对象引用变化，保持 Markdown 框不变
      queryClient.setQueryData(['question', variables.id], (old: any) => {
        if (!old) return old
        return {
          ...old,
          data: {
            ...old.data,
            draft_original_question: variables.data.draft_original_question ?? old.data.draft_original_question,
            draft_original_answer: variables.data.draft_original_answer ?? old.data.draft_original_answer,
          }
        }
      })
    },
  })
}

export const useSubmitOCREdit = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => questionService.submitOCREdit(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['question', id] })
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useSubmitOCRReview = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      questionService.submitOCRReview(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useUpdateRewriteDraft = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, index, data }: { id: number; index: number; data: any }) =>
      questionService.updateRewriteDraft(id, index, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
    },
  })
}

export const useSubmitRewriteEdit = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, index }: { id: number; index: number }) =>
      questionService.submitRewriteEdit(id, index),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
    },
  })
}

export const useSubmitAllRewriteEdits = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      questionService.submitAllRewriteEdits(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['question', id] })
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useSubmitRewriteReview = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, index, data }: { id: number; index: number; data: any }) =>
      questionService.submitRewriteReview(id, index, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['questions'] })
    },
  })
}

export const useMyTasks = (page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['myTasks', page, pageSize],
    queryFn: () => questionService.getMyTasks(page, pageSize),
  })
}

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => questionService.getDashboardStats(),
  })
}

export const useRegenerateRewrite = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, index }: { id: number; index: number }) =>
      questionService.regenerateRewrite(id, index),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['question', variables.id] })
    },
  })
}
