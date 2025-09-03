import { formatDateTime, getStatusColor } from '@/lib/utils'
import { Calendar, MapPin, Clock } from 'lucide-react'

interface MatchCardProps {
  match: {
    id: number
    home_team: { name: string; logo_url?: string }
    away_team: { name: string; logo_url?: string }
    match_date: string
    status: string
    venue?: string
    home_score?: number
    away_score?: number
    league: { name: string }
  }
  showPrediction?: boolean
  onPredict?: (matchId: number) => void
}

export function MatchCard({ match, showPrediction = false, onPredict }: MatchCardProps) {
  const matchDate = new Date(match.match_date)
  const isFinished = match.status === 'FINISHED'
  const isLive = match.status === 'IN_PLAY'
  const isUpcoming = match.status === 'SCHEDULED' || match.status === 'TIMED'

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="card-body">
        {/* League */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600">
            {match.league.name}
          </span>
          <span className={`badge ${getStatusColor(match.status)}`}>
            {match.status.replace('_', ' ')}
          </span>
        </div>

        {/* Teams */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            {match.home_team.logo_url && (
              <img
                src={match.home_team.logo_url}
                alt={match.home_team.name}
                className="w-8 h-8 object-contain"
              />
            )}
            <span className="font-semibold text-gray-900">
              {match.home_team.name}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {isFinished || isLive ? (
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {match.home_score} - {match.away_score}
                </div>
                {isLive && (
                  <div className="text-xs text-green-600 font-medium">
                    LIVE
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-500">vs</div>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <span className="font-semibold text-gray-900">
              {match.away_team.name}
            </span>
            {match.away_team.logo_url && (
              <img
                src={match.away_team.logo_url}
                alt={match.away_team.name}
                className="w-8 h-8 object-contain"
              />
            )}
          </div>
        </div>

        {/* Match Info */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {formatDateTime(match.match_date)}
            </div>
            {match.venue && (
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-1" />
                {match.venue}
              </div>
            )}
          </div>
        </div>

        {/* Prediction Button */}
        {showPrediction && isUpcoming && onPredict && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => onPredict(match.id)}
              className="btn btn-primary btn-sm w-full"
            >
              Make Prediction
            </button>
          </div>
        )}
      </div>
    </div>
  )
}