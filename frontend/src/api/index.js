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

export const submitPlugin = (data) => {
  return api.post('/plugins/submit', data)
}

export const submitPluginUpload = (formData) => {
  return api.post('/plugins/submit/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}

export const submitPluginGit = (data) => {
  return api.post('/plugins/submit/git-sync', data)
}

export const getSubmissionFiles = (submissionId) => {
  return api.get(`/plugins/submissions/${submissionId}/files`)
}

export const ratePlugin = (name, data) => {
  return api.post(`/plugins/${name}/rate`, data)
}

// Review APIs
export const getPendingReviews = () => {
  return api.get('/reviews/pending')
}

export const getAllSubmissions = () => {
  return api.get('/reviews/all')
}

export const approveSubmission = (submissionId, reviewerEmail, notes = '') => {
  return api.post(`/reviews/${submissionId}/approve`, {
    reviewer_email: reviewerEmail,
    notes: notes
  })
}

export const rejectSubmission = (submissionId, reviewerEmail, reason) => {
  return api.post(`/reviews/${submissionId}/reject`, {
    reviewer_email: reviewerEmail,
    reason: reason
  })
}

// Stats APIs
export const getStatsOverview = () => {
  return api.get('/stats/overview')
}

export const getRatingsStats = () => {
  return api.get('/stats/ratings')
}

// Health check
export const healthCheck = () => {
  return api.get('/health')
}

export default api