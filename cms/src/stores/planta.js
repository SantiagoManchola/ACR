import { defineStore } from 'pinia'
import client, { apiError } from '../api/http'

const PAGE_SIZE = 20

export const usePlantaStore = defineStore('planta', {
  state: () => ({
    parametros: [],
    mediciones: [],
    medicionesTotal: 0,
    fueraRango: [],
    dosificaciones: [],
    dosificacionesTotal: 0,
    actividades: [],
    actividadesTotal: 0,
    horas: [],
    horasTotal: 0,
    horasGrafico: [],
    // Responsables ligeros para selects (no paginados)
    usuariosOpciones: [],
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

    async loadMediciones(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.loading = true
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/planta/mediciones', { params })
        this.mediciones = data.items
        this.medicionesTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.loading = false }
    },
    async createMedicion(p) { const { data } = await client.post('/planta/mediciones', p); return data },

    async loadFueraRango() {
      // Estado ACTUAL: parámetros cuya ÚLTIMA medición está fuera de rango
      // (no lista mediciones pasadas; ya ajustadas no siguen alertando).
      const { data } = await client.get('/planta/parametros-fuera-rango')
      this.fueraRango = data
    },

    async loadDosificaciones(filtros = {}, page = 1, orden = '', dir = 'desc') {
      const params = { ...filtros, page, page_size: PAGE_SIZE }
      if (orden) { params.orden = orden; params.dir_orden = dir }
      const { data } = await client.get('/planta/dosificaciones', { params })
      this.dosificaciones = data.items
      this.dosificacionesTotal = data.total
    },
    async createDosificacion(p) {
      const { data } = await client.post('/planta/dosificaciones', p)
      return data
    },

    async loadActividades(filtros = {}, page = 1, orden = '', dir = 'desc') {
      const params = { ...filtros, page, page_size: PAGE_SIZE }
      if (orden) { params.orden = orden; params.dir_orden = dir }
      const { data } = await client.get('/planta/actividades', { params })
      this.actividades = data.items
      this.actividadesTotal = data.total
    },
    async createActividad(p) {
      const { data } = await client.post('/planta/actividades', p)
      return data
    },
    async updateActividad(id, p) { const { data } = await client.patch(`/planta/actividades/${id}`, p); return data },

    async loadHoras(filtros = {}, page = 1, orden = '', dir = 'desc') {
      const params = { ...filtros, page, page_size: PAGE_SIZE }
      if (orden) { params.orden = orden; params.dir_orden = dir }
      const { data } = await client.get('/planta/horas-servicio', { params })
      this.horas = data.items
      this.horasTotal = data.total
    },
    // Datos del gráfico anual (rango amplio): no toca `horas` de la tabla.
    async loadHorasGrafico(filtros = {}) { const { data } = await client.get('/planta/horas-servicio', { params: filtros }); this.horasGrafico = data; return data },
    async createHoraServicio(p) {
      const { data } = await client.post('/planta/horas-servicio', p)
      return data
    },
    // Responsables ligeros (selects de planta)
    async loadUsuariosOpciones() {
      const { data } = await client.get('/usuarios/opciones')
      this.usuariosOpciones = data
    },
  },
})
