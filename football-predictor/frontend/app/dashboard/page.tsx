'use client'

import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { useRouter } from 'next/navigation'
import { 
  Trophy, 
  Target, 
  TrendingUp, 
  Calendar,
  BarChart3,
  LogOut,
  User,
  Settings
} from 'lucide-react'
import { api } from '@/lib/api'
import { MatchCard } from '@/components/MatchCard'
import { PredictionCard } from '@/components/PredictionCard'
import { StatsCard } from '@/components/StatsCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  // Fetch user data
  const { data: userData, isLoading: userLoading } = useQuery(
    'user-data',
    () => api.auth.getMe().then(response => response.data),
    {
      onError: () => {
        localStorage.removeItem('token')
        router.push('/auth/login')
      }
    }
  )

  // Fetch user stats
  const { data: userStats, isLoading: statsLoading } = useQuery(
    'user-stats',
    () => api.users.getStats().then(response => response.data),
    {
      enabled: !!userData,
    }
  )

  // Fetch upcoming matches
  const { data: upcomingMatches, isLoading: matchesLoading } = useQuery(
    'upcoming-matches',
    () => api.matches.getUpcoming({ limit: 5 }).then(response => response.data),
    {
      refetchInterval: 60000,
    }
  )

  // Fetch user predictions
  const { data: userPredictions, isLoading: predictionsLoading } = useQuery(
    'user-predictions',
    () => api.predictions.getUserPredictions({ limit: 5 }).then(response => response.data),
    {
      enabled: !!userData,
    }
  )

  // Fetch leaderboard
  const { data: leaderboard, isLoading: leaderboardLoading } = useQuery(
    'leaderboard',
    () => api.predictions.getLeaderboard({ limit: 10 }).then(response => response.data)
  )

  useEffect(() => {
    if (userData) {
      setUser(userData)
    }
  }, [userData])

  const handleLogout = () => {
    localStorage.removeItem('token')
    toast.success('Logged out successfully')
    router.push('/')
  }

  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-5 h-5 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">
                  {user.full_name || user.username}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Welcome back, {user.full_name || user.username}!
          </h2>
          <p className="text-gray-600">
            Here's your prediction performance and upcoming matches.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            icon={Target}
            title="Total Predictions"
            value={userStats?.total_predictions || 0}
            change={userStats?.predictions_change ? `+${userStats.predictions_change}%` : undefined}
            changeType="positive"
          />
          <StatsCard
            icon={Trophy}
            title="Accuracy"
            value={userStats?.accuracy ? `${(userStats.accuracy * 100).toFixed(1)}%` : '0%'}
            change={userStats?.accuracy_change ? `+${(userStats.accuracy_change * 100).toFixed(1)}%` : undefined}
            changeType={userStats?.accuracy_change && userStats.accuracy_change > 0 ? 'positive' : 'negative'}
          />
          <StatsCard
            icon={TrendingUp}
            title="Win Streak"
            value={userStats?.current_streak || 0}
            change={userStats?.best_streak ? `Best: ${userStats.best_streak}` : undefined}
            changeType="positive"
          />
          <StatsCard
            icon={BarChart3}
            title="Rank"
            value={userStats?.rank ? `#${userStats.rank}` : 'Unranked'}
            change={userStats?.rank_change ? `${userStats.rank_change > 0 ? '+' : ''}${userStats.rank_change}` : undefined}
            changeType={userStats?.rank_change && userStats.rank_change < 0 ? 'positive' : 'negative'}
          />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upcoming Matches */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Upcoming Matches
                </h3>
              </div>
              <div className="card-body">
                {matchesLoading ? (
                  <LoadingSpinner />
                ) : upcomingMatches?.length > 0 ? (
                  <div className="space-y-4">
                    {upcomingMatches.map((match: any) => (
                      <MatchCard 
                        key={match.id} 
                        match={match} 
                        showPrediction={true}
                        onPredict={(matchId) => router.push(`/predict?match=${matchId}`)}
                      />
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
          </div>

          {/* Recent Predictions */}
          <div>
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Recent Predictions
                </h3>
              </div>
              <div className="card-body">
                {predictionsLoading ? (
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
                )}
              </div>
              <div className="card-footer">
                <a
                  href="/predictions"
                  className="btn btn-primary btn-sm w-full"
                >
                  View All Predictions
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard Section */}
        <div className="mt-8">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Trophy className="w-5 h-5 mr-2" />
                Top Predictors
              </h3>
            </div>
            <div className="card-body">
              {leaderboardLoading ? (
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
                          {user.accuracy ? (user.accuracy * 100).toFixed(1) : 0}%
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
              )}
            </div>
            <div className="card-footer">
              <a
                href="/leaderboard"
                className="btn btn-primary btn-sm w-full"
              >
                View Full Leaderboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}