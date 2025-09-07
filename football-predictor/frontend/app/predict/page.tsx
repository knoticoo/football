'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation } from 'react-query'
import { useRouter, useSearchParams } from 'next/navigation'
import { 
  Target, 
  Calendar,
  TrendingUp,
  ArrowLeft,
  CheckCircle
} from 'lucide-react'
import { api } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import toast from 'react-hot-toast'

export default function PredictPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const matchId = searchParams.get('match')
  
  const [selectedMatch, setSelectedMatch] = useState<any>(null)
  const [predictionData, setPredictionData] = useState({
    prediction_type: 'WIN_DRAW_WIN',
    prediction_value: '',
    confidence: 0.5,
    odds: '',
    stake: '',
    additional_data: '',
  })

  // Fetch upcoming matches
  const { data: upcomingMatches, isLoading: matchesLoading } = useQuery(
    'upcoming-matches',
    () => api.matches.getUpcoming({ limit: 20 }).then(response => response.data),
    {
      onSuccess: (data) => {
        if (matchId && data) {
          const match = data.find((m: any) => m.id === parseInt(matchId))
          if (match) {
            setSelectedMatch(match)
          }
        }
      }
    }
  )

  // Create prediction mutation
  const createPredictionMutation = useMutation(
    (data: any) => api.predictions.createPrediction(data),
    {
      onSuccess: () => {
        toast.success('Prediction created successfully!')
        router.push('/dashboard')
      },
      onError: (error: any) => {
        const message = error.response?.data?.detail || 'Failed to create prediction'
        toast.error(message)
      },
    }
  )

  const predictionTypes = [
    { value: 'WIN_DRAW_WIN', label: '1X2 (Win/Draw/Win)', options: ['1', 'X', '2'] },
    { value: 'OVER_UNDER', label: 'Over/Under Goals', options: ['Over 0.5', 'Over 1.5', 'Over 2.5', 'Under 2.5', 'Under 1.5'] },
    { value: 'BOTH_TEAMS_SCORE', label: 'Both Teams to Score', options: ['Yes', 'No'] },
    { value: 'CORRECT_SCORE', label: 'Correct Score', options: ['1-0', '2-0', '2-1', '3-0', '3-1', '3-2', '0-1', '0-2', '1-2', '0-3', '1-3', '2-3', '1-1', '2-2', '3-3', '0-0'] },
    { value: 'DOUBLE_CHANCE', label: 'Double Chance', options: ['1X', '12', 'X2'] },
  ]

  const handleMatchSelect = (match: any) => {
    setSelectedMatch(match)
    setPredictionData({
      ...predictionData,
      prediction_value: '',
    })
  }

  const handlePredictionTypeChange = (type: string) => {
    setPredictionData({
      ...predictionData,
      prediction_type: type,
      prediction_value: '',
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedMatch) {
      toast.error('Please select a match')
      return
    }

    if (!predictionData.prediction_value) {
      toast.error('Please select a prediction value')
      return
    }

    if (predictionData.confidence < 0.1 || predictionData.confidence > 1) {
      toast.error('Confidence must be between 0.1 and 1.0')
      return
    }

    const submitData = {
      match_id: selectedMatch.id,
      prediction_type: predictionData.prediction_type,
      prediction_value: predictionData.prediction_value,
      confidence: predictionData.confidence,
      odds: predictionData.odds ? parseFloat(predictionData.odds) : undefined,
      stake: predictionData.stake ? parseFloat(predictionData.stake) : undefined,
      additional_data: predictionData.additional_data || undefined,
    }

    createPredictionMutation.mutate(submitData)
  }

  const getCurrentPredictionType = () => {
    return predictionTypes.find(type => type.value === predictionData.prediction_type)
  }

  if (matchesLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
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
            <h1 className="text-2xl font-bold text-gray-900">Make a Prediction</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Match Selection */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Select Match
              </h3>
            </div>
            <div className="card-body">
              {upcomingMatches?.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {upcomingMatches.map((match: any) => (
                    <div
                      key={match.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedMatch?.id === match.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleMatchSelect(match)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {match.home_team.logo_url && (
                            <img
                              src={match.home_team.logo_url}
                              alt={match.home_team.name}
                              className="w-6 h-6 object-contain"
                            />
                          )}
                          <span className="font-medium text-gray-900">
                            {match.home_team.name}
                          </span>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-500">vs</div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-gray-900">
                            {match.away_team.name}
                          </span>
                          {match.away_team.logo_url && (
                            <img
                              src={match.away_team.logo_url}
                              alt={match.away_team.name}
                              className="w-6 h-6 object-contain"
                            />
                          )}
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-gray-500">
                        {match.league.name} • {new Date(match.match_date).toLocaleDateString()} at {new Date(match.match_date).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">
                  No upcoming matches available
                </p>
              )}
            </div>
          </div>

          {/* Prediction Form */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Make Prediction
              </h3>
            </div>
            <div className="card-body">
              {selectedMatch ? (
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Selected Match Display */}
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {selectedMatch.home_team.logo_url && (
                          <img
                            src={selectedMatch.home_team.logo_url}
                            alt={selectedMatch.home_team.name}
                            className="w-8 h-8 object-contain"
                          />
                        )}
                        <span className="font-semibold text-gray-900">
                          {selectedMatch.home_team.name}
                        </span>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-gray-500">vs</div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="font-semibold text-gray-900">
                          {selectedMatch.away_team.name}
                        </span>
                        {selectedMatch.away_team.logo_url && (
                          <img
                            src={selectedMatch.away_team.logo_url}
                            alt={selectedMatch.away_team.name}
                            className="w-8 h-8 object-contain"
                          />
                        )}
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500 text-center">
                      {selectedMatch.league.name} • {new Date(selectedMatch.match_date).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Prediction Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Prediction Type
                    </label>
                    <select
                      value={predictionData.prediction_type}
                      onChange={(e) => handlePredictionTypeChange(e.target.value)}
                      className="form-select"
                    >
                      {predictionTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Prediction Value */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Prediction
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {getCurrentPredictionType()?.options.map((option) => (
                        <button
                          key={option}
                          type="button"
                          className={`p-3 text-sm font-medium rounded-lg border transition-colors ${
                            predictionData.prediction_value === option
                              ? 'border-primary-500 bg-primary-50 text-primary-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => setPredictionData({
                            ...predictionData,
                            prediction_value: option
                          })}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Confidence */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confidence: {(predictionData.confidence * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="1"
                      step="0.1"
                      value={predictionData.confidence}
                      onChange={(e) => setPredictionData({
                        ...predictionData,
                        confidence: parseFloat(e.target.value)
                      })}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Low (10%)</span>
                      <span>High (100%)</span>
                    </div>
                  </div>

                  {/* Optional Fields */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Odds (optional)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        placeholder="e.g., 2.50"
                        value={predictionData.odds}
                        onChange={(e) => setPredictionData({
                          ...predictionData,
                          odds: e.target.value
                        })}
                        className="form-input"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Stake (optional)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        placeholder="e.g., 10.00"
                        value={predictionData.stake}
                        onChange={(e) => setPredictionData({
                          ...predictionData,
                          stake: e.target.value
                        })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  {/* Additional Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Notes (optional)
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Any additional thoughts or analysis..."
                      value={predictionData.additional_data}
                      onChange={(e) => setPredictionData({
                        ...predictionData,
                        additional_data: e.target.value
                      })}
                      className="form-textarea"
                    />
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={createPredictionMutation.isLoading || !predictionData.prediction_value}
                    className="w-full btn btn-primary btn-lg flex items-center justify-center"
                  >
                    {createPredictionMutation.isLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <>
                        <CheckCircle className="w-5 h-5 mr-2" />
                        Submit Prediction
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Please select a match to make a prediction</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}