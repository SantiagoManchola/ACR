<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import client, { apiError } from '../api/http'
import AppIcon from '../components/AppIcon.vue'
import BaseAlert from '../components/BaseAlert.vue'
import GraficoHoras from '../components/GraficoHoras.vue'
import { fmtNum, fmtRango } from '../utils/format'

/* El dashboard ya NO descarga listas completas: una sola petición
   GET /dashboard/resumen trae los KPIs y tops calculados en la API
   (agregados SQL) y recortados según el rol del usuario. */
const auth = useAuthStore()
const router = useRouter()

const resumen = ref(null)
/* loading inicia en true: los skeletons están en el PRIMER render
   (antes del mounted), así la vista no muestra ceros ni salta al cargar. */
const loading = ref(true)
const error = ref('')

const rol = computed(() => auth.rol)
const puedeInventario = computed(() => ['admin', 'administrativo', 'operario'].includes(rol.value))
const puedeMM = computed(() => ['admin', 'administrativo', 'operario', 'fontanero'].includes(rol.value))
const puedePlanta = computed(() => ['admin', 'operario'].includes(rol.value))
const esAdministrativo = computed(() => rol.value === 'administrativo')
/* Visibilidad fina por rol (misma regla que /dashboard/resumen):
   - administrativo: inventario/alertas solo Oficina; químicos NO ve nada.
   - fontanero y operario: sin consumo (ni total ni por medidor).
   - operario: sin suscriptores/medidores/frenados. */
const verQuimicos = computed(() => puedeInventario.value && !esAdministrativo.value)
const verConsumo = computed(() => puedeMM.value && rol.value !== 'fontanero' && rol.value !== 'operario')
const verMedidores = computed(() => puedeMM.value && rol.value !== 'operario')

/* Secciones del resumen */
const rInv = computed(() => resumen.value?.inventario || null)
const rQuim = computed(() => resumen.value?.quimicos_planta || null)
const rMM = computed(() => resumen.value?.micromedidores || null)
const rConsumo = computed(() => rMM.value?.consumo || null)
const rPlanta = computed(() => resumen.value?.planta || null)

/* Periodo del gráfico de consumo (días hacia atrás desde hoy Colombia) */
const periodoConsumo = ref(60)
const periodos = [30, 60, 90]

async function load() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await client.get('/dashboard/resumen', { params: { dias_consumo: periodoConsumo.value } })
    resumen.value = data
  } catch (e) {
    error.value = apiError(e, 'No se pudo cargar el dashboard')
  } finally {
    loading.value = false
  }
}

watch(periodoConsumo, load)

/* ---------------- Químicos en planta (conciso) ---------------- */
const quimicosTop = computed(() => rQuim.value?.items || [])
const quimicosBajos = computed(() => rQuim.value?.bajos || 0)
const quimicosTotal = computed(() => rQuim.value?.total || 0)
const esBajo = (q) => q.minimo != null && q.minimo !== '' && Number(q.cantidad) <= Number(q.minimo)
const maxQuimico = computed(() => Math.max(...quimicosTop.value.map((q) => Number(q.cantidad) || 0), 0))
function anchoQuimico(q) {
  if (!maxQuimico.value) return '4%'
  return `${Math.max(5, Math.min(100, (Number(q.cantidad) / maxQuimico.value) * 100))}%`
}

/* ---------------- Medidores frenados ---------------- */
const frenados = computed(() => rMM.value?.frenados || [])
const frenadosTotal = computed(() => rMM.value?.frenados_total || 0)

/* Consumo por medidor (nombre de usuario incluido) */
const consumoTotal = computed(() => (rConsumo.value ? Number(rConsumo.value.total) : 0))
const promedioGlobal = computed(() => (rConsumo.value && rConsumo.value.promedio != null ? Number(rConsumo.value.promedio) : null))
const lecturasConsumo = computed(() => (rConsumo.value ? rConsumo.value.lecturas : 0))
const consumoTop = computed(() => rConsumo.value?.por_medidor || [])
const maxConsumo = computed(() => Math.max(...consumoTop.value.map((r) => Number(r.total) || 0), 0))
function alturaConsumo(t) {
  if (!maxConsumo.value) return '4%'
  return `${Math.max(5, Math.min(100, (Number(t) / maxConsumo.value) * 100))}%`
}

