'use client'

import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { 
  Trophy, 
  Target, 
  TrendingUp, 
  Users, 
  Calendar,
  BarChart3,
  Zap,
  Star
} from 'lucide-react'
import { api } from '@/lib/api'
import { logger } from '@/lib/logger'
import { MatchCard } from '@/components/MatchCard'
import { PredictionCard } from '@/components/PredictionCard'
import { StatsCard } from '@/components/StatsCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export default function HomePage() {
  const [user, setUser] = useState(null)
  
  logger.info('HomePage', 'Component rendered')
  logger.debug('HomePage', 'Current user state', { user })

  // Fetch upcoming matches
  const { data: upcomingMatches, isLoading: matchesLoading, error: matchesError } = useQuery(
    'upcoming-matches',
    () => {
      logger.info('HomePage', 'Fetching upcoming matches...')
      return api.matches.getUpcoming({ limit: 6 }).then(response => {
        logger.info('HomePage', 'Upcoming matches fetched successfully', { count: response.data?.length || 0 })
        return response.data
      }).catch(error => {
        logger.error('HomePage', 'Failed to fetch upcoming matches', error)
        throw error
      })
    },
    {
      refetchInterval: 60000, // Refetch every minute
      onError: (error) => {
        logger.error('HomePage', 'Upcoming matches query error', error)
      }
    }
  )

  // Fetch user predictions
  const { data: userPredictions, isLoading: predictionsLoading, error: predictionsError } = useQuery(
    'user-predictions',
    () => {
      logger.info('HomePage', 'Fetching user predictions...')
      return api.predictions.getUserPredictions({ limit: 5 }).then(response => {
        logger.info('HomePage', 'User predictions fetched successfully', { count: response.data?.length || 0 })
        return response.data
      }).catch(error => {
        logger.error('HomePage', 'Failed to fetch user predictions', error)
        throw error
      })
    },
    {
      enabled: !!user,
      onError: (error) => {
        logger.error('HomePage', 'User predictions query error', error)
      }
    }
  )

  // Fetch user stats
  const { data: userStats, isLoading: statsLoading, error: statsError } = useQuery(
    'user-stats',
    () => {
      logger.info('HomePage', 'Fetching user stats...')
      return api.users.getStats().then(response => {
        logger.info('HomePage', 'User stats fetched successfully', response.data)
        return response.data
      }).catch(error => {
        logger.error('HomePage', 'Failed to fetch user stats', error)
        throw error
      })
    },
    {
      enabled: !!user,
      onError: (error) => {
        logger.error('HomePage', 'User stats query error', error)
      }
    }
  )

  // Fetch leaderboard
  const { data: leaderboard, isLoading: leaderboardLoading, error: leaderboardError } = useQuery(
    'leaderboard',
    () => {
      logger.info('HomePage', 'Fetching leaderboard...')
      return api.predictions.getLeaderboard({ limit: 5 }).then(response => {
        logger.info('HomePage', 'Leaderboard fetched successfully', { count: response.data?.length || 0 })
        return response.data
      }).catch(error => {
        logger.error('HomePage', 'Failed to fetch leaderboard', error)
        throw error
      })
    },
    {
      onError: (error) => {
        logger.error('HomePage', 'Leaderboard query error', error)
      }
    }
  )

  useEffect(() => {
    logger.info('HomePage', 'useEffect triggered - checking user authentication')
    // Check if user is logged in
    const token = localStorage.getItem('token')
    logger.debug('HomePage', 'Token found in localStorage', { hasToken: !!token })
    
    if (token) {
      logger.info('HomePage', 'Verifying token and fetching user data...')
      // Verify token and get user data
      api.auth.getMe().then(response => {
        logger.info('HomePage', 'User authenticated successfully', response.data)
        setUser(response.data)
      }).catch(error => {
        logger.error('HomePage', 'Token verification failed', error)
        logger.warn('HomePage', 'Removing invalid token')
        localStorage.removeItem('token')
        setUser(null)
      })
    } else {
      logger.warn('HomePage', 'No token found - user not authenticated')
    }
  }, [])

  const features = [
    {
      icon: Target,
      title: 'Accurate Predictions',
      description: 'Make predictions with confidence using our advanced algorithms and statistics.',
    },
    {
      icon: TrendingUp,
      title: 'Track Performance',
      description: 'Monitor your prediction accuracy and improve over time with detailed analytics.',
    },
    {
      icon: Users,
      title: 'Compete with Others',
      description: 'Join the leaderboard and compete with other football prediction enthusiasts.',
    },
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'Get live match updates and instant notifications for your predictions.',
    },
  ]

  logger.debug('HomePage', 'Loading states', {
    matchesLoading,
    predictionsLoading,
    statsLoading,
    leaderboardLoading
  })
  
  logger.debug('HomePage', 'Data states', {
    upcomingMatches: upcomingMatches?.length || 0,
    userPredictions: userPredictions?.length || 0,
    userStats: !!userStats,
    leaderboard: leaderboard?.length || 0
  })
  
  logger.debug('HomePage', 'Error states', {
    matchesError: !!matchesError,
    predictionsError: !!predictionsError,
    statsError: !!statsError,
    leaderboardError: !!leaderboardError
  })

  if (matchesLoading) {
    logger.info('HomePage', 'Showing loading spinner for matches')
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Football Predictor
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              Make accurate predictions, track your performance, and compete with others
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <>
                  <a
                    href="/predict"
                    className="btn btn-lg bg-white text-primary-600 hover:bg-gray-100"
                  >
                    Make Prediction
                  </a>
                  <a
                    href="/dashboard"
                    className="btn btn-lg border-2 border-white text-white hover:bg-white hover:text-primary-600"
                  >
                    View Dashboard
                  </a>
                </>
              ) : (
                <>
                  <a
                    href="/auth/login"
                    className="btn btn-lg bg-white text-primary-600 hover:bg-gray-100"
                  >
                    Get Started
                  </a>
                  <a
                    href="/auth/register"
                    className="btn btn-lg border-2 border-white text-white hover:bg-white hover:text-primary-600"
                  >
                    Sign Up
                  </a>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <StatsCard
            icon={Trophy}
            title="Total Predictions"
            value="12,450"
            change="+15%"
            changeType="positive"
          />
          <StatsCard
            icon={Target}
            title="Average Accuracy"
            value="68.5%"
            change="+2.3%"
            changeType="positive"
          />
          <StatsCard
            icon={Users}
            title="Active Users"
            value="1,250"
            change="+8%"
            changeType="positive"
          />
          <StatsCard
            icon={Calendar}
            title="Matches Today"
            value="24"
            change="+3"
            changeType="positive"
          />
        </div>

        {/* Features Section */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose Football Predictor?
          </h2>
          <p className="text-lg text-gray-600 mb-12">
            Our platform combines advanced analytics with user-friendly features
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                  <feature.icon className="w-8 h-8 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Matches */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Upcoming Matches
              </h3>
            </div>
            <div className="card-body">
              {upcomingMatches?.length > 0 ? (
                <div className="space-y-4">
                  {upcomingMatches.slice(0, 3).map((match: any) => (
                    <MatchCard key={match.id} match={match} />
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">
                  No upcoming matches available
                </p>
              )}
            </div>
            <div className="card-footer">
              <a
                href="/matches"
                className="btn btn-primary btn-sm w-full"
              >
                View All Matches
              </a>
            </div>
          </div>

          {/* User Predictions or Leaderboard */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                {user ? (
                  <>
                    <Target className="w-5 h-5 mr-2" />
                    Your Recent Predictions
                  </>
                ) : (
                  <>
                    <Trophy className="w-5 h-5 mr-2" />
                    Top Predictors
                  </>
                )}
              </h3>
            </div>
            <div className="card-body">
              {user ? (
                predictionsLoading ? (
                  <LoadingSpinner />
                ) : userPredictions?.length > 0 ? (
                  <div className="space-y-4">
                    {userPredictions.map((prediction: any) => (
                      <PredictionCard key={prediction.id} prediction={prediction} />
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No predictions yet. Make your first prediction!
                  </p>
                )
              ) : (
                leaderboardLoading ? (
                  <LoadingSpinner />
                ) : leaderboard?.length > 0 ? (
                  <div className="space-y-4">
                    {leaderboard.map((user: any, index: number) => (
                      <div key={user.id} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="flex items-center justify-center w-8 h-8 bg-primary-100 rounded-full mr-3">
                            <span className="text-sm font-semibold text-primary-600">
                              {index + 1}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {user.full_name || user.username}
                            </p>
                            <p className="text-sm text-gray-500">
                              {user.total_predictions} predictions
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">
                            {user.accuracy?.toFixed(1)}%
                          </p>
                          <p className="text-sm text-gray-500">accuracy</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No leaderboard data available
                  </p>
                )
              )}
            </div>
            <div className="card-footer">
              {user ? (
                <a
                  href="/predictions"
                  className="btn btn-primary btn-sm w-full"
                >
                  View All Predictions
                </a>
              ) : (
                <a
                  href="/leaderboard"
                  className="btn btn-primary btn-sm w-full"
                >
                  View Full Leaderboard
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}