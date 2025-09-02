import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  icon: LucideIcon
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  className?: string
}

export function StatsCard({
  icon: Icon,
  title,
  value,
  change,
  changeType = 'neutral',
  className = '',
}: StatsCardProps) {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-green-600'
      case 'negative':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />
      case 'negative':
        return <TrendingDown className="w-4 h-4" />
      default:
        return null
    }
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-body">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg">
              <Icon className="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <div className="ml-4 flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <div className="flex items-baseline">
              <p className="text-2xl font-semibold text-gray-900">{value}</p>
              {change && (
                <div className={`ml-2 flex items-center ${getChangeColor()}`}>
                  {getChangeIcon()}
                  <span className="text-sm font-medium ml-1">{change}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}