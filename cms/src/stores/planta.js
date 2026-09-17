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
    // Contador de peticiones en curso (skeleton mientras haya alguna)
    cargas: 0,
    error: null,
  }),
  getters: {
    loading: (s) => s.cargas > 0,
  },
  actions: {
    async loadParametros() {
      this.cargas++
      this.error = null
      try {
        const { data } = await client.get('/planta/parametros')
        this.parametros = data
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
    },
    async createParametro(p) { const { data } = await client.post('/planta/parametros', p); this.parametros.push(data); return data },
    async updateParametro(id, p) { const { data } = await client.patch(`/planta/parametros/${id}`, p); const i = this.parametros.findIndex((x) => x.id === id); if (i >= 0) this.parametros[i] = data; return data },

    async loadMediciones(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.cargas++
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/planta/mediciones', { params })
        this.mediciones = data.items
        this.medicionesTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
    },
    async createMedicion(p) { const { data } = await client.post('/planta/mediciones', p); return data },

    async loadFueraRango() {
      // Estado ACTUAL: parámetros cuya ÚLTIMA medición está fuera de rango
      // (no lista mediciones pasadas; ya ajustadas no siguen alertando).
      this.cargas++
      this.error = null
      try {
        const { data } = await client.get('/planta/parametros-fuera-rango')
        this.fueraRango = data
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
    },

    async loadDosificaciones(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.cargas++
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/planta/dosificaciones', { params })
        this.dosificaciones = data.items
        this.dosificacionesTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
    },
    async createDosificacion(p) {
      const { data } = await client.post('/planta/dosificaciones', p)
      return data
    },

    async loadActividades(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.cargas++
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/planta/actividades', { params })
        this.actividades = data.items
        this.actividadesTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
    },
    async createActividad(p) {
      const { data } = await client.post('/planta/actividades', p)
      return data
    },
    async updateActividad(id, p) { const { data } = await client.patch(`/planta/actividades/${id}`, p); return data },

    async loadHoras(filtros = {}, page = 1, orden = '', dir = 'desc') {
      this.cargas++
      this.error = null
      try {
        const params = { ...filtros, page, page_size: PAGE_SIZE }
        if (orden) { params.orden = orden; params.dir_orden = dir }
        const { data } = await client.get('/planta/horas-servicio', { params })
        this.horas = data.items
        this.horasTotal = data.total
      } catch (e) { this.error = apiError(e) } finally { this.cargas = Math.max(0, this.cargas - 1) }
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
