import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

const PAGE_SIZE = 20

export const useMicromedidoresStore = defineStore('micromedidores', {
  state: () => ({
    suscriptores: [],
    suscriptoresTotal: 0,
    micromedidores: [],
    micromedidoresTotal: 0,
    lecturas: [],
    lecturasTotal: 0,
    consumo: [],
    sectores: [],
    historial: null,
    // Listas ligeras para selects/filtros (no paginadas)
    opcionesSuscriptores: [],
    opcionesMedidores: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadSuscriptores(filtros = {}, page = 1, orden = '', dir = 'asc') {
      this.loading = true
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/suscriptores', { params })
        this.suscriptores = data.items
        this.suscriptoresTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async loadSuscriptoresOpciones() {
      const { data } = await client.get('/suscriptores/opciones')
      this.opcionesSuscriptores = data
    },
    async loadSectores() {
      this.error = null
      try {
        const { data } = await client.get('/sectores')
        this.sectores = data
      } catch (e) { this.error = apiError(e) }
    },
    async loadConteoSectores() {
      const { data } = await client.get('/sectores/conteo')
      return data
    },
    async createSector(p) { const { data } = await client.post('/sectores', p); this.sectores.push(data); return data },
    async updateSector(id, p) { const { data } = await client.patch(`/sectores/${id}`, p); const i = this.sectores.findIndex((s) => s.id === id); if (i >= 0) this.sectores[i] = data; return data },
    async deleteSector(id) { await client.delete(`/sectores/${id}`); const i = this.sectores.findIndex((s) => s.id === id); if (i >= 0) this.sectores[i].estado = 'inactivo' },
    async loadHistorialSuscriptor(sid) {
      this.error = null
      try {
        const { data } = await client.get(`/suscriptores/${sid}/historial`)
        this.historial = data
      } catch (e) { this.error = apiError(e) }
    },
    async loadHistorialMicromedidor(mid) {
      this.error = null
      try {
        const { data } = await client.get(`/micromedidores/${mid}/historial`)
        this.historial = data
      } catch (e) { this.error = apiError(e) }
    },
    async createSuscriptor(p) { const { data } = await client.post('/suscriptores', p); return data },
    async updateSuscriptor(id, p) { const { data } = await client.patch(`/suscriptores/${id}`, p); return data },
    async deleteSuscriptor(id) { await client.delete(`/suscriptores/${id}`); },

    async loadMicromedidores(filtros = {}, page = 1, orden = '', dir = 'asc') {
      this.loading = true
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/micromedidores', { params })
        this.micromedidores = data.items
        this.micromedidoresTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async loadMicromedidoresOpciones() {
      const { data } = await client.get('/micromedidores/opciones')
      this.opcionesMedidores = data
    },
    async createMicromedidor(p) { const { data } = await client.post('/micromedidores', p); return data },
    async updateMicromedidor(id, p) { const { data } = await client.patch(`/micromedidores/${id}`, p); return data },
    async deleteMicromedidor(id) { await client.delete(`/micromedidores/${id}`); },

    async loadLecturas(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.loading = true
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/lecturas', { params })
        this.lecturas = data.items
        this.lecturasTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async createLectura(p) { const { data } = await client.post('/lecturas', p); return data },

    async loadConsumoPorSector(sector) {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get(`/consumo/sector/${encodeURIComponent(sector)}`)
        this.consumo = data
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
  },
})
