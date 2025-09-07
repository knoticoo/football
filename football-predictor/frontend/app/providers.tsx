'use client'

import { QueryClient, QueryClientProvider } from 'react-query'
import { useState } from 'react'
import { logger } from '@/lib/logger'

export function Providers({ children }: { children: React.ReactNode }) {
  
  const [queryClient] = useState(
    () => {
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


  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}