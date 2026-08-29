import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

export const usePlantaStore = defineStore('planta', {
  state: () => ({
    parametros: [],
    mediciones: [],
    fueraRango: [],
    productos: [],
    dosificaciones: [],
    actividades: [],
    horas: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadParametros() {
      const { data } = await client.get('/planta/parametros')
      this.parametros = data
    },
    async createParametro(p) { const { data } = await client.post('/planta/parametros', p); this.parametros.push(data); return data },
    async updateParametro(id, p) { const { data } = await client.patch(`/planta/parametros/${id}`, p); const i = this.parametros.findIndex((x) => x.id === id); if (i >= 0) this.parametros[i] = data; return data },

    async loadMediciones(filtros = {}) {
      this.loading = true
      this.error = null
      try { const { data } = await client.get('/planta/mediciones', { params: filtros }); this.mediciones = data }
      catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async createMedicion(p) { const { data } = await client.post('/planta/mediciones', p); await this.loadMediciones(); return data },

    async loadFueraRango() {
      const { data } = await client.get('/planta/mediciones/fuera-rango')
      this.fueraRango = data
    },

    async loadProductos() { const { data } = await client.get('/planta/productos'); this.productos = data },
    async createProducto(p) { const { data } = await client.post('/planta/productos', p); this.productos.push(data); return data },
    async updateProducto(id, p) { const { data } = await client.patch(`/planta/productos/${id}`, p); const i = this.productos.findIndex((x) => x.id === id); if (i >= 0) this.productos[i] = data; return data },
    async loadDosificaciones(filtros = {}) {
      const { data } = await client.get('/planta/dosificaciones', { params: filtros }); this.dosificaciones = data
    },
    async createDosificacion(p) {
      const { data } = await client.post('/planta/dosificaciones', p); await this.loadDosificaciones(); return data
    },

    async loadActividades(filtros = {}) { const { data } = await client.get('/planta/actividades', { params: filtros }); this.actividades = data },
    async createActividad(p) { const { data } = await client.post('/planta/actividades', p); await this.loadActividades(); return data },
    async updateActividad(id, p) { const { data } = await client.patch(`/planta/actividades/${id}`, p); return data },

    async loadHoras(filtros = {}) { const { data } = await client.get('/planta/horas-servicio', { params: filtros }); this.horas = data },
    async createHoraServicio(p) {
      const { data } = await client.post('/planta/horas-servicio', p); await this.loadHoras(); return data
    },
  },
})
