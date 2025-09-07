import axios from 'axios'
import { logger } from './logger'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'


// Create axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const api = {
  // Auth endpoints
  auth: {
    login: (credentials: { username: string; password: string }) =>
      apiClient.post('/auth/login', credentials),
    register: (userData: { username: string; email: string; password: string; full_name?: string }) =>
      apiClient.post('/auth/register', userData),
    getMe: () => apiClient.get('/auth/me'),
    telegramAuth: (telegramData: any) =>
      apiClient.post('/auth/telegram', telegramData),
  },

  // User endpoints
  users: {
    getUsers: (params?: { skip?: number; limit?: number; is_active?: boolean }) =>
      apiClient.get('/users', { params }),
    getUser: (id: number) => apiClient.get(`/users/${id}`),
    updateUser: (id: number, data: any) => apiClient.put(`/users/${id}`, data),
    deleteUser: (id: number) => apiClient.delete(`/users/${id}`),
    getStats: () => apiClient.get('/users/stats'),
  },

  // Match endpoints
  matches: {
    getMatches: (params?: {
      skip?: number
      limit?: number
      league_id?: number
      team_id?: number
      status?: string
      date_from?: string
      date_to?: string
    }) => apiClient.get('/matches', { params }),
    getMatch: (id: number) => apiClient.get(`/matches/${id}`),
    getUpcoming: (params?: { limit?: number; league_id?: number }) =>
      apiClient.get('/matches/upcoming', { params }),
    getLive: () => apiClient.get('/matches/live'),
    createMatch: (data: any) => apiClient.post('/matches', data),
    updateMatch: (id: number, data: any) => apiClient.put(`/matches/${id}`, data),
  },

  // Prediction endpoints
  predictions: {
    getPredictions: (params?: {
      skip?: number
      limit?: number
      user_id?: number
      match_id?: number
      prediction_type?: string
      result?: string
    }) => apiClient.get('/predictions', { params }),
    getPrediction: (id: number) => apiClient.get(`/predictions/${id}`),
    getUserPredictions: (params?: { limit?: number }) =>
      apiClient.get('/predictions/user', { params }),
    getMatchPredictions: (matchId: number) =>
      apiClient.get(`/predictions/match/${matchId}`),
    createPrediction: (data: {
      match_id: number
      prediction_type: string
      prediction_value: string
      confidence: number
      odds?: number
      stake?: number
      additional_data?: string
    }) => apiClient.post('/predictions', data),
    updatePrediction: (id: number, data: any) =>
      apiClient.put(`/predictions/${id}`, data),
    getLeaderboard: (params?: { limit?: number }) =>
      apiClient.get('/predictions/leaderboard', { params }),
  },

  // League endpoints
  leagues: {
    getLeagues: (params?: {
      skip?: number
      limit?: number
      country?: string
      is_active?: string
    }) => apiClient.get('/leagues', { params }),
    getLeague: (id: number) => apiClient.get(`/leagues/${id}`),
    getLeagueTeams: (id: number) => apiClient.get(`/leagues/${id}/teams`),
    getLeagueTable: (id: number) => apiClient.get(`/leagues/${id}/table`),
    createLeague: (data: any) => apiClient.post('/leagues', data),
    updateLeague: (id: number, data: any) => apiClient.put(`/leagues/${id}`, data),
  },

  // Team endpoints
  teams: {
    getTeams: (params?: {
      skip?: number
      limit?: number
      league_id?: number
      country?: string
    }) => apiClient.get('/teams', { params }),
    getTeam: (id: number) => apiClient.get(`/teams/${id}`),
    getTeamStats: (id: number) => apiClient.get(`/teams/${id}/stats`),
    createTeam: (data: any) => apiClient.post('/teams', data),
    updateTeam: (id: number, data: any) => apiClient.put(`/teams/${id}`, data),
  },
}

export default api