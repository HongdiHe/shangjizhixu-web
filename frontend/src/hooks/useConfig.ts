/**
 * System configuration hooks
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { configService, type ConfigUpdateData } from '@/services/config.service'

export const useConfigs = () => {
  return useQuery({
    queryKey: ['configs'],
    queryFn: () => configService.getAll(),
  })
}

export const useConfig = (key: string) => {
  return useQuery({
    queryKey: ['config', key],
    queryFn: () => configService.getByKey(key),
    enabled: !!key,
  })
}

export const useUpdateConfig = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ key, data }: { key: string; data: ConfigUpdateData }) =>
      configService.update(key, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configs'] })
    },
  })
}
