import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

export const useMicromedidoresStore = defineStore('micromedidores', {
  state: () => ({
    suscriptores: [],
    micromedidores: [],
    lecturas: [],
    consumo: [],
    sectores: [],
    historial: null,
    loading: false,
    error: null,
  }),
  actions: {
    async loadSuscriptores(filtros = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get('/suscriptores', { params: filtros })
        this.suscriptores = data
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async loadSectores() {
      this.error = null
      try {
        const { data } = await client.get('/suscriptores/sectores')
        this.sectores = data
      } catch (e) { this.error = apiError(e) }
    },
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
    async createSuscriptor(p) { const { data } = await client.post('/suscriptores', p); this.suscriptores.push(data); return data },
    async updateSuscriptor(id, p) { const { data } = await client.patch(`/suscriptores/${id}`, p); const i = this.suscriptores.findIndex((s) => s.id === id); if (i >= 0) this.suscriptores[i] = data; return data },
    async deleteSuscriptor(id) { await client.delete(`/suscriptores/${id}`); const i = this.suscriptores.findIndex((s) => s.id === id); if (i >= 0) this.suscriptores[i].estado = 'inactivo' },

    async loadMicromedidores(filtros = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get('/micromedidores', { params: filtros })
        this.micromedidores = data
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async createMicromedidor(p) { const { data } = await client.post('/micromedidores', p); this.micromedidores.push(data); return data },
    async updateMicromedidor(id, p) { const { data } = await client.patch(`/micromedidores/${id}`, p); const i = this.micromedidores.findIndex((m) => m.id === id); if (i >= 0) this.micromedidores[i] = data; return data },
    async deleteMicromedidor(id) { await client.delete(`/micromedidores/${id}`); const i = this.micromedidores.findIndex((m) => m.id === id); if (i >= 0) this.micromedidores[i].estado = 'inactivo' },

    async loadLecturas(filtros = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await client.get('/lecturas', { params: filtros })
        this.lecturas = data
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