/* ---------------- Puntos críticos (para decidir) ---------------- */
const puntosCriticos = computed(() => {
  const out = []
  if (verMedidores.value && frenadosTotal.value) {
    out.push({ icon: 'gauge', texto: `${frenadosTotal.value} medidor(es) frenado(s): requieren revisión en campo`, to: '/micromedidores', tone: 'bad' })
  }
  if (verQuimicos.value && quimicosBajos.value) {
    out.push({ icon: 'flask', texto: `${quimicosBajos.value} químico(s) en planta en mínimo o por debajo`, to: '/planta', tone: 'bad' })
  }
  if (puedePlanta.value && (rPlanta.value?.fuera_rango || []).length) {
    out.push({ icon: 'alert', texto: `${rPlanta.value.fuera_rango.length} parámetro(s) fuera de rango (última medición)`, to: '/planta', tone: 'warn' })
  }
  if (puedeInventario.value && (rInv.value?.alertas || 0)) {
    out.push({ icon: 'inventory', texto: `${rInv.value.alertas} elemento(s) de inventario bajo mínimo`, to: '/inventario', tone: 'warn' })
  }
  return out
})

/* KPIs derivados del resumen (sin estado local: se recalculan al cargar) */
const kpis = computed(() => {
  const out = []
  if (puedeInventario.value && rInv.value) {
    out.push({ label: 'Elementos en inventario', value: rInv.value.elementos, to: '/inventario', icon: 'inventory', sub: esAdministrativo.value ? 'Solo Oficina' : undefined })
    out.push({ label: 'Alertas de existencia', value: rInv.value.alertas, to: '/inventario', icon: 'alert', tone: rInv.value.alertas ? 'bad' : 'ok', sub: rInv.value.alertas ? 'Reponer stock' : 'Stock al día' })
    if (verQuimicos.value) out.push({ label: 'Químicos en planta', value: quimicosTotal.value, to: '/planta', icon: 'flask', tone: quimicosBajos.value ? 'bad' : '', sub: quimicosBajos.value ? `${quimicosBajos.value} en mínimo` : 'Niveles OK' })
  }
  if (verMedidores.value && rMM.value) {
    out.push({ label: 'Suscriptores', value: rMM.value.suscriptores, to: '/micromedidores', icon: 'users' })
    out.push({ label: 'Micromedidores', value: rMM.value.medidores, to: '/micromedidores', icon: 'gauge' })
    out.push({ label: 'Medidores frenados', value: frenadosTotal.value, to: '/micromedidores', icon: 'alert', tone: frenadosTotal.value ? 'bad' : 'ok', sub: frenadosTotal.value ? 'Revisión en campo' : 'Sin frenados' })
  }
  if (verConsumo.value && rConsumo.value) {
    out.push({
      label: `Consumo total micromedición (${periodoConsumo.value}d)`, value: `${fmtNum(consumoTotal.value)} m³`, to: '/micromedidores', icon: 'report',
      sub: promedioGlobal.value !== null ? `Prom. ${fmtNum(promedioGlobal.value)} m³/lectura` : 'Sin lecturas en el periodo',
    })
  }
  if (puedePlanta.value && rPlanta.value) {
    const n = rPlanta.value.fuera_rango.length
    out.push({ label: 'Parámetros fuera de rango', value: n, to: '/planta', icon: 'drop', tone: n ? 'warn' : 'ok', sub: n ? 'Ajustar proceso' : 'Todo en rango' })
  }
  return out
})

/* Cantidad esperada de KPIs según el rol: los skeletons de la fila 1 se
   pintan con este número (6 o menos) para que la grilla no salte al cargar. */
const kpisEsperados = computed(() => {
  if (rol.value === 'admin') return 8
  if (rol.value === 'administrativo') return 6
  if (rol.value === 'operario') return 4
  return 0
})

/* Fila 1: primeros 6 KPIs · Fila 2: el resto (admin: 2) a ancho completo.
   Si hay 6 o menos, una sola fila sin espacios en blanco. */
const tieneDosFilas = computed(() => kpis.value.length > 6)
const kpisFila1 = computed(() => (tieneDosFilas.value ? kpis.value.slice(0, 6) : kpis.value))
const kpisFila2 = computed(() => (tieneDosFilas.value ? kpis.value.slice(6) : []))
const skeletonFila1 = computed(() => Math.min(kpisEsperados.value, 6))

const enlaces = computed(() => {  const map = {
    admin: [['inventario', 'Inventario', 'inventory'], ['micromedidores', 'Micromedidores', 'gauge'], ['planta', 'Planta', 'drop'], ['reportes', 'Reportes', 'report'], ['usuarios', 'Usuarios', 'users']],
    administrativo: [['inventario', 'Inventario', 'inventory'], ['micromedidores', 'Micromedidores', 'gauge'], ['reportes', 'Reportes', 'report']],
    operario: [['planta', 'Planta', 'drop'], ['reportes', 'Reportes', 'report']],
    fontanero: [['micromedidores', 'Lecturas', 'gauge']],
  }
  return map[rol.value] || []
})

function go(to) { router.push(to) }

onMounted(load)
</script>

<template>
  <div class="view-scroll">
    <div class="dash-head">
      <div>
        <h1>Bienvenido, {{ auth.nombre || 'usuario' }}</h1>
        <p class="muted">Rol: <span style="text-transform:capitalize;font-weight:600">{{ rol }}</span> · Acueducto Comunitario Acuaricaurte — Ibagué, Tolima</p>
      </div>
      <button class="btn btn-ghost" @click="load" :disabled="loading"><AppIcon name="refresh" />{{ loading ? 'Cargando…' : 'Actualizar' }}</button>
    </div>

    <BaseAlert v-if="error" type="bad" class="mb-1">{{ error }} <button class="btn btn-ghost btn-sm" @click="load">Reintentar</button></BaseAlert>

    <!-- Puntos críticos para decidir (con esqueleto para no saltar el layout) -->
    <BaseAlert v-if="!loading && puntosCriticos.length" type="warn" class="mb-1">
      <strong>Puntos críticos ({{ puntosCriticos.length }}):</strong>
      <span v-for="(p, i) in puntosCriticos" :key="i">
        <a href="#" @click.prevent="go(p.to)" style="font-weight:600">{{ p.texto }}</a><span v-if="i < puntosCriticos.length - 1"> · </span>
      </span>
    </BaseAlert>
    <BaseAlert v-else-if="!loading" type="ok" class="mb-1">Sin puntos críticos: niveles, medidores y parámetros al día. ✔</BaseAlert>
    <div v-else class="alert alert-warn mb-1" aria-hidden="true"><div class="skeleton-line w75" style="height:.95rem"></div></div>

    <!-- KPIs (esqueletos desde el primer render) -->
    <div v-if="loading" class="kpi-grid kpi-row-1 mt-2 kpi-single" :style="{ '--cols': Math.max(skeletonFila1, 1) }">
      <div v-for="n in Math.max(skeletonFila1, 1)" :key="'kpi-sk' + n" class="kpi kpi-skeleton" aria-hidden="true">
        <div class="skeleton-line w60"></div>
        <div class="skeleton-line value w40"></div>
        <div class="skeleton-line sub w75"></div>
      </div>
    </div>
    <div v-else class="kpi-grid kpi-row-1 mt-2" :class="tieneDosFilas ? 'tiene-2filas' : 'kpi-single'" :style="{ '--cols': kpisFila1.length || 1 }">
      <div class="kpi kpi-click" v-for="k in kpisFila1" :key="k.label" @click="go(k.to)">
        <div class="flex center gap-1">
          <AppIcon :name="k.icon" :size="16" />
          <span class="label">{{ k.label }}</span>
        </div>
        <div class="value" :class="k.tone === 'bad' ? 'bad' : k.tone === 'warn' ? 'warn' : ''">{{ k.value }}</div>
        <div v-if="k.sub" class="kpi-sub">{{ k.sub }}</div>
      </div>
    </div>
    <div v-if="!loading && tieneDosFilas" class="kpi-grid kpi-row-2" :style="{ '--cols': kpisFila2.length || 1 }">
      <div class="kpi kpi-click" v-for="k in kpisFila2" :key="k.label" @click="go(k.to)">
        <div class="flex center gap-1">
          <AppIcon :name="k.icon" :size="16" />
          <span class="label">{{ k.label }}</span>
        </div>
        <div class="value" :class="k.tone === 'bad' ? 'bad' : k.tone === 'warn' ? 'warn' : ''">{{ k.value }}</div>
        <div v-if="k.sub" class="kpi-sub">{{ k.sub }}</div>
      </div>
    </div>

    <div class="dash-grid">
      <!-- 1. Químicos disponibles en planta (no visible para administrativo) -->
      <div v-if="verQuimicos" class="card dash-card">
        <div class="card-head">
          <div class="title"><AppIcon name="flask" /><h3>Químicos en planta</h3>
            <span v-if="!loading && quimicosBajos" class="badge badge-bad">{{ quimicosBajos }} en mínimo</span>
            <span v-else-if="!loading" class="badge badge-ok">Niveles OK</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/planta')">Ver planta</button>
        </div>
        <p class="muted dash-sub" v-if="loading">Cargando resumen de químicos…</p>
        <p v-else class="muted dash-sub">{{ quimicosTotal }} químico(s) en Planta de tratamiento · {{ quimicosBajos }} bajo mínimo</p>
        <div v-if="loading" class="card-skeleton" role="status" aria-live="polite" aria-label="Cargando químicos en planta">
          <p class="skeleton-status"><span class="spinner" aria-hidden="true"></span>Cargando químicos…</p>
          <div v-for="n in 3" :key="'qsk' + n" class="chem-row" aria-hidden="true">
            <div class="chem-top"><div class="skeleton-line w60"></div></div>
            <div class="chem-bar"><div class="skeleton-line w75"></div></div>
            <div class="skeleton-line w40"></div>
          </div>
        </div>
        <div v-else-if="quimicosTop.length" class="chem-list">
          <div v-for="q in quimicosTop" :key="q.id" class="chem-row">
            <div class="chem-top">
              <strong class="chem-name">{{ q.nombre }}</strong>
              <span class="chem-qty">{{ fmtNum(q.cantidad) }} {{ q.unidad || '' }}</span>
              <span v-if="esBajo(q)" class="badge badge-bad">Bajo mínimo</span>
              <span v-else class="badge badge-ok">OK</span>
            </div>
            <div class="chem-bar"><div class="chem-fill" :class="esBajo(q) ? 'is-low' : 'is-ok'" :style="{ width: anchoQuimico(q) }"></div></div>
            <div class="chem-meta muted">Mínimo: {{ q.minimo ?? '—' }} {{ q.unidad || '' }}</div>
          </div>
        </div>
        <p v-else class="muted">Sin químicos con stock en planta.</p>
      </div>

      <!-- 2. Consumo por medidor con nombre de usuario (no visible para fontanero) -->
      <div v-if="verConsumo" class="card dash-card">
        <div class="card-head">
          <div class="title"><AppIcon name="report" /><h3>Consumo por medidor</h3></div>
          <div class="seg">
            <button v-for="d in periodos" :key="d" :class="{ active: periodoConsumo === d }" @click="periodoConsumo = d">{{ d }}d</button>
          </div>
        </div>
        <p class="muted dash-sub" v-if="loading">Cargando resumen de consumo…</p>
        <p v-else class="muted dash-sub">
          Últimos {{ periodoConsumo }} días · Total: <strong>{{ fmtNum(consumoTotal) }} m³</strong>
          · Promedio: <strong>{{ promedioGlobal !== null ? fmtNum(promedioGlobal) + ' m³/lectura' : '—' }}</strong>
          · {{ lecturasConsumo }} lectura(s)
        </p>
        <div v-if="loading" class="cons-chart cons-chart-skeleton" role="status" aria-live="polite" aria-label="Cargando consumo por medidor">
          <p class="skeleton-status"><span class="spinner" aria-hidden="true"></span>Cargando consumo…</p>
          <div v-for="n in 6" :key="'csk' + n" class="cons-col" aria-hidden="true">
            <div class="skeleton-line w40"></div>
            <div class="cons-track"><div class="skeleton-line" style="height:60%"></div></div>
            <div class="skeleton-line w75"></div>
          </div>
        </div>
        <div v-else-if="consumoTop.length" class="cons-bloque">
          <p class="cons-leyenda">Nombre del usuario · <span class="lg-avg">⌀ promedio por lectura</span> · <span class="lg-med"># serial del medidor</span></p>
          <div class="cons-chart">
            <div v-for="r in consumoTop" :key="r.micromedidor_id" class="cons-col" :title="`${r.serial} · Total ${fmtNum(r.total)} m³ · Prom. ${fmtNum(r.promedio)} m³ (${r.lecturas} lecturas) · ${r.suscriptor || 'Sin suscriptor'}`">
              <span class="cons-val">{{ fmtNum(r.total) }}</span>
              <div class="cons-track"><div class="cons-fill" :style="{ height: alturaConsumo(r.total) }"></div></div>
              <span class="cons-label" :title="r.suscriptor || r.serial">{{ r.suscriptor || '#' + r.serial }}</span>
              <span class="cons-sub" :title="`Promedio por lectura: ${fmtNum(r.promedio)} m³`">⌀ {{ fmtNum(r.promedio) }} m³</span>
              <span class="cons-med" :title="`Serial del medidor: ${r.serial}`">#{{ r.serial }}</span>
            </div>
          </div>
        </div>
        <p v-else class="muted">Sin consumos registrados en los últimos {{ periodoConsumo }} días.</p>
        <div class="dash-foot">
          <button class="btn btn-ghost btn-sm" @click="go('/micromedidores')">Ver lecturas</button>
        </div>
      </div>

      <!-- 3. Medidores frenados (no visible para operario) -->
      <div v-if="verMedidores" class="card dash-card dash-alert" :class="{ 'is-critical': !loading && frenadosTotal }">
        <div class="card-head">
          <div class="title"><AppIcon name="gauge" /><h3>Medidores frenados</h3>
            <span v-if="!loading" class="badge" :class="frenadosTotal ? 'badge-bad' : 'badge-ok'">{{ frenadosTotal }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/micromedidores')">Ver medidores</button>
        </div>
        <p class="muted dash-sub">Contador detenido (3 lecturas idénticas seguidas). Requieren visita en campo.</p>
        <div v-if="loading" class="card-skeleton" role="status" aria-live="polite" aria-label="Cargando medidores frenados">
          <p class="skeleton-status"><span class="spinner" aria-hidden="true"></span>Cargando medidores…</p>
          <div v-for="n in 3" :key="'fsk' + n" class="fren-row" aria-hidden="true">
            <div class="skeleton-dot"></div>
            <div class="skeleton-line w75"></div>
            <div class="skeleton-line w40"></div>
          </div>
        </div>
        <div v-else-if="frenados.length" class="fren-list">
          <div v-for="m in frenados" :key="m.id" class="fren-row">
            <span class="fren-dot"></span>
            <div class="fren-info">
              <strong>{{ m.serial }}</strong>
              <span class="muted">{{ m.suscriptor || 'Sin suscriptor' }}<span v-if="m.sector"> · {{ m.sector }}</span></span>
            </div>
            <span class="badge badge-bad">Frenado</span>
          </div>
          <p v-if="frenadosTotal > 5" class="muted">+ {{ frenadosTotal - 5 }} más…</p>
        </div>
        <BaseAlert v-else type="ok" class="mb-1">Ningún medidor frenado. ✔</BaseAlert>
      </div>

      <!-- Fuera de rango (contexto crítico) -->
      <div v-if="puedePlanta" class="card dash-card" :class="{ 'is-critical': !loading && (rPlanta?.fuera_rango || []).length }">
        <div class="card-head">
          <div class="title"><AppIcon name="drop" /><h3>Fuera de rango</h3>
            <span v-if="!loading" class="badge" :class="(rPlanta?.fuera_rango || []).length ? 'badge-warn' : 'badge-ok'">{{ (rPlanta?.fuera_rango || []).length }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/planta')">Ver planta</button>
        </div>
        <p class="muted dash-sub">Parámetros cuya última medición está fuera de rango.</p>
        <div v-if="loading" class="card-skeleton" role="status" aria-live="polite" aria-label="Cargando parámetros fuera de rango">
          <p class="skeleton-status"><span class="spinner" aria-hidden="true"></span>Cargando parámetros…</p>
          <div v-for="n in 3" :key="'rsk' + n" class="fren-row" aria-hidden="true">
            <div class="skeleton-dot"></div>
            <div class="skeleton-line w75"></div>
            <div class="skeleton-line w40"></div>
          </div>
        </div>
        <div v-else-if="(rPlanta?.fuera_rango || []).length" class="fren-list">
          <div v-for="r in (rPlanta?.fuera_rango || []).slice(0, 5)" :key="r.parametro_id || r.parametro" class="fren-row">
            <span class="fren-dot warn"></span>
            <div class="fren-info">
              <strong>{{ r.parametro }}</strong>
              <span class="muted">{{ fmtNum(r.valor) }} {{ r.unidad || '' }} · rango {{ fmtRango(r.valor_min, r.valor_max) }}</span>
            </div>
            <span class="badge badge-warn">Ajustar</span>
          </div>
        </div>
        <BaseAlert v-else type="ok" class="mb-1">Todos los parámetros en rango. ✔</BaseAlert>
      </div>
    </div>

    <!-- Horas de servicio: mismo gráfico navegable de Planta (anual → mes → semana) -->
    <div v-if="puedePlanta" class="card dash-card" style="margin-bottom:1.2rem">
      <div class="card-head">
        <div class="title"><AppIcon name="clock" /><h3>Horas de servicio</h3></div>
        <button class="btn btn-ghost btn-sm" @click="go('/planta')">Ver planta</button>
      </div>
      <GraficoHoras texto-accion-dia="Clic para abrir planta." @click-dia="go('/planta')" />
    </div>

    <div class="card">
      <div class="card-head">
        <div class="title"><AppIcon name="dashboard" /><h3>Accesos rápidos</h3></div>
      </div>
      <div class="flex wrap gap-1">
        <button v-for="[to, label, icon] in enlaces" :key="to" class="btn btn-ghost" @click="go('/' + to)">
          <AppIcon :name="icon" /> {{ label }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dash-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.kpi-click { cursor: pointer; transition: transform .12s, box-shadow .12s; }
.kpi-click:hover { transform: translateY(-1px); box-shadow: var(--acr-sombra); }
.kpi-sub { font-size: .75rem; color: var(--acr-texto-suave); margin-top: .15rem; }
/* KPIs: fila 1 = 6 a ancho completo · fila 2 = el resto (admin: 2) a ancho completo (sin huecos) */
.kpi-row-1, .kpi-row-2 { grid-template-columns: repeat(var(--cols, 6), minmax(0, 1fr)); }
.kpi-row-2 { margin-top: 0; }
@media (max-width: 1200px) {
  .kpi-row-1.tiene-2filas { grid-template-columns: repeat(3, minmax(0, 1fr)); } /* 6 → 3+3 */
  .kpi-row-1.kpi-single { grid-template-columns: repeat(2, minmax(0, 1fr)); } /* 4 → 2+2 */
}
@media (max-width: 768px) {
  .kpi-row-1.tiene-2filas { grid-template-columns: repeat(2, minmax(0, 1fr)); } /* 6 → 3 filas exactas */
}
@media (max-width: 480px) {
  .kpi-row-1, .kpi-row-2 { grid-template-columns: minmax(0, 1fr); }
}
.dash-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin: 1.2rem 0; }
/* Si una card queda sola en su fila (conteo impar), ocupa todo el ancho: sin huecos */
.dash-grid > :last-child:nth-child(odd) { grid-column: 1 / -1; }
@media (max-width: 900px) {
  .dash-grid { grid-template-columns: minmax(0, 1fr); }
}
.dash-card { border-top: 3px solid var(--acr-azul); }
.dash-card.is-critical { border-top-color: var(--acr-bad); }
.dash-sub { font-size: .82rem; margin: 0 0 .7rem; }
.dash-foot { margin-top: .8rem; display: flex; justify-content: flex-end; }

/* Químicos */
.chem-list { display: flex; flex-direction: column; gap: .65rem; }
.chem-row { border: 1px solid var(--acr-borde); border-radius: 8px; padding: .55rem .65rem; background: #FBFDFF; }
.chem-top { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.chem-name { flex: 1; min-width: 120px; }
.chem-qty { font-variant-numeric: tabular-nums; font-weight: 700; color: var(--acr-azul-700); }
.chem-bar { height: 8px; background: #EDF2F9; border-radius: 999px; margin-top: .45rem; overflow: hidden; }
.chem-fill { height: 100%; border-radius: 999px; }
.chem-fill.is-ok { background: linear-gradient(90deg, #2E9E5B, #5CC184); }
.chem-fill.is-low { background: linear-gradient(90deg, #D64545, #F08080); }
.chem-meta { font-size: .72rem; margin-top: .25rem; }

/* Consumo por medidor */
.seg { display: inline-flex; border: 1px solid var(--acr-borde); border-radius: 999px; overflow: hidden; }
.seg button { border: none; background: #fff; padding: .3rem .7rem; font-size: .78rem; font-weight: 700; cursor: pointer; color: var(--acr-texto-suave); font-family: inherit; }
.seg button.active { background: var(--acr-azul); color: #fff; }
.cons-leyenda { font-size: .72rem; color: var(--acr-texto-suave); margin: 0 0 .45rem; }
.cons-leyenda .lg-avg { color: var(--acr-azul-700); font-weight: 700; }
.cons-leyenda .lg-med { color: var(--acr-texto-suave); font-weight: 700; }
.cons-bloque { min-width: 0; }
.cons-chart { display: flex; align-items: flex-end; gap: .55rem; min-height: 220px; border-bottom: 2px solid var(--acr-borde); padding-bottom: .5rem; overflow-x: auto; }
/* Cada columna es un contenedor propio: los textos se recortan DENTRO de su
   columna (display:block + min-width:0) y ya no se sobreponen entre barras */
.cons-col { flex: 1 0 0; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: .2rem; }
.cons-val { font-size: .72rem; font-weight: 800; color: var(--acr-azul-700); font-variant-numeric: tabular-nums; }
.cons-track { width: 100%; max-width: 52px; height: 140px; background: #EDF2F9; border: 1px solid var(--acr-borde); border-radius: 8px 8px 4px 4px; display: flex; align-items: flex-end; overflow: hidden; }
.cons-fill { width: 100%; background: linear-gradient(180deg, #3A7BD0 0%, var(--acr-azul) 100%); border-radius: 7px 7px 0 0; min-height: 4px; }
/* Nombre del usuario: 1 línea, recortado con "…" y título completo al pasar el mouse */
.cons-label { display: block; max-width: 100%; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .68rem; font-weight: 700; }
/* Línea de promedio (azul) y línea del serial del medidor (gris), separadas */
.cons-sub { display: block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .66rem; font-weight: 700; color: var(--acr-azul-700); font-variant-numeric: tabular-nums; }
.cons-med { display: block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .62rem; color: var(--acr-texto-suave); font-variant-numeric: tabular-nums; }

/* Listas críticas */
.fren-list { display: flex; flex-direction: column; gap: .5rem; }
.fren-row { display: flex; align-items: center; gap: .6rem; border: 1px solid var(--acr-borde); border-radius: 8px; padding: .5rem .65rem; background: #fff; }
.fren-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.fren-info span { font-size: .78rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fren-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--acr-bad); flex: none; box-shadow: 0 0 0 3px var(--acr-bad-bg); }
.fren-dot.warn { background: var(--acr-warn); box-shadow: 0 0 0 3px var(--acr-warn-bg); }

/* Skeletons de carga */
.skeleton-line { height: .85rem; border-radius: 5px; background: var(--acr-gris, #EAF1FB); animation: skeleton-pulse 1.4s ease-in-out infinite; }
.skeleton-line.value { height: 1.7rem; }
.skeleton-line.sub { height: .7rem; }
.skeleton-line.w40 { width: 40%; }
.skeleton-line.w60 { width: 60%; }
.skeleton-line.w75 { width: 75%; }
.skeleton-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--acr-gris, #EAF1FB); flex: none; animation: skeleton-pulse 1.4s ease-in-out infinite; }
.kpi-skeleton { pointer-events: none; }
.card-skeleton { display: flex; flex-direction: column; gap: .65rem; }
.skeleton-status { display: flex; align-items: center; gap: .6rem; color: var(--acr-azul); font-size: .85rem; margin: 0 0 .4rem; }
.skeleton-status .spinner { width: 18px; height: 18px; margin: 0; border-width: 2px; }
.cons-chart-skeleton { align-items: center; }
.cons-chart-skeleton .skeleton-status { width: 100%; }
.cons-chart-skeleton .cons-track { align-items: center; justify-content: center; }
.cons-chart-skeleton .skeleton-line { width: 80%; height: 60%; border-radius: 6px; }
@keyframes skeleton-pulse { 50% { opacity: .4; } }
@media (prefers-reduced-motion: reduce) {
  .skeleton-line, .skeleton-dot, .skeleton-status .spinner { animation: none; }
}
</style>
