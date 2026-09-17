<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import client from '../api/http'
import { useAuthStore } from '../stores/auth'
import { hoyColombia, formatoOptions } from '../utils/format'
import { debounce } from '../utils/debounce'
import DataTable from '../components/DataTable.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import BaseInput from '../components/BaseInput.vue'

const auth = useAuthStore()
const modulo = ref('inventario')
const formato = ref('csv')
const sector = ref('')
const fueraRango = ref('')
const fechaInicio = ref(hoyColombia())
const fechaFin = ref(hoyColombia())
const preview = ref([])
const previewCols = ref([])
const previewTotal = ref(0)
const loading = ref(false)
const error = ref('')
const ok = ref('')

const modulos = [
  { id: 'inventario', endpoint: '/reportes/inventario', tipo: 'elementos', label: 'Inventario', cols: ['tipo', 'nombre', 'categoria', 'ubicacion', 'cantidad', 'unidad', 'minimo', 'valor', 'estado'] },
  { id: 'consumo', endpoint: '/reportes/micromedidores', tipo: 'lecturas', label: 'Consumo micromedidores', cols: ['fecha', 'hora', 'suscriptor', 'medidor', 'lectura', 'consumo', 'promedio_usado', 'irregular', 'novedad'] },
  { id: 'planta', endpoint: '/reportes/planta', tipo: 'mediciones', label: 'Planta de tratamiento', cols: ['fecha', 'hora', 'parametro', 'valor', 'fuera_rango', 'accion_correctiva'] },
]
const moduloOptions = computed(() => modulos.map((m) => ({ value: m.id, label: m.label })))
const fueraRangoOptions = [
  { value: 'true', label: 'Solo fuera de rango' },
  { value: 'false', label: 'Solo en rango' },
]

const moduloActual = computed(() => modulos.find((m) => m.id === modulo.value) || modulos[0])

function buildParams() {
  const p = { tipo: moduloActual.value.tipo }
  if (modulo.value === 'consumo' && sector.value.trim()) p.sector = sector.value.trim()
  if (modulo.value === 'planta' && fueraRango.value !== '') p.fuera_rango = fueraRango.value === 'true'
  if (fechaInicio.value) p.fecha_inicio = fechaInicio.value
  if (fechaFin.value) p.fecha_fin = fechaFin.value
  return p
}

function colLabel(c) {
  const map = { nombre: 'Nombre', categoria: 'Categoría', ubicacion: 'Ubicación', cantidad: 'Cantidad', unidad: 'Unidad', minimo: 'Mínimo', estado: 'Estado', fecha: 'Fecha', hora: 'Hora', sector: 'Sector', suscriptor: 'Suscriptor', medidor: 'Medidor', lectura: 'Lectura', consumo: 'Consumo', promedio_usado: 'Estimada (promedio)', irregular: 'Irregular', novedad: 'Novedad', parametro: 'Parámetro', valor: 'Valor', fuera_rango: 'Fuera de rango', accion_correctiva: 'Acción correctiva', tipo: 'Tipo', direccion: 'Dirección', codigo_usuario: 'Código usuario', codigo_facturacion: 'Código facturación', identificacion: 'Identificación', tipo_usuario: 'Tipo de usuario', serial: 'Serial', fecha_instalacion: 'Instalación', insumo: 'Insumo', tasa: 'Tasa', unidad_tasa: 'Unidad tasa', observaciones: 'Observaciones', responsable: 'Responsable', horas: 'Horas', foto_url: 'Foto', valor: 'Valor' }
  return map[c] || c
}

async function verPreview() {
  error.value = ''; ok.value = ''; loading.value = true
  try {
    const { data } = await client.get(moduloActual.value.endpoint, { params: { ...buildParams(), formato: 'json' } })
    /* La vista previa se limita a 200 filas: el listado completo siempre
       está disponible en la descarga (CSV/Excel/PDF). */
    const filas = Array.isArray(data) ? data : []
    preview.value = filas.slice(0, 200)
    previewTotal.value = filas.length
    const keys = preview.value.length ? Object.keys(preview.value[0]) : moduloActual.value.cols
    previewCols.value = keys.map((k) => ({ key: k, label: colLabel(k) }))
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se pudo generar la vista previa'
  } finally { loading.value = false }
}

async function exportar() {
  error.value = ''; ok.value = ''; loading.value = true
  try {
    const { data } = await client.get(moduloActual.value.endpoint, {
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

/* La vista previa se regenera sola (debounce) al cambiar módulo, filtros o fechas */
const verPreviewDeb = debounce(() => verPreview(), 400)
watch([modulo, sector, fueraRango, fechaInicio, fechaFin], () => { if (puedeVer.value) verPreviewDeb() })
/* Primer render: arranca la vista previa de una vez (skeleton inmediato) */
onMounted(() => { if (puedeVer.value) verPreview() })
</script>

<template>
  <div v-if="!puedeVer">
    <BaseAlert type="bad">Tu rol no tiene permiso para ver reportes.</BaseAlert>
  </div>
  <div v-else class="view-fit">
    <h1>Reportes</h1>
    <p class="muted">Filtre por módulo, fecha y sector, y exporte en CSV, Excel o PDF.</p>

    <div class="card">
      <div class="toolbar">
        <div class="field" style="margin:0">
          <label>Módulo</label>
          <SearchableSelect v-model="modulo" :options="moduloOptions" placeholder="Módulo" @update:model-value="preview = []" />
        </div>
        <div class="field" style="margin:0" v-if="modulo === 'consumo'">
          <label>Sector / barrio</label>
          <BaseInput v-model="sector" placeholder="Escriba para filtrar…" />
        </div>
        <div class="field" style="margin:0" v-if="modulo === 'planta'">
          <label>Estado</label>
          <SearchableSelect v-model="fueraRango" :options="fueraRangoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field" style="margin:0">
          <label>Desde</label>
          <BaseInput v-model="fechaInicio" type="date" />
        </div>
        <div class="field" style="margin:0">
          <label>Hasta</label>
          <BaseInput v-model="fechaFin" type="date" />
        </div>
        <button class="btn btn-ghost" :disabled="loading" @click="verPreview"><span v-if="loading" class="spinner"></span><AppIcon v-else name="refresh" />{{ loading ? 'Generando…' : 'Refrescar' }}</button>
      </div>

      <div class="toolbar">
        <label class="muted" style="align-self:center">Exportar:</label>
        <SearchableSelect v-model="formato" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-primary" @click="exportar" :disabled="loading"><span v-if="loading" class="spinner"></span><AppIcon v-else name="download" />{{ loading ? 'Generando…' : 'Descargar' }}</button>
      </div>

      <BaseAlert v-if="error" type="bad" class="mb-1">{{ error }}</BaseAlert>
      <BaseAlert v-if="ok" type="ok" class="mb-1">{{ ok }}</BaseAlert>

      <div v-if="preview.length || loading" class="mt-2 preview-wrap">
        <h3>Vista previa ({{ previewTotal > 200 ? `primeras 200 de ${previewTotal}` : `${previewTotal} filas` }})</h3>
        <p v-if="previewTotal > 200" class="muted" style="font-size:.82rem">Vista previa limitada a 200 filas: descargue el reporte para obtener el listado completo.</p>
        <DataTable :columns="previewCols" :rows="preview" :loading="loading" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* La tarjeta y la vista previa se ajustan al alto del panel: la tabla scrollea dentro
   (los estilos de .data-table/.table-wrap viven en theme.css para todo el sitio) */
.view-fit .card { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.preview-wrap { flex: 1; min-height: 0; display: flex; flex-direction: column; }
</style>
