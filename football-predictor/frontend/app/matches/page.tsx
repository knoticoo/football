'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import { useRouter } from 'next/navigation'
import { 
  Calendar,
  Filter,
  Search,
  ArrowLeft,
  Target
} from 'lucide-react'
import { api } from '@/lib/api'
import { MatchCard } from '@/components/MatchCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export default function MatchesPage() {
  const router = useRouter()
  const [filters, setFilters] = useState({
    status: 'all',
    league_id: '',
    date_from: '',
    date_to: '',
    search: '',
  })
  const [showFilters, setShowFilters] = useState(false)

  // Fetch matches
  const { data: matches, isLoading: matchesLoading, refetch } = useQuery(
    ['matches', filters],
    () => api.matches.getMatches({
      status: filters.status !== 'all' ? filters.status : undefined,
      league_id: filters.league_id ? parseInt(filters.league_id) : undefined,
      date_from: filters.date_from || undefined,
      date_to: filters.date_to || undefined,
    }).then(response => response.data),
    {
      refetchInterval: 60000, // Refetch every minute
    }
  )

  // Fetch leagues for filter
  const { data: leagues } = useQuery(
    'leagues',
    () => api.leagues.getLeagues().then(response => response.data)
  )

  const handleFilterChange = (key: string, value: string) => {
    setFilters({
      ...filters,
      [key]: value,
    })
  }

  const clearFilters = () => {
    setFilters({
      status: 'all',
      league_id: '',
      date_from: '',
      date_to: '',
      search: '',
    })
  }

  const filteredMatches = matches?.filter((match: any) => {
    if (!filters.search) return true
    
    const searchTerm = filters.search.toLowerCase()
    return (
      match.home_team.name.toLowerCase().includes(searchTerm) ||
      match.away_team.name.toLowerCase().includes(searchTerm) ||
      match.league.name.toLowerCase().includes(searchTerm)
    )
  }) || []

  const statusOptions = [
    { value: 'all', label: 'All Matches' },
    { value: 'SCHEDULED', label: 'Scheduled' },
    { value: 'TIMED', label: 'Timed' },
    { value: 'IN_PLAY', label: 'Live' },
    { value: 'FINISHED', label: 'Finished' },
    { value: 'POSTPONED', label: 'Postponed' },
    { value: 'CANCELLED', label: 'Cancelled' },
  ]

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
            <h1 className="text-2xl font-bold text-gray-900">Matches</h1>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search matches, teams, or leagues..."
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="form-select"
                  >
                    {statusOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* League Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    League
                  </label>
                  <select
                    value={filters.league_id}
                    onChange={(e) => handleFilterChange('league_id', e.target.value)}
                    className="form-select"
                  >
                    <option value="">All Leagues</option>
                    {leagues?.map((league: any) => (
                      <option key={league.id} value={league.id}>
                        {league.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Date From */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Date
                  </label>
                  <input
                    type="date"
                    value={filters.date_from}
                    onChange={(e) => handleFilterChange('date_from', e.target.value)}
                    className="form-input"
                  />
                </div>

                {/* Date To */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To Date
                  </label>
                  <input
                    type="date"
                    value={filters.date_to}
                    onChange={(e) => handleFilterChange('date_to', e.target.value)}
                    className="form-input"
                  />
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
            Showing {filteredMatches.length} match{filteredMatches.length !== 1 ? 'es' : ''}
          </p>
        </div>

        {/* Matches Grid */}
        {matchesLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredMatches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMatches.map((match: any) => (
              <MatchCard
                key={match.id}
                match={match}
                showPrediction={true}
                onPredict={(matchId) => router.push(`/predict?match=${matchId}`)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No matches found</h3>
            <p className="text-gray-500 mb-4">
              Try adjusting your filters or search terms
            </p>
            <button
              onClick={clearFilters}
              className="btn btn-primary"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Load More Button (if needed) */}
        {filteredMatches.length > 0 && (
          <div className="mt-8 text-center">
            <button
              onClick={() => refetch()}
              className="btn btn-secondary"
            >
              Refresh Matches
            </button>
          </div>
        )}
      </div>
    </div>
  )
}