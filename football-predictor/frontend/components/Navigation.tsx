'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { 
  Home,
  Target,
  Calendar,
  Trophy,
  User,
  LogOut,
  Menu,
  X,
  BarChart3
} from 'lucide-react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

export function Navigation() {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<any>(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  
  console.log('🧭 Navigation component rendered')
  console.log('📍 Current pathname:', pathname)
  console.log('👤 User state:', user)
  console.log('📱 Menu open:', isMenuOpen)

  // Check if user is logged in
  useEffect(() => {
    console.log('🔄 Navigation useEffect triggered - checking user authentication')
    const token = localStorage.getItem('token')
    console.log('🔑 Token found in localStorage:', !!token)
    
    if (token) {
      console.log('🔍 Verifying token and fetching user data in Navigation...')
      api.auth.getMe()
        .then(response => {
          console.log('✅ User authenticated successfully in Navigation:', response.data)
          setUser(response.data)
        })
        .catch(error => {
          console.error('❌ Token verification failed in Navigation:', error)
          console.log('🗑️ Removing invalid token from Navigation')
          localStorage.removeItem('token')
          setUser(null)
        })
    } else {
      console.log('⚠️ No token found in Navigation - user not authenticated')
    }
  }, [])

  const handleLogout = () => {
    console.log('🚪 Logout initiated')
    console.log('🗑️ Removing token from localStorage')
    localStorage.removeItem('token')
    console.log('👤 Clearing user state')
    setUser(null)
    console.log('🎉 Showing logout success toast')
    toast.success('Logged out successfully')
    console.log('🔄 Redirecting to home page')
    router.push('/')
    console.log('📱 Closing mobile menu')
    setIsMenuOpen(false)
  }

  const navigationItems = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Matches', href: '/matches', icon: Calendar },
    { name: 'Predict', href: '/predict', icon: Target },
    { name: 'My Predictions', href: '/predictions', icon: BarChart3 },
    { name: 'Leaderboard', href: '/leaderboard', icon: Trophy },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname.startsWith(href)
  }

  // Don't show navigation on auth pages
  if (pathname.startsWith('/auth/')) {
    console.log('🚫 Not showing navigation on auth page:', pathname)
    return null
  }
  
  console.log('✅ Showing navigation for pathname:', pathname)

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button
              onClick={() => router.push('/')}
              className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
            >
              <Target className="w-8 h-8" />
              <span className="text-xl font-bold">Football Predictor</span>
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigationItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.name}
                  onClick={() => router.push(item.href)}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </button>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
                >
                  <User className="w-5 h-5" />
                  <span className="text-sm font-medium">
                    {user.full_name || user.username}
                  </span>
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-600 hover:text-gray-900"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm">Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.push('/auth/login')}
                  className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                >
                  Sign In
                </button>
                <button
                  onClick={() => router.push('/auth/register')}
                  className="btn btn-primary btn-sm"
                >
                  Sign Up
                </button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.name}
                    onClick={() => {
                      router.push(item.href)
                      setIsMenuOpen(false)
                    }}
                    className={`flex items-center space-x-2 w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </button>
                )
              })}
              
              {/* Mobile User Menu */}
              <div className="border-t border-gray-200 pt-2 mt-2">
                {user ? (
                  <div className="space-y-1">
                    <button
                      onClick={() => {
                        router.push('/dashboard')
                        setIsMenuOpen(false)
                      }}
                      className="flex items-center space-x-2 w-full px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                    >
                      <User className="w-4 h-4" />
                      <span>{user.full_name || user.username}</span>
                    </button>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 w-full px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <button
                      onClick={() => {
                        router.push('/auth/login')
                        setIsMenuOpen(false)
                      }}
                      className="flex items-center space-x-2 w-full px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                    >
                      <User className="w-4 h-4" />
                      <span>Sign In</span>
                    </button>
                    <button
                      onClick={() => {
                        router.push('/auth/register')
                        setIsMenuOpen(false)
                      }}
                      className="flex items-center space-x-2 w-full px-3 py-2 rounded-md text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50"
                    >
                      <span>Sign Up</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}