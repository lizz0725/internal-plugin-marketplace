import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Plugin APIs
export const getPlugins = (search = null, keyword = null) => {
  const params = {}
  if (search) params.search = search
  if (keyword) params.keyword = keyword
  return api.get('/plugins/', { params })
}

export const getPlugin = (name) => {
  return api.get(`/plugins/${name}`)
}

export const ratePlugin = (name, data) => {
  return api.post(`/plugins/${name}/rate`, data)
}

// Stats APIs
export const getStatsOverview = () => {
  return api.get('/stats/overview')
}

export const getRatingsStats = () => {
  return api.get('/stats/ratings')
}

// Sync APIs
export const getSyncStatus = () => {
  return api.get('/sync/status')
}

// Health check
export const healthCheck = () => {
  return api.get('/health')
}

export default api