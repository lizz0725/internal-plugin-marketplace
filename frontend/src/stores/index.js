import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getStatsOverview } from '../api'

export const useAppStore = defineStore('app', () => {
  // User info (mock for now, will integrate with SSO later)
  const userEmail = ref('')
  const userName = ref('')
  const isAdmin = ref(false)

  // Stats
  const stats = ref({
    plugins_count: 0,
    total_ratings: 0,
    marketplace_name: ''
  })

  // Loading states
  const isLoading = ref(false)

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await getStatsOverview()
      stats.value = response.data
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  // Set user (mock function for development)
  const setUser = (email, name, admin = false) => {
    userEmail.value = email
    userName.value = name
    isAdmin.value = admin
  }

  return {
    userEmail,
    userName,
    isAdmin,
    stats,
    isLoading,
    fetchStats,
    setUser
  }
})