import { defineStore } from 'pinia'
import client, { getToken, setToken, setRefreshToken, limpiarSesion, apiError } from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: null,
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    rol: (s) => s.user?.rol?.nombre || null,
    nombre: (s) => s.user?.nombre || '',
  },
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const body = new URLSearchParams({ username, password })
        const { data } = await client.post('/auth/login', body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        setToken(data.access_token)
        setRefreshToken(data.refresh_token)
        this.token = data.access_token
        await this.fetchMe()
        return true
      } catch (e) {
        this.error = apiError(e, 'No se pudo iniciar sesión')
        return false
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      const { data } = await client.get('/auth/me')
      this.user = data
      return data
    },
    logout() {
      limpiarSesion()
      this.token = null
      this.user = null
    },
  },
})
