'use client'

import { QueryClient, QueryClientProvider } from 'react-query'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  console.log('🔧 Providers component rendered')
  
  const [queryClient] = useState(
    () => {
      console.log('🔄 Creating new QueryClient instance')
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

  console.log('✅ QueryClient provider ready')

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}