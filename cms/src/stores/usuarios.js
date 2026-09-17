import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

const PAGE_SIZE = 20

export const useUsuariosStore = defineStore('usuarios', {
  state: () => ({
    usuarios: [],
    usuariosTotal: 0,
    opciones: [],
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
    async loadUsuarios(page = 1, orden = '', dir = 'asc') {
      this.loading = true
      this.error = null
      try {
        const params = { page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/usuarios', { params })
        this.usuarios = data.items
        this.usuariosTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    // Lista ligera {id, nombre, estado} para selects de responsables
    async loadOpciones() {
      const { data } = await client.get('/usuarios/opciones')
      this.opciones = data
    },
    async createUsuario(p) { const { data } = await client.post('/usuarios', p); return data },
    async updateUsuario(id, p) { const { data } = await client.patch(`/usuarios/${id}`, p); return data },
    async deleteUsuario(id) { await client.delete(`/usuarios/${id}`); },
  },
})
