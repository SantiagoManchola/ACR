<script setup>
import { computed } from 'vue'

const props = defineProps({
  resultado: { type: Object, required: true },
})
const emit = defineEmits(['descargar-novedades', 'descargar-auditoria'])

const titulos = {
  usuario_no_encontrado: 'Filas del archivo sin suscriptor en ACR',
  coincidencia_por_codruta: 'Coincidencias realizadas por código de ruta',
  nombre_diferente: 'Nombre del archivo diferente al nombre en ACR',
  codruta_diferente: 'Código de ruta diferente al registro ACR',
  area_repetida: 'Códigos de área repetidos en la plantilla',
  suscriptor_inactivo: 'Suscriptores inactivos en ACR presentes en el archivo',
  serial_otro_suscriptor: 'Serial del Excel asociado a otro suscriptor',
  serial_no_en_db: 'Serial del Excel no registrado en ACR',
  nmedidor_vacio_excel: 'Medidor en ACR, pero sin serial en el Excel',
  serial_diferente_db: 'Se usó el medidor asociado en ACR; serial distinto',
  multiples_medidores: 'Más de un medidor posible para la cuenta',
  multiples_medidores_inactivos: 'Varios medidores sin serial para elegir',
  medidor_excel_sin_asociacion: 'Medidor del Excel sin asociación en ACR',
  medidor_inactivo_db: 'Medidor inactivo en ACR',
  sin_lectura_en_periodo: 'Medidor sin lectura en el rango elegido',
  varias_lecturas_periodo: 'Varias lecturas en el rango; se eligió la última',
  lectura_estimada_db: 'Lectura estimada registrada en ACR',
  lectura_irregular_db: 'Lectura irregular registrada en ACR',
  historial_insuficiente_formula: 'Sin dos meses previos para estimar',
  valor_mes_difiere: 'El Excel ya traía un valor distinto en el mes',
  sin_resultado: 'Fila sin resultado automático',
}

const grupos = computed(() => {
  const mapa = new Map()
  for (const n of props.resultado.novedades || []) {
    if (!mapa.has(n.tipo)) mapa.set(n.tipo, [])
    mapa.get(n.tipo).push(n)
  }
  return [...mapa.entries()].map(([tipo, filas]) => ({
    tipo,
    titulo: titulos[tipo] || tipo.replaceAll('_', ' '),
    filas,
  }))
})
</script>

<template>
  <section class="fact-resultado" aria-live="polite">
    <h2>Resultado de la revisión</h2>
    <p class="muted">Hoja «{{ resultado.resumen.hoja }}» · {{ resultado.resumen.mes_nombre }} {{ resultado.resumen.anio }} · Lecturas {{ resultado.resumen.fecha_desde }} a {{ resultado.resumen.fecha_hasta }}</p>

    <div class="fact-kpis">
      <article><strong>{{ resultado.resumen.filas_total }}</strong><span>filas del archivo</span></article>
      <article><strong>{{ resultado.resumen.filas_con_lectura_db }}</strong><span>valores desde lecturas ACR</span></article>
      <article><strong>{{ resultado.resumen.filas_formula }}</strong><span>estimaciones por fórmula</span></article>
      <article><strong>{{ resultado.resumen.filas_pendientes }}</strong><span>filas pendientes de resolver</span></article>
    </div>

    <div v-if="resultado.resumen.celdas_mes_con_datos" class="fact-aviso">
      La columna <strong>{{ resultado.resumen.mes_nombre }}</strong> ya tiene
      <strong>{{ resultado.resumen.celdas_mes_con_datos }}</strong> celdas con un valor distinto de cero.
      Las celdas en 0 o vacías se completan sin confirmación. El original no se modifica;
      al generar la copia se reemplazará esa columna si lo confirmas.
    </div>

    <div class="fact-resultado-acciones">
      <button class="btn btn-ghost btn-sm" type="button" @click="emit('descargar-auditoria')">
        Descargar detalle de filas y origen del valor
      </button>
      <button v-if="grupos.length" class="btn btn-ghost btn-sm" type="button" @click="emit('descargar-novedades')">
        Descargar novedades ({{ resultado.novedades.length }})
      </button>
    </div>

    <div v-if="!grupos.length" class="fact-sin-novedades">
      No se encontraron novedades; revisa el resumen y genera el archivo cuando estés listo.
    </div>
    <div v-else class="fact-grupos">
      <section v-for="g in grupos" :key="g.tipo" class="fact-grupo">
        <h3>{{ g.titulo }} <span class="fact-contador">{{ g.filas.length }}</span></h3>
        <div class="fact-tabla-scroll">
          <table class="fact-tabla">
            <thead>
              <tr>
                <th>Fila</th><th>Área</th><th>Usuario del Excel</th>
                <th>nmedidor Excel</th><th>Medidor ACR</th><th>Detalle</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="n in g.filas" :key="`${n.tipo}-${n.fila}`">
                <td>{{ n.fila }}</td>
                <td>{{ n.area || '—' }}</td>
                <td>{{ n.nombre_excel || '—' }}</td>
                <td>{{ n.nmedidor_excel ?? '—' }}</td>
                <td>{{ n.serial_db || '—' }}</td>
                <td>{{ n.detalle }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.fact-resultado { margin-top: 1.25rem; }
.fact-resultado h2 { margin: 0 0 .25rem; font-size: 1.12rem; }
.fact-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: .6rem; margin: .8rem 0; }
.fact-kpis article { display: flex; flex-direction: column; gap: .15rem; border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm); background: #fff; padding: .7rem .8rem; }
.fact-kpis strong { color: var(--acr-azul-700); font-size: 1.2rem; }
.fact-kpis span { color: var(--acr-texto-suave); font-size: .78rem; }
.fact-aviso { border: 1px solid #e8bd5a; background: #fff8e4; color: #72520b; border-radius: var(--acr-radio-sm); padding: .65rem .8rem; margin: .7rem 0; font-size: .88rem; }
.fact-resultado-acciones { display: flex; flex-wrap: wrap; gap: .5rem; margin: .7rem 0; }
.fact-sin-novedades { background: #eff8f1; color: #23613b; border-radius: var(--acr-radio-sm); padding: .75rem; margin-top: .7rem; }
.fact-grupos { display: grid; gap: .8rem; margin-top: .8rem; }
.fact-grupo { border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm); background: #fff; overflow: hidden; }
.fact-grupo h3 { display: flex; align-items: center; gap: .5rem; margin: 0; padding: .65rem .8rem; background: #f4f8fd; font-size: .9rem; }
.fact-contador { display: inline-grid; place-items: center; min-width: 1.45rem; height: 1.45rem; padding: 0 .25rem; border-radius: 99px; background: #e7eef9; color: var(--acr-azul-700); font-size: .75rem; }
.fact-tabla-scroll { max-height: 300px; overflow: auto; }
.fact-tabla { border-collapse: collapse; width: 100%; font-size: .78rem; }
.fact-tabla th, .fact-tabla td { text-align: left; padding: .45rem .55rem; border-bottom: 1px solid #e9eff6; vertical-align: top; }
.fact-tabla th { position: sticky; top: 0; background: #fff; color: var(--acr-texto-suave); z-index: 1; }
@media (max-width: 700px) { .fact-tabla { min-width: 760px; } }
</style>
