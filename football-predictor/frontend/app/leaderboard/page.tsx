'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import { useRouter } from 'next/navigation'
import { 
  Trophy,
  Medal,
  Award,
  ArrowLeft,
  TrendingUp,
  Target,
  Users
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export default function LeaderboardPage() {
  const router = useRouter()
  const [timeframe, setTimeframe] = useState('all')

  // Fetch leaderboard
  const { data: leaderboard, isLoading: leaderboardLoading, refetch } = useQuery(
    ['leaderboard', timeframe],
    () => api.predictions.getLeaderboard({
      limit: 50,
    }).then(response => response.data),
    {
      refetchInterval: 300000, // Refetch every 5 minutes
    }
  )

  // Fetch current user stats for comparison
  const { data: userStats } = useQuery(
    'user-stats',
    () => api.users.getStats().then(response => response.data),
  )

  const timeframeOptions = [
    { value: 'all', label: 'All Time' },
    { value: 'month', label: 'This Month' },
    { value: 'week', label: 'This Week' },
  ]

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-6 h-6 text-yellow-500" />
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />
      case 3:
        return <Award className="w-6 h-6 text-amber-600" />
      default:
        return (
          <div className="flex items-center justify-center w-6 h-6 bg-gray-100 rounded-full">
            <span className="text-xs font-semibold text-gray-600">{rank}</span>
          </div>
        )
    }
  }

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white'
      case 2:
        return 'bg-gradient-to-r from-gray-300 to-gray-500 text-white'
      case 3:
        return 'bg-gradient-to-r from-amber-500 to-amber-700 text-white'
      default:
        return 'bg-white'
    }
  }

  const getCurrentUserRank = () => {
    if (!userStats || !leaderboard) return null
    
    return leaderboard.find((user: any) => user.id === userStats.user_id)
  }

  const currentUserRank = getCurrentUserRank()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-6">
            <button
              onClick={() => router.back()}
              className="flex items-center text-gray-500 hover:text-gray-700 mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              Back
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Leaderboard</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Timeframe Filter */}
        <div className="mb-8">
          <div className="flex justify-center">
            <div className="bg-white rounded-lg shadow-sm border p-1">
              {timeframeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setTimeframe(option.value)}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    timeframe === option.value
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Current User Rank (if logged in) */}
        {currentUserRank && (
          <div className="mb-8">
            <div className="card border-primary-200 bg-primary-50">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full">
                      {getRankIcon(currentUserRank.rank)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Your Rank: #{currentUserRank.rank}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {currentUserRank.total_predictions} predictions • {currentUserRank.accuracy ? (currentUserRank.accuracy * 100).toFixed(1) : 0}% accuracy
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-600">
                      {currentUserRank.accuracy ? (currentUserRank.accuracy * 100).toFixed(1) : 0}%
                    </div>
                    <div className="text-sm text-gray-500">accuracy</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Leaderboard */}
        {leaderboardLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : leaderboard?.length > 0 ? (
          <div className="space-y-4">
            {/* Top 3 Podium */}
            {leaderboard.slice(0, 3).map((user: any, index: number) => (
              <div
                key={user.id}
                className={`card ${getRankColor(user.rank)} transition-all duration-200 hover:shadow-lg`}
              >
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-12 h-12 rounded-full">
                        {getRankIcon(user.rank)}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">
                          {user.full_name || user.username}
                        </h3>
                        <p className="text-sm opacity-90">
                          {user.total_predictions} predictions
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">
                        {user.accuracy ? (user.accuracy * 100).toFixed(1) : 0}%
                      </div>
                      <div className="text-sm opacity-90">accuracy</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Rest of the leaderboard */}
            {leaderboard.slice(3).map((user: any) => (
              <div
                key={user.id}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-10 h-10 bg-gray-100 rounded-full">
                        <span className="text-sm font-semibold text-gray-600">
                          {user.rank}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {user.full_name || user.username}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {user.total_predictions} predictions
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-gray-900">
                        {user.accuracy ? (user.accuracy * 100).toFixed(1) : 0}%
                      </div>
                      <div className="text-sm text-gray-500">accuracy</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Trophy className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No leaderboard data</h3>
            <p className="text-gray-500 mb-4">
              There's not enough data to generate a leaderboard yet
            </p>
            <button
              onClick={() => refetch()}
              className="btn btn-primary"
            >
              Refresh
            </button>
          </div>
        )}

        {/* Stats Summary */}
        {leaderboard && leaderboard.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="card-body text-center">
                <Users className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{leaderboard.length}</div>
                <div className="text-sm text-gray-600">Total Players</div>
              </div>
            </div>
            <div className="card">
              <div className="card-body text-center">
                <Target className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {leaderboard.reduce((sum: number, user: any) => sum + user.total_predictions, 0)}
                </div>
                <div className="text-sm text-gray-600">Total Predictions</div>
              </div>
            </div>
            <div className="card">
              <div className="card-body text-center">
                <TrendingUp className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">
                  {leaderboard.length > 0 
                    ? (leaderboard.reduce((sum: number, user: any) => sum + (user.accuracy || 0), 0) / leaderboard.length * 100).toFixed(1)
                    : 0}%
                </div>
                <div className="text-sm text-gray-600">Average Accuracy</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}