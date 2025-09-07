'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import { useRouter } from 'next/navigation'
import { 
  Target,
  Filter,
  Search,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Clock
} from 'lucide-react'
import { api } from '@/lib/api'
import { PredictionCard } from '@/components/PredictionCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export default function PredictionsPage() {
  const router = useRouter()
  const [filters, setFilters] = useState({
    result: 'all',
    prediction_type: 'all',
    search: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  // Fetch user predictions
  const { data: predictions, isLoading: predictionsLoading, refetch } = useQuery(
    ['user-predictions', filters],
    () => api.predictions.getUserPredictions({
      limit: 50,
    }).then(response => response.data),
  )

  const handleFilterChange = (key: string, value: string) => {
    setFilters({
      ...filters,
      [key]: value,
    })
  }

  const clearFilters = () => {
    setFilters({
      result: 'all',
      prediction_type: 'all',
      search: '',
    })
  }

  const filteredPredictions = predictions?.filter((prediction: any) => {
    if (!filters.search) return true
    
    const searchTerm = filters.search.toLowerCase()
    return (
      prediction.match.home_team.name.toLowerCase().includes(searchTerm) ||
      prediction.match.away_team.name.toLowerCase().includes(searchTerm) ||
      prediction.match.league.name.toLowerCase().includes(searchTerm) ||
      prediction.prediction_type.toLowerCase().includes(searchTerm)
    )
  }) || []

  const resultOptions = [
    { value: 'all', label: 'All Results' },
    { value: 'PENDING', label: 'Pending' },
    { value: 'WON', label: 'Won' },
    { value: 'LOST', label: 'Lost' },
    { value: 'VOID', label: 'Void' },
  ]

  const predictionTypeOptions = [
    { value: 'all', label: 'All Types' },
    { value: 'WIN_DRAW_WIN', label: '1X2' },
    { value: 'OVER_UNDER', label: 'Over/Under' },
    { value: 'BOTH_TEAMS_SCORE', label: 'BTTS' },
    { value: 'CORRECT_SCORE', label: 'Correct Score' },
    { value: 'DOUBLE_CHANCE', label: 'Double Chance' },
  ]

  // Calculate stats
  const stats = {
    total: predictions?.length || 0,
    won: predictions?.filter((p: any) => p.result === 'WON').length || 0,
    lost: predictions?.filter((p: any) => p.result === 'LOST').length || 0,
    pending: predictions?.filter((p: any) => p.result === 'PENDING').length || 0,
    accuracy: predictions?.length > 0 
      ? (predictions.filter((p: any) => p.result === 'WON').length / 
         predictions.filter((p: any) => p.result !== 'PENDING').length) * 100 || 0
      : 0,
  }

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
            <h1 className="text-2xl font-bold text-gray-900">My Predictions</h1>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg">
                    <Target className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">Total Predictions</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.total}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">Won</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.won}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-lg">
                    <TrendingDown className="w-6 h-6 text-red-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">Lost</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.lost}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-lg">
                    <Clock className="w-6 h-6 text-yellow-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">Accuracy</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {stats.accuracy.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search predictions, matches, or teams..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="form-input pl-10"
                />
              </div>
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-secondary flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-white rounded-lg shadow border">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Result Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Result
                  </label>
                  <select
                    value={filters.result}
                    onChange={(e) => handleFilterChange('result', e.target.value)}
                    className="form-select"
                  >
                    {resultOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Prediction Type Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prediction Type
                  </label>
                  <select
                    value={filters.prediction_type}
                    onChange={(e) => handleFilterChange('prediction_type', e.target.value)}
                    className="form-select"
                  >
                    {predictionTypeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="btn btn-secondary btn-sm mr-2"
                >
                  Clear Filters
                </button>
                <button
                  onClick={() => setShowFilters(false)}
                  className="btn btn-primary btn-sm"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            Showing {filteredPredictions.length} prediction{filteredPredictions.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Predictions Grid */}
        {predictionsLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredPredictions.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPredictions.map((prediction: any) => (
              <PredictionCard
                key={prediction.id}
                prediction={prediction}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No predictions found</h3>
            <p className="text-gray-500 mb-4">
              {predictions?.length === 0 
                ? "You haven't made any predictions yet. Start by making your first prediction!"
                : "Try adjusting your filters or search terms"
              }
            </p>
            {predictions?.length === 0 && (
              <button
                onClick={() => router.push('/predict')}
                className="btn btn-primary"
              >
                Make First Prediction
              </button>
            )}
            {predictions?.length > 0 && (
              <button
                onClick={clearFilters}
                className="btn btn-primary"
              >
                Clear Filters
              </button>
            )}
          </div>
        )}

        {/* Load More Button (if needed) */}
        {filteredPredictions.length > 0 && (
          <div className="mt-8 text-center">
            <button
              onClick={() => refetch()}
              className="btn btn-secondary"
            >
              Refresh Predictions
            </button>
          </div>
        )}
      </div>
    </div>
  )
}