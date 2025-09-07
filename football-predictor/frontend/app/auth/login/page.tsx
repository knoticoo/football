'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from 'react-query'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Eye, EyeOff, LogIn } from 'lucide-react'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  
  console.log('🔐 LoginPage component rendered')
  console.log('📝 Form data:', formData)
  console.log('👁️ Show password:', showPassword)

  const loginMutation = useMutation(
    (credentials: { username: string; password: string }) => {
      console.log('🔐 Attempting login with credentials:', { username: credentials.username, password: '***' })
      return api.auth.login(credentials)
    },
    {
      onSuccess: (response) => {
        console.log('✅ Login successful:', response.data)
        const { access_token, user } = response.data
        console.log('💾 Storing token in localStorage')
        localStorage.setItem('token', access_token)
        console.log('🎉 Showing success toast')
        toast.success(`Welcome back, ${user.full_name || user.username}!`)
        console.log('🔄 Redirecting to dashboard')
        router.push('/dashboard')
      },
      onError: (error: any) => {
        console.error('❌ Login failed:', error)
        console.error('❌ Error response:', error.response?.data)
        const message = error.response?.data?.detail || 'Login failed'
        console.log('🚨 Showing error toast:', message)
        toast.error(message)
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('📝 Form submitted with data:', { username: formData.username, password: '***' })
    
    if (!formData.username || !formData.password) {
      console.log('❌ Form validation failed - missing fields')
      toast.error('Please fill in all fields')
      return
    }
    
    console.log('✅ Form validation passed - submitting login request')
    loginMutation.mutate(formData)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('📝 Input changed:', e.target.name, '=', e.target.value)
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
            <LogIn className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <a
              href="/auth/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              create a new account
            </a>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="form-input rounded-t-md"
                placeholder="Username"
                value={formData.username}
                onChange={handleInputChange}
                disabled={loginMutation.isLoading}
              />
            </div>
            <div className="relative">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                className="form-input rounded-b-md pr-10"
                placeholder="Password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loginMutation.isLoading}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <a href="#" className="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loginMutation.isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loginMutation.isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}