import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

const PAGE_SIZE = 20

export const useInventarioStore = defineStore('inventario', {
  state: () => ({
    categorias: [],
    elementos: [],
    elementosTotal: 0,
    opciones: [],
    movimientos: [],
    movimientosTotal: 0,
    alertas: [],
    quimicos: [],
    dosificacionesInv: [],
    ubicaciones: [],
    traslados: [],
    trasladosTotal: 0,
    loading: false,
    error: null,
  }),
  actions: {
    async loadCategorias() {
      const { data } = await client.get('/inventario/categorias')
      this.categorias = data
    },
    async createCategoria(p) { const { data } = await client.post('/inventario/categorias', p); this.categorias.push(data); return data },
    async loadUbicaciones() {
      const { data } = await client.get('/inventario/ubicaciones')
      this.ubicaciones = data
    },
    async createUbicacion(p) { const { data } = await client.post('/inventario/ubicaciones', p); this.ubicaciones.push(data); return data },
    async updateUbicacion(id, p) { const { data } = await client.patch(`/inventario/ubicaciones/${id}`, p); const i = this.ubicaciones.findIndex((u) => u.id === id); if (i >= 0) this.ubicaciones[i] = data; return data },
    async loadElementos(filtros = {}, page = 1, orden = '', dir = 'asc') {
      this.loading = true
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/inventario', { params })
        this.elementos = data.items
        this.elementosTotal = data.total
      } catch (e) {
        this.error = apiError(e)
      } finally {
        this.loading = false
      }
    },
    // Lista ligera (id, nombre, stock resumido) para selects de formularios y filtros
    async loadOpciones() {
      const { data } = await client.get('/inventario/opciones')
      this.opciones = data
    },
    // Detalle fresco de un elemento (tras quitar stock, editar, etc.)
    async loadElemento(id) {
      const { data } = await client.get(`/inventario/${id}`)
      return data
    },
    async loadQuimicos() {
      const { data } = await client.get('/inventario', { params: { categoria_tipo: 'insumo', categoria_nombre: 'Químicos', page: 1, page_size: 100 } })
      this.quimicos = data.items
    },
    async createQuimico(p) {
      const { data } = await client.post('/inventario', p)
      this.quimicos.push(data)
      return data
    },
    async updateQuimico(id, p) {
      const { data } = await client.patch(`/inventario/${id}`, p)
      const i = this.quimicos.findIndex((q) => q.id === id)
      if (i >= 0) this.quimicos[i] = data
      return data
    },
    async loadDosificacionesInv(filtros = {}) {
      const { data } = await client.get('/planta/dosificaciones', { params: filtros })
      this.dosificacionesInv = data.items
    },
    async createDosificacionInv(p) {
      const { data } = await client.post('/planta/dosificaciones', p)
      await this.loadQuimicos()
      return data
    },
    async loadTraslados(filtros = {}, page = 1, orden = '', dir = 'desc') {
      const params = { ...filtros, page, page_size: PAGE_SIZE }
      if (orden) { params.orden = orden; params.dir_orden = dir }
      const { data } = await client.get('/inventario/traslados', { params })
      this.traslados = data.items
      this.trasladosTotal = data.total
    },
    async deleteStock(id) {
      await client.delete(`/inventario/stock/${id}`)
    },
    async createTraslado(p) {
      const { data } = await client.post('/inventario/traslados', p)
      return data
    },
    async createElemento(payload) {
      const { data } = await client.post('/inventario', payload)
      return data
    },
    async updateElemento(id, payload) {
      const { data } = await client.patch(`/inventario/${id}`, payload)
      return data
    },
    async deleteElemento(id) {
      await client.delete(`/inventario/${id}`)
    },
    async registrarMovimiento(id, tipo, payload) {
      const { data } = await client.post(`/inventario/${id}/${tipo}`, payload)
      return data
    },
    async loadMovimientos(filtros = {}, page = 1, orden = '', dir = 'desc') {
      const params = { ...filtros, page, page_size: PAGE_SIZE }
      if (orden) { params.orden = orden; params.dir_orden = dir }
      const { data } = await client.get('/inventario/movimientos', { params })
      this.movimientos = data.items
      this.movimientosTotal = data.total
    },
    async loadAlertas() {
      const { data } = await client.get('/inventario/alertas')
      this.alertas = data
    },
  },
})
