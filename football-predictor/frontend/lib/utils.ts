import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatTime(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatCurrency(amount: number, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatNumber(number: number) {
  return new Intl.NumberFormat('en-US').format(number)
}

export function formatPercentage(number: number, decimals = 1) {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(number / 100)
}

export function getInitials(name: string) {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function getStatusColor(status: string) {
  switch (status.toLowerCase()) {
    case 'scheduled':
    case 'timed':
      return 'text-blue-600 bg-blue-100'
    case 'in_play':
    case 'in-play':
      return 'text-green-600 bg-green-100'
    case 'finished':
      return 'text-gray-600 bg-gray-100'
    case 'postponed':
      return 'text-yellow-600 bg-yellow-100'
    case 'cancelled':
    case 'canceled':
      return 'text-red-600 bg-red-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}

export function getPredictionResultColor(result: string) {
  switch (result.toLowerCase()) {
    case 'won':
      return 'text-green-600 bg-green-100'
    case 'lost':
      return 'text-red-600 bg-red-100'
    case 'pending':
      return 'text-yellow-600 bg-yellow-100'
    case 'void':
      return 'text-gray-600 bg-gray-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}

export function getConfidenceColor(confidence: number) {
  if (confidence >= 0.8) return 'text-green-600 bg-green-100'
  if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}