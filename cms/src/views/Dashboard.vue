<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useInventarioStore } from '../stores/inventario'
import { useMicromedidoresStore } from '../stores/micromedidores'
import { usePlantaStore } from '../stores/planta'
import AppIcon from '../components/AppIcon.vue'
import BaseAlert from '../components/BaseAlert.vue'
import GraficoHoras from '../components/GraficoHoras.vue'
import { fmtNum, fmtRango } from '../utils/format'

const auth = useAuthStore()
const router = useRouter()
const inv = useInventarioStore()
const mm = useMicromedidoresStore()
const planta = usePlantaStore()

const kpis = ref([])
const loading = ref(false)
const rol = computed(() => auth.rol)
const puedeInventario = computed(() => ['admin', 'administrativo', 'operario'].includes(rol.value))
const puedeMM = computed(() => ['admin', 'administrativo', 'operario', 'fontanero'].includes(rol.value))
const puedePlanta = computed(() => ['admin', 'operario'].includes(rol.value))
const esAdministrativo = computed(() => rol.value === 'administrativo')
const esFontanero = computed(() => rol.value === 'fontanero')
const esOperario = computed(() => rol.value === 'operario')
/* Visibilidad fina por rol:
   - administrativo: inventario/alertas solo Oficina; químicos NO ve nada.
   - fontanero y operario: sin consumo (ni total ni por medidor).
   - operario: sin suscriptores/medidores/frenados. */
const verQuimicos = computed(() => puedeInventario.value && !esAdministrativo.value)
const verConsumo = computed(() => puedeMM.value && !esFontanero.value && !esOperario.value)
const verMedidores = computed(() => puedeMM.value && !esOperario.value)

/* Periodo del gráfico de consumo (días hacia atrás desde hoy Colombia) */
const periodoConsumo = ref(60)
const periodos = [30, 60, 90]
function isoHaceDias(n) {
  const d = new Date()
  d.setDate(d.getDate() - (Number(n) - 1))
  return d.toISOString().slice(0, 10)
}

async function load() {
  loading.value = true
  const tareas = []
  if (puedeInventario.value) {
    tareas.push(inv.loadElementos(), inv.loadAlertas())
    if (verQuimicos.value) tareas.push(inv.loadQuimicos(), inv.loadUbicaciones())
  }
  if (puedeMM.value) {
    tareas.push(mm.loadSuscriptores(), mm.loadMicromedidores())
    if (verConsumo.value) tareas.push(mm.loadLecturas({ fecha_inicio: isoHaceDias(periodoConsumo.value) }))
  }
  if (puedePlanta.value) {
    tareas.push(planta.loadFueraRango())
  }
  await Promise.allSettled(tareas)
  buildKpis()
  loading.value = false
}

watch(periodoConsumo, async () => {
  if (!verConsumo.value) return
  await mm.loadLecturas({ fecha_inicio: isoHaceDias(periodoConsumo.value) })
  buildKpis()
})

/* ---------------- Mapas base ---------------- */
const susMap = computed(() => Object.fromEntries(mm.suscriptores.map((s) => [s.id, s.nombre])))
const susSector = computed(() => Object.fromEntries(mm.suscriptores.map((s) => [s.id, s.sector])))
const mmSerial = computed(() => Object.fromEntries(mm.micromedidores.map((m) => [m.id, m.serial])))

/* ---------------- Químicos en planta (conciso) ---------------- */
const plantaUbi = computed(() => (inv.ubicaciones || []).find((u) => /planta/i.test(u.nombre || '')) || null)
const quimicosPlanta = computed(() => {
  if (!plantaUbi.value) return []
  return (inv.quimicos || [])
    .map((q) => {
      const fila = (q.stock || []).find((s) => s.ubicacion_id === plantaUbi.value.id)
      return fila ? { ...q, cantidad: fila.cantidad } : null
    })
    .filter(Boolean)
})
const esBajo = (q) => q.minimo != null && q.minimo !== '' && Number(q.cantidad) <= Number(q.minimo)
const quimicosBajos = computed(() => quimicosPlanta.value.filter(esBajo).length)
const quimicosTop = computed(() => quimicosPlanta.value
  .slice()
  .sort((a, b) => {
    const ba = esBajo(a) ? 0 : 1
    const bb = esBajo(b) ? 0 : 1
    if (ba !== bb) return ba - bb
    const ra = a.minimo ? Number(a.cantidad) / Number(a.minimo || 1) : Number(a.cantidad)
    const rb = b.minimo ? Number(b.cantidad) / Number(b.minimo || 1) : Number(b.cantidad)
    return ra - rb
  })
  .slice(0, 6))
const maxQuimico = computed(() => Math.max(...quimicosPlanta.value.map((q) => Number(q.cantidad) || 0), 0))
function anchoQuimico(q) {
  if (!maxQuimico.value) return '4%'
  return `${Math.max(5, Math.min(100, (Number(q.cantidad) / maxQuimico.value) * 100))}%`
}

/* ---------------- Medidores frenados ---------------- */
const frenados = computed(() => (mm.micromedidores || []).filter((m) => m.condicion === 'frenado'))
const frenadosTop = computed(() => frenados.value.slice(0, 5))

/* ---------------- Consumo total / promedio por medidor ---------------- */
const lecturasValidas = computed(() => (mm.lecturas || []).filter((l) => l.consumo !== null && l.consumo !== undefined && l.consumo !== ''))
const consumoTotal = computed(() => lecturasValidas.value.reduce((t, l) => t + Number(l.consumo || 0), 0))
const promedioGlobal = computed(() => (lecturasValidas.value.length ? consumoTotal.value / lecturasValidas.value.length : null))
const consumoPorMedidor = computed(() => {
  const map = {}
  for (const l of lecturasValidas.value) {
    const id = l.micromedidor_id
    const cur = map[id] || { id, total: 0, n: 0 }
    cur.total += Number(l.consumo || 0)
    cur.n += 1
    map[id] = cur
  }
  return Object.values(map)
    .map((r) => ({
      ...r,
      promedio: r.n ? r.total / r.n : null,
      serial: mmSerial.value[r.id] || `#${r.id}`,
      suscriptor: susMap.value[mm.micromedidores.find((m) => m.id === r.id)?.suscriptor_id] || '—',
    }))
    .sort((a, b) => b.total - a.total)
})
const consumoTop = computed(() => consumoPorMedidor.value.slice(0, 8))
const maxConsumo = computed(() => Math.max(...consumoTop.value.map((r) => r.total), 0))
function alturaConsumo(t) {
  if (!maxConsumo.value) return '4%'
  return `${Math.max(5, Math.min(100, (Number(t) / maxConsumo.value) * 100))}%`
}
function serialCorto(s) {
  const t = String(s || '')
  return t.length > 10 ? `…${t.slice(-8)}` : t
}

/* ---------------- Puntos críticos (para decidir) ---------------- */
const puntosCriticos = computed(() => {
  const out = []
  if (puedeMM.value && frenados.value.length && verMedidores.value) {
    out.push({ icon: 'gauge', texto: `${frenados.value.length} medidor(es) frenado(s): requieren revisión en campo`, to: '/micromedidores', tone: 'bad' })
  }
  if (verQuimicos.value && quimicosBajos.value) {
    out.push({ icon: 'flask', texto: `${quimicosBajos.value} químico(s) en planta en mínimo o por debajo`, to: '/planta', tone: 'bad' })
  }
  if (puedePlanta.value && planta.fueraRango.length) {
    out.push({ icon: 'alert', texto: `${planta.fueraRango.length} parámetro(s) fuera de rango (última medición)`, to: '/planta', tone: 'warn' })
  }
  if (puedeInventario.value && inv.alertas.length) {
    out.push({ icon: 'inventory', texto: `${inv.alertas.length} elemento(s) de inventario bajo mínimo`, to: '/inventario', tone: 'warn' })
  }
  return out
})

function buildKpis() {
  const out = []
  if (puedeInventario.value) {
    out.push({ label: 'Elementos en inventario', value: inv.elementos.length, to: '/inventario', icon: 'inventory', sub: esAdministrativo.value ? 'Solo Oficina' : undefined })
    out.push({ label: 'Alertas de existencia', value: inv.alertas.length, to: '/inventario', icon: 'alert', tone: inv.alertas.length ? 'bad' : 'ok', sub: inv.alertas.length ? 'Reponer stock' : 'Stock al día' })
    if (verQuimicos.value) out.push({ label: 'Químicos en planta', value: quimicosPlanta.value.length, to: '/planta', icon: 'flask', tone: quimicosBajos.value ? 'bad' : '', sub: quimicosBajos.value ? `${quimicosBajos.value} en mínimo` : 'Niveles OK' })
  }
  if (verMedidores.value) {
    out.push({ label: 'Suscriptores', value: mm.suscriptores.length, to: '/micromedidores', icon: 'users' })
    out.push({ label: 'Micromedidores', value: mm.micromedidores.length, to: '/micromedidores', icon: 'gauge' })
    out.push({ label: 'Medidores frenados', value: frenados.value.length, to: '/micromedidores', icon: 'alert', tone: frenados.value.length ? 'bad' : 'ok', sub: frenados.value.length ? 'Revisión en campo' : 'Sin frenados' })
  }
  if (verConsumo.value) {
    out.push({
      label: `Consumo total micromedición (${periodoConsumo.value}d)`, value: `${fmtNum(consumoTotal.value)} m³`, to: '/micromedidores', icon: 'report',
      sub: promedioGlobal.value !== null ? `Prom. ${fmtNum(promedioGlobal.value)} m³/lectura` : 'Sin lecturas en el periodo',
    })
  }
  if (puedePlanta.value) {
    out.push({ label: 'Parámetros fuera de rango', value: planta.fueraRango.length, to: '/planta', icon: 'drop', tone: planta.fueraRango.length ? 'warn' : 'ok', sub: planta.fueraRango.length ? 'Ajustar proceso' : 'Todo en rango' })
  }
  kpis.value = out
}

/* Fila 1: primeros 6 KPIs · Fila 2: el resto (admin: 2) a ancho completo.
   Si hay 6 o menos, una sola fila sin espacios en blanco. */
const tieneDosFilas = computed(() => kpis.value.length > 6)
const kpisFila1 = computed(() => (tieneDosFilas.value ? kpis.value.slice(0, 6) : kpis.value))
const kpisFila2 = computed(() => (tieneDosFilas.value ? kpis.value.slice(6) : []))

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

    <!-- Puntos críticos para decidir -->
    <BaseAlert v-if="puntosCriticos.length" type="warn" class="mb-1">
      <strong>Puntos críticos ({{ puntosCriticos.length }}):</strong>
      <span v-for="(p, i) in puntosCriticos" :key="i">
        <a href="#" @click.prevent="go(p.to)" style="font-weight:600">{{ p.texto }}</a><span v-if="i < puntosCriticos.length - 1"> · </span>
      </span>
    </BaseAlert>
    <BaseAlert v-else-if="!loading" type="ok" class="mb-1">Sin puntos críticos: niveles, medidores y parámetros al día. ✔</BaseAlert>

    <div class="kpi-grid kpi-row-1 mt-2" :class="tieneDosFilas ? 'tiene-2filas' : 'kpi-single'" :style="{ '--cols': kpisFila1.length || 1 }">
      <div class="kpi kpi-click" v-for="k in kpisFila1" :key="k.label" @click="go(k.to)">
        <div class="flex center gap-1">
          <AppIcon :name="k.icon" :size="16" />
          <span class="label">{{ k.label }}</span>
        </div>
        <div class="value" :class="k.tone === 'bad' ? 'bad' : k.tone === 'warn' ? 'warn' : ''">{{ k.value }}</div>
        <div v-if="k.sub" class="kpi-sub">{{ k.sub }}</div>
      </div>
    </div>
    <div v-if="tieneDosFilas" class="kpi-grid kpi-row-2" :style="{ '--cols': kpisFila2.length || 1 }">
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
            <span v-if="quimicosBajos" class="badge badge-bad">{{ quimicosBajos }} en mínimo</span>
            <span v-else class="badge badge-ok">Niveles OK</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/planta')">Ver planta</button>
        </div>
        <p v-if="!plantaUbi" class="muted">No se encontró la ubicación «Planta de tratamiento».</p>
        <p v-else class="muted dash-sub">{{ quimicosPlanta.length }} químico(s) en {{ plantaUbi.nombre }} · {{ quimicosBajos }} bajo mínimo</p>
        <div v-if="quimicosTop.length" class="chem-list">
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

      <!-- 2. Consumo total / promedio por medidor (no visible para fontanero) -->
      <div v-if="verConsumo" class="card dash-card">
        <div class="card-head">
          <div class="title"><AppIcon name="report" /><h3>Consumo por medidor</h3></div>
          <div class="seg">
            <button v-for="d in periodos" :key="d" :class="{ active: periodoConsumo === d }" @click="periodoConsumo = d">{{ d }}d</button>
          </div>
        </div>
        <p class="muted dash-sub">
          Últimos {{ periodoConsumo }} días · Total: <strong>{{ fmtNum(consumoTotal) }} m³</strong>
          · Promedio: <strong>{{ promedioGlobal !== null ? fmtNum(promedioGlobal) + ' m³/lectura' : '—' }}</strong>
          · {{ lecturasValidas.length }} lectura(s)
        </p>
        <div v-if="consumoTop.length" class="cons-chart">
          <div v-for="r in consumoTop" :key="r.id" class="cons-col" :title="`${r.serial} · Total ${fmtNum(r.total)} m³ · Prom. ${fmtNum(r.promedio)} m³ (${r.n} lecturas) · ${r.suscriptor}`">
            <span class="cons-val">{{ fmtNum(r.total) }}</span>
            <div class="cons-track"><div class="cons-fill" :style="{ height: alturaConsumo(r.total) }"></div></div>
            <span class="cons-label">{{ serialCorto(r.serial) }}</span>
            <span class="cons-sub">⌀ {{ fmtNum(r.promedio) }}</span>
          </div>
        </div>
        <p v-else class="muted">Sin consumos registrados en los últimos {{ periodoConsumo }} días.</p>
        <div class="dash-foot">
          <button class="btn btn-ghost btn-sm" @click="go('/micromedidores')">Ver lecturas</button>
        </div>
      </div>

      <!-- 3. Medidores frenados (no visible para operario) -->
      <div v-if="verMedidores" class="card dash-card dash-alert" :class="{ 'is-critical': frenados.length }">
        <div class="card-head">
          <div class="title"><AppIcon name="gauge" /><h3>Medidores frenados</h3>
            <span class="badge" :class="frenados.length ? 'badge-bad' : 'badge-ok'">{{ frenados.length }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/micromedidores')">Ver medidores</button>
        </div>
        <p class="muted dash-sub">Contador detenido (3 lecturas idénticas seguidas). Requieren visita en campo.</p>
        <div v-if="frenadosTop.length" class="fren-list">
          <div v-for="m in frenadosTop" :key="m.id" class="fren-row">
            <span class="fren-dot"></span>
            <div class="fren-info">
              <strong>{{ m.serial }}</strong>
              <span class="muted">{{ susMap[m.suscriptor_id] || 'Sin suscriptor' }}<span v-if="susSector[m.suscriptor_id]"> · {{ susSector[m.suscriptor_id] }}</span></span>
            </div>
            <span class="badge badge-bad">Frenado</span>
          </div>
          <p v-if="frenados.length > 5" class="muted">+ {{ frenados.length - 5 }} más…</p>
        </div>
        <BaseAlert v-else type="ok" class="mb-1">Ningún medidor frenado. ✔</BaseAlert>
      </div>

      <!-- Fuera de rango (contexto crítico) -->
      <div v-if="puedePlanta" class="card dash-card" :class="{ 'is-critical': planta.fueraRango.length }">
        <div class="card-head">
          <div class="title"><AppIcon name="drop" /><h3>Fuera de rango</h3>
            <span class="badge" :class="planta.fueraRango.length ? 'badge-warn' : 'badge-ok'">{{ planta.fueraRango.length }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="go('/planta')">Ver planta</button>
        </div>
        <p class="muted dash-sub">Parámetros cuya última medición está fuera de rango.</p>
        <div v-if="planta.fueraRango.length" class="fren-list">
          <div v-for="r in planta.fueraRango.slice(0, 5)" :key="r.parametro_id || r.parametro" class="fren-row">
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
/* KPIs: fila 1 = 6 a ancho completo · fila 2 = el resto a ancho completo (sin huecos) */
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
.cons-chart { display: flex; align-items: flex-end; gap: .55rem; min-height: 220px; border-bottom: 2px solid var(--acr-borde); padding-bottom: .5rem; overflow-x: auto; }
.cons-col { flex: 1; min-width: 62px; display: flex; flex-direction: column; align-items: center; gap: .2rem; }
.cons-val { font-size: .72rem; font-weight: 800; color: var(--acr-azul-700); font-variant-numeric: tabular-nums; }
.cons-track { width: 100%; max-width: 52px; height: 140px; background: #EDF2F9; border: 1px solid var(--acr-borde); border-radius: 8px 8px 4px 4px; display: flex; align-items: flex-end; overflow: hidden; }
.cons-fill { width: 100%; background: linear-gradient(180deg, #3A7BD0 0%, var(--acr-azul) 100%); border-radius: 7px 7px 0 0; min-height: 4px; }
.cons-label { font-size: .7rem; font-weight: 700; max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cons-sub { font-size: .68rem; color: var(--acr-texto-suave); font-variant-numeric: tabular-nums; }

/* Listas críticas */
.fren-list { display: flex; flex-direction: column; gap: .5rem; }
.fren-row { display: flex; align-items: center; gap: .6rem; border: 1px solid var(--acr-borde); border-radius: 8px; padding: .5rem .65rem; background: #fff; }
.fren-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.fren-info span { font-size: .78rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fren-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--acr-bad); flex: none; box-shadow: 0 0 0 3px var(--acr-bad-bg); }
.fren-dot.warn { background: var(--acr-warn); box-shadow: 0 0 0 3px var(--acr-warn-bg); }
</style>
