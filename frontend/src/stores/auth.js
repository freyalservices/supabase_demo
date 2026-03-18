import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    user.value = { email: data.user }
    localStorage.setItem('token', data.access_token)
    return data
  }

  async function signup(email, password) {
    const { data } = await api.post('/auth/signup', { email, password })
    return data
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {
      // Best-effort logout
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await api.get('/auth/user')
      user.value = data
    } catch {
      token.value = null
      localStorage.removeItem('token')
    }
  }

  return { user, token, isAuthenticated, login, signup, logout, fetchUser }
})
