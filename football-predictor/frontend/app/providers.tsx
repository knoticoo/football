'use client'

import { QueryClient, QueryClientProvider } from 'react-query'
import { useState } from 'react'
import { logger } from '@/lib/logger'

export function Providers({ children }: { children: React.ReactNode }) {
  logger.info('Providers', 'Component rendered')
  
  const [queryClient] = useState(
    () => {
      logger.info('Providers', 'Creating new QueryClient instance')
      return new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            cacheTime: 5 * 60 * 1000, // 5 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
    }
  )

  logger.info('Providers', 'QueryClient provider ready')

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}