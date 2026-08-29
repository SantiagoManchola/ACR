import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

export const useUsuariosStore = defineStore('usuarios', {
  state: () => ({
    usuarios: [],
    roles: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadRoles() {
      const { data } = await client.get('/usuarios/roles')
      this.roles = data
    },
    async createRol(p) { const { data } = await client.post('/usuarios/roles', p); this.roles.push(data); return data },
    async loadUsuarios() {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get('/usuarios')
        this.usuarios = data
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async createUsuario(p) { const { data } = await client.post('/usuarios', p); this.usuarios.push(data); return data },
    async updateUsuario(id, p) { const { data } = await client.patch(`/usuarios/${id}`, p); const i = this.usuarios.findIndex((u) => u.id === id); if (i >= 0) this.usuarios[i] = data; return data },
    async deleteUsuario(id) { await client.delete(`/usuarios/${id}`); const i = this.usuarios.findIndex((u) => u.id === id); if (i >= 0) this.usuarios[i].estado = 'inactivo' },
  },
})
