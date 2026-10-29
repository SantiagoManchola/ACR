<script setup>
import { computed } from 'vue'
import { estadoPlantaMeta } from '../../utils/estadoPlanta'

const props = defineProps({
  componentes: { type: Array, default: () => [] },
  compact: { type: Boolean, default: false },
  interactive: { type: Boolean, default: true },
})
const emit = defineEmits(['select'])

const nodos = computed(() => (props.componentes || []).map((c) => ({
  ...c,
  meta: estadoPlantaMeta(c.estado_actual),
})))

function seleccionar(componente) {
  if (props.interactive) emit('select', componente)
}

function titulo(componente) {
  const meta = estadoPlantaMeta(componente.estado_actual)
  const nota = componente.nota_actual ? ` · ${componente.nota_actual}` : ''
  return `${componente.nombre}: ${meta.label}${nota}`
}
</script>

<template>
  <div class="diagrama-wrapper">
    <p v-if="!componentes.length" class="diagrama-vacio">
      No hay partes configuradas. El administrador puede agregarlas desde «Configurar partes».
    </p>
    <div v-else class="diagrama" :class="{ compacto: compact, completo: !compact }" role="group" aria-label="Diagrama lineal de la planta de tratamiento">
      <template v-for="(componente, i) in nodos" :key="componente.id">
        <component
          :is="interactive ? 'button' : 'div'"
          class="nodo"
          :class="[`estado-${componente.meta.color}`, { interactivo: interactive }]"
          :type="interactive ? 'button' : undefined"
          :title="titulo(componente)"
          @click="seleccionar(componente)"
        >
          <span class="nodo-top">
            <span class="dot" aria-hidden="true"></span>
            <span class="nodo-estado">{{ componente.meta.short }}</span>
          </span>
          <strong class="nodo-nombre">{{ componente.nombre }}</strong>
          <template v-if="!compact">
            <span class="nodo-label">{{ componente.meta.label }}</span>
            <span v-if="componente.nota_actual" class="nodo-nota">{{ componente.nota_actual }}</span>
            <span v-if="componente.fecha_actualizacion" class="nodo-fecha">
              {{ componente.fecha_actualizacion }}<template v-if="componente.hora_actualizacion"> · {{ String(componente.hora_actualizacion).slice(0, 5) }}</template>
              <template v-if="componente.responsable_nombre"> · {{ componente.responsable_nombre }}</template>
            </span>
          </template>
        </component>
        <span v-if="i < nodos.length - 1" class="conector" aria-hidden="true">
          <span class="conector-linea"></span>
          <span class="conector-flecha"></span>
        </span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.diagrama-wrapper { min-width: 0; }
.diagrama {
  display: flex;
  align-items: stretch;
  gap: .35rem;
  overflow-x: auto;
  padding: .25rem .15rem .5rem;
  scrollbar-width: thin;
}
.diagrama-vacio {
  margin: 0;
  padding: .8rem 1rem;
  border: 1px dashed var(--acr-borde);
  border-radius: var(--acr-radio-sm);
  color: var(--acr-texto-suave);
  font-size: .86rem;
  background: #fff;
}
.nodo {
  flex: 0 0 auto;
  width: 178px;
  min-height: 112px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: .28rem;
  text-align: left;
  padding: .65rem .7rem;
  border: 1px solid var(--acr-borde);
  border-top: 4px solid var(--acr-borde);
  border-radius: var(--acr-radio-sm);
  background: #fff;
  color: var(--acr-texto);
  font-family: inherit;
  box-shadow: var(--acr-sombra-sm);
}
.nodo.interactivo { cursor: pointer; }
.nodo.interactivo:hover { box-shadow: var(--acr-sombra); transform: translateY(-1px); }
.nodo.interactivo:focus-visible { outline: 2px solid var(--acr-azul); outline-offset: 2px; }
.nodo-top { display: flex; align-items: center; gap: .35rem; width: 100%; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; flex: none; }
.nodo-estado {
  font-size: .68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .03em;
  color: currentColor;
}
.nodo-nombre {
  font-size: .84rem;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.nodo-label { font-size: .72rem; color: var(--acr-texto-suave); }
.nodo-nota {
  width: 100%;
  font-size: .72rem;
  color: var(--acr-texto-suave);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nodo-fecha { font-size: .66rem; color: var(--acr-texto-suave); }
.nodo.estado-ok { border-top-color: var(--acr-ok); color: var(--acr-ok); background: linear-gradient(180deg, var(--acr-ok-bg), #fff 62%); }
.nodo.estado-warn { border-top-color: var(--acr-warn); color: #9a6d00; background: linear-gradient(180deg, var(--acr-warn-bg), #fff 62%); }
.nodo.estado-bad { border-top-color: var(--acr-bad); color: var(--acr-bad); background: linear-gradient(180deg, var(--acr-bad-bg), #fff 62%); }
.nodo.estado-muted { border-top-color: var(--acr-texto-suave); color: var(--acr-texto-suave); background: linear-gradient(180deg, #eef1f5, #fff 62%); }
.nodo .nodo-nombre, .nodo .nodo-label, .nodo .nodo-nota, .nodo .nodo-fecha { color: var(--acr-texto); }
.nodo .nodo-estado { color: currentColor; }
.conector {
  flex: 0 0 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--acr-azul);
  user-select: none;
}
.conector-linea { width: 10px; height: 2px; background: #c9d8ea; border-radius: 2px; }
.conector-flecha {
  width: 7px;
  height: 7px;
  border-top: 2px solid currentColor;
  border-right: 2px solid currentColor;
  transform: rotate(45deg);
  margin-left: -3px;
}
.compacto { gap: .3rem; padding-top: .2rem; scroll-snap-type: x proximity; -webkit-overflow-scrolling: touch; }
.compacto .nodo { width: 150px; min-height: 68px; padding: .55rem .65rem; gap: .16rem; scroll-snap-align: start; }
.compacto .nodo-nombre { font-size: .79rem; }
.compacto .nodo-estado { font-size: .63rem; }
.compacto .conector { flex-basis: 17px; }
.compacto .conector-linea { width: 8px; }
.compacto .conector-flecha { width: 6px; height: 6px; margin-left: -2px; }
@media (max-width: 700px) {
  /* Flujo vertical: más aire entre partes y flechas claras hacia abajo */
  .completo { flex-direction: column; align-items: stretch; overflow-x: visible; gap: .3rem; padding: .2rem 0 .6rem; }
  .completo .nodo { width: 100%; min-height: 0; padding: .8rem .85rem; gap: .32rem; }
  .completo .nodo-nombre { font-size: .92rem; line-height: 1.25; }
  .completo .nodo-label { display: none; }
  .completo .nodo-nota {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-size: .78rem;
    line-height: 1.3;
  }
  .completo .nodo-fecha { font-size: .72rem; line-height: 1.3; }
  .completo .conector {
    flex: 0 0 34px;
    height: 34px;
    flex-direction: column;
    gap: 1px;
  }
  .completo .conector-linea { width: 2px; height: 20px; }
  .completo .conector-flecha { transform: rotate(135deg); margin: -3px 0 0 0; }
  .compacto .nodo { width: 152px; min-height: 72px; padding: .6rem .65rem; gap: .2rem; }
  .compacto .nodo-nombre { font-size: .8rem; }
  .compacto .nodo-estado { font-size: .64rem; }
}
</style>
