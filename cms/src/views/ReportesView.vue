<script setup>
import { ref, computed } from 'vue'
import client from '../api/http'
import { useAuthStore } from '../stores/auth'
import { hoyColombia, formatoOptions } from '../utils/format'
import DataTable from '../components/DataTable.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import SearchableSelect from '../components/SearchableSelect.vue'

const auth = useAuthStore()
const modulo = ref('inventario')
const formato = ref('csv')
const sector = ref('')
const fueraRango = ref('')
const fechaInicio = ref(hoyColombia())
const fechaFin = ref(hoyColombia())
const preview = ref([])
const previewCols = ref([])
const loading = ref(false)
const error = ref('')
const ok = ref('')

const modulos = [
  { id: 'inventario', label: 'Inventario', cols: ['id', 'nombre', 'categoria_id', 'ubicacion', 'cantidad', 'unidad', 'minimo', 'estado'] },
  { id: 'consumo', label: 'Consumo micromedidores', cols: ['lectura_id', 'fecha', 'sector', 'suscriptor', 'micromedidor_id', 'lectura', 'consumo', 'promedio_usado', 'irregular'] },
  { id: 'planta', label: 'Planta de tratamiento', cols: ['medicion_id', 'fecha', 'parametro', 'valor', 'fuera_rango', 'accion_correctiva'] },
]
const moduloOptions = computed(() => modulos.map((m) => ({ value: m.id, label: m.label })))
const fueraRangoOptions = [
  { value: 'true', label: 'Solo fuera de rango' },
  { value: 'false', label: 'Solo en rango' },
]

function buildParams() {
  const p = {}
  if (modulo.value === 'consumo' && sector.value.trim()) p.sector = sector.value.trim()
  if (modulo.value === 'planta' && fueraRango.value !== '') p.fuera_rango = fueraRango.value === 'true'
  if (fechaInicio.value) p.fecha_inicio = fechaInicio.value
  if (fechaFin.value) p.fecha_fin = fechaFin.value
  return p
}

function colLabel(c) {
  const map = { id: 'ID', nombre: 'Nombre', categoria_id: 'Categoría', ubicacion: 'Ubicación', cantidad: 'Cantidad', unidad: 'Unidad', minimo: 'Mínimo', estado: 'Estado', lectura_id: 'Lectura', fecha: 'Fecha', sector: 'Sector', suscriptor: 'Suscriptor', micromedidor_id: 'Medidor', lectura: 'Lectura', consumo: 'Consumo', promedio_usado: 'Promedio', irregular: 'Irregular', medicion_id: 'Medición', parametro: 'Parámetro', valor: 'Valor', fuera_rango: 'Fuera de rango', accion_correctiva: 'Acción correctiva' }
  return map[c] || c
}

async function verPreview() {
  error.value = ''; ok.value = ''; loading.value = true
  try {
    const { data } = await client.get(`/reportes/${modulo.value}`, { params: { ...buildParams(), formato: 'json' } })
    preview.value = data
    const keys = data.length ? Object.keys(data[0]) : modulos.find((m) => m.id === modulo.value).cols
    previewCols.value = keys.map((k) => ({ key: k, label: colLabel(k) }))
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se pudo generar la vista previa'
  } finally { loading.value = false }
}

async function exportar() {
  error.value = ''; ok.value = ''; loading.value = true
  try {
    const { data } = await client.get(`/reportes/${modulo.value}`, {
      params: { ...buildParams(), formato: formato.value },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `reporte_${modulo.value}.${formato.value}`
    document.body.appendChild(a); a.click(); a.remove()
    window.URL.revokeObjectURL(url)
    ok.value = `Archivo ${formato.value.toUpperCase()} generado correctamente.`
  } catch (e) {
    error.value = 'No se pudo exportar el reporte.'
  } finally { loading.value = false }
}

const puedeVer = computed(() => ['admin', 'administrativo', 'operario'].includes(auth.rol))
</script>

<template>
  <div v-if="!puedeVer">
    <BaseAlert type="bad">Tu rol no tiene permiso para ver reportes.</BaseAlert>
  </div>
  <div v-else>
    <h1>Reportes</h1>
    <p class="muted">Filtre por módulo, fecha y sector, y exporte en CSV, Excel o PDF (RF-20, RF-36, RF-54).</p>

    <div class="card">
      <div class="toolbar">
        <div class="field" style="margin:0">
          <label>Módulo</label>
          <SearchableSelect v-model="modulo" :options="moduloOptions" placeholder="Módulo" @update:model-value="preview = []" />
        </div>
        <div class="field" style="margin:0" v-if="modulo === 'consumo'">
          <label>Sector / barrio</label>
          <input class="input" v-model="sector" placeholder="Ej. Ricaurte" />
        </div>
        <div class="field" style="margin:0" v-if="modulo === 'planta'">
          <label>Estado</label>
          <SearchableSelect v-model="fueraRango" :options="fueraRangoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field" style="margin:0">
          <label>Desde</label>
          <input class="input" type="date" v-model="fechaInicio" />
        </div>
        <div class="field" style="margin:0">
          <label>Hasta</label>
          <input class="input" type="date" v-model="fechaFin" />
        </div>
        <button class="btn btn-ghost" @click="verPreview"><AppIcon name="search" />Vista previa</button>
        <button class="btn btn-ghost" @click="verPreview"><AppIcon name="refresh" />Refrescar</button>
      </div>

      <div class="toolbar">
        <label class="muted" style="align-self:center">Exportar:</label>
        <SearchableSelect v-model="formato" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-primary" @click="exportar" :disabled="loading"><AppIcon name="download" />Descargar</button>
      </div>

      <BaseAlert v-if="error" type="bad" class="mb-1">{{ error }}</BaseAlert>
      <BaseAlert v-if="ok" type="ok" class="mb-1">{{ ok }}</BaseAlert>

      <div v-if="preview.length" class="mt-2">
        <h3>Vista previa ({{ preview.length }} filas)</h3>
        <DataTable :columns="previewCols" :rows="preview" :loading="loading" />
      </div>
    </div>
  </div>
</template>
