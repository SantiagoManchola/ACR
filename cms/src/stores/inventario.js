import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

export const useInventarioStore = defineStore('inventario', {
  state: () => ({
    categorias: [],
    elementos: [],
    movimientos: [],
    alertas: [],
    quimicos: [],
    dosificacionesInv: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadCategorias() {
      const { data } = await client.get('/inventario/categorias')
      this.categorias = data
    },
    async createCategoria(p) { const { data } = await client.post('/inventario/categorias', p); this.categorias.push(data); return data },
    async loadElementos(filtros = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get('/inventario', { params: filtros })
        this.elementos = data
      } catch (e) {
        this.error = apiError(e)
      } finally {
        this.loading = false
      }
    },
    async loadQuimicos() {
      const { data } = await client.get('/planta/productos')
      this.quimicos = data
    },
    async createQuimico(p) {
      const { data } = await client.post('/planta/productos', p)
      this.quimicos.push(data)
      return data
    },
    async updateQuimico(id, p) {
      const { data } = await client.patch(`/planta/productos/${id}`, p)
      const i = this.quimicos.findIndex((q) => q.id === id)
      if (i >= 0) this.quimicos[i] = data
      return data
    },
    async loadDosificacionesInv(filtros = {}) {
      const { data } = await client.get('/planta/dosificaciones', { params: filtros })
      this.dosificacionesInv = data
    },
    async createDosificacionInv(p) {
      const { data } = await client.post('/planta/dosificaciones', p)
      await this.loadQuimicos()
      return data
    },
    async createElemento(payload) {
      const { data } = await client.post('/inventario', payload)
      this.elementos.push(data)
      return data
    },
    async updateElemento(id, payload) {
      const { data } = await client.patch(`/inventario/${id}`, payload)
      const i = this.elementos.findIndex((e) => e.id === id)
      if (i >= 0) this.elementos[i] = data
      return data
    },
    async deleteElemento(id) {
      await client.delete(`/inventario/${id}`)
      const i = this.elementos.findIndex((e) => e.id === id)
      if (i >= 0) this.elementos[i].estado = 'inactivo'
    },
    async registrarMovimiento(id, tipo, payload) {
      const { data } = await client.post(`/inventario/${id}/${tipo}`, payload)
      return data
    },
    async loadMovimientos(elementoId) {
      const { data } = await client.get('/inventario/movimientos', {
        params: { elemento_id: elementoId },
      })
      this.movimientos = data
    },
    async loadAlertas() {
      const { data } = await client.get('/inventario/alertas')
      this.alertas = data
    },
  },
})
