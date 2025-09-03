import { formatDateTime, getPredictionResultColor, getConfidenceColor } from '@/lib/utils'
import { Target, TrendingUp, TrendingDown } from 'lucide-react'

interface PredictionCardProps {
  prediction: {
    id: number
    prediction_type: string
    prediction_value: string
    confidence: number
    result: string
    created_at: string
    match: {
      id: number
      home_team: { name: string }
      away_team: { name: string }
      match_date: string
      home_score?: number
      away_score?: number
    }
  }
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  const isWon = prediction.result === 'WON'
  const isLost = prediction.result === 'LOST'
  const isPending = prediction.result === 'PENDING'

  const getResultIcon = () => {
    if (isWon) return <TrendingUp className="w-4 h-4 text-green-600" />
    if (isLost) return <TrendingDown className="w-4 h-4 text-red-600" />
    return <Target className="w-4 h-4 text-yellow-600" />
  }

  const getPredictionTypeLabel = (type: string) => {
    switch (type) {
      case 'WIN_DRAW_WIN':
        return '1X2'
      case 'OVER_UNDER':
        return 'Over/Under'
      case 'BOTH_TEAMS_SCORE':
        return 'BTTS'
      case 'CORRECT_SCORE':
        return 'Correct Score'
      case 'DOUBLE_CHANCE':
        return 'Double Chance'
      default:
        return type
    }
  }

  const getPredictionValueLabel = (type: string, value: string) => {
    switch (type) {
      case 'WIN_DRAW_WIN':
        switch (value) {
          case '1':
            return 'Home Win'
          case 'X':
            return 'Draw'
          case '2':
            return 'Away Win'
          default:
            return value
        }
      case 'OVER_UNDER':
        return value
      case 'BOTH_TEAMS_SCORE':
        return value === 'Yes' ? 'Yes' : 'No'
      case 'CORRECT_SCORE':
        return value
      case 'DOUBLE_CHANCE':
        return value
      default:
        return value
    }
  }

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="card-body">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            {getResultIcon()}
            <span className="text-sm font-medium text-gray-600">
              {getPredictionTypeLabel(prediction.prediction_type)}
            </span>
          </div>
          <span className={`badge ${getPredictionResultColor(prediction.result)}`}>
            {prediction.result}
          </span>
        </div>

        {/* Match Info */}
        <div className="mb-3">
          <p className="font-semibold text-gray-900">
            {prediction.match.home_team.name} vs {prediction.match.away_team.name}
          </p>
          <p className="text-sm text-gray-500">
            {formatDateTime(prediction.match.match_date)}
          </p>
        </div>

        {/* Prediction Details */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm text-gray-600">Prediction</p>
            <p className="font-semibold text-gray-900">
              {getPredictionValueLabel(prediction.prediction_type, prediction.prediction_value)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Confidence</p>
            <span className={`badge ${getConfidenceColor(prediction.confidence)}`}>
              {(prediction.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Result (if available) */}
        {!isPending && (
          <div className="pt-3 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Result</span>
              <span className="font-semibold text-gray-900">
                {prediction.match.home_score} - {prediction.match.away_score}
              </span>
            </div>
          </div>
        )}

        {/* Created Date */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Predicted on {formatDateTime(prediction.created_at)}
          </p>
        </div>
      </div>
    </div>
  )
}