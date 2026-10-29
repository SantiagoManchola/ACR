<script setup>
import { computed, ref, watch } from 'vue'
import BaseModal from '../BaseModal.vue'
import BaseAlert from '../BaseAlert.vue'
import AppIcon from '../AppIcon.vue'
import { usePlantaStore } from '../../stores/planta'
import { apiError } from '../../api/http'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const planta = usePlantaStore()
const componentes = computed(() => planta.componentesAdmin)
const form = ref({ nombre: '', descripcion: '' })
const editando = ref(null)
const error = ref('')
const guardando = ref(false)
const reordenando = ref(false)

function limpiarFormulario() {
  editando.value = null
  form.value = { nombre: '', descripcion: '' }
  error.value = ''
}

async function cargar() {
  error.value = ''
  await planta.loadComponentesAdmin()
  if (planta.error) error.value = planta.error
}

watch(
  () => props.modelValue,
  (abierto) => {
    if (abierto) {
      limpiarFormulario()
      cargar()
    }
  },
  { immediate: true },
)

function editar(componente) {
  editando.value = componente
  form.value = {
    nombre: componente.nombre,
    descripcion: componente.descripcion || '',
  }
  error.value = ''
}

async function guardar() {
  error.value = ''
  if (!form.value.nombre.trim()) {
    error.value = 'El nombre de la parte es obligatorio.'
    return
  }
  guardando.value = true
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      descripcion: form.value.descripcion.trim() || null,
    }
    if (editando.value) await planta.updateComponente(editando.value.id, payload)
    else await planta.createComponente(payload)
    limpiarFormulario()
    await Promise.all([planta.loadComponentesAdmin(), planta.loadComponentes()])
    emit('saved')
  } catch (e) {
    error.value = apiError(e)
  } finally {
    guardando.value = false
  }
}

async function alternarActivo(componente) {
  error.value = ''
  try {
    await planta.updateComponente(componente.id, {
      estado: componente.estado === 'activo' ? 'inactivo' : 'activo',
    })
    await Promise.all([planta.loadComponentesAdmin(), planta.loadComponentes()])
    emit('saved')
  } catch (e) {
    error.value = apiError(e)
  }
}

async function mover(index, delta) {
  const destino = index + delta
  if (destino < 0 || destino >= componentes.value.length) return
  const ids = componentes.value.map((c) => c.id)
  const [movido] = ids.splice(index, 1)
  ids.splice(destino, 0, movido)
  error.value = ''
  reordenando.value = true
  try {
    await planta.reordenarComponentes(ids)
    await planta.loadComponentes()
    emit('saved')
  } catch (e) {
    error.value = apiError(e)
  } finally {
    reordenando.value = false
  }
}

function cerrar() {
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Configurar partes de la planta"
    size="820"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <BaseAlert v-if="error" type="bad" class="mb-1">{{ error }}</BaseAlert>

    <div class="config-form card">
      <div class="card-head">
        <div class="title">
          <AppIcon :name="editando ? 'edit' : 'plus'" :size="18" />
          <strong>{{ editando ? 'Editar parte' : 'Agregar parte' }}</strong>
        </div>
        <button v-if="editando" class="btn btn-ghost btn-sm" @click="limpiarFormulario">Cancelar edición</button>
      </div>
      <div class="form-row">
        <div class="field" style="grid-column:span 2">
          <label>Nombre *</label>
          <input v-model="form.nombre" class="input" maxlength="100" placeholder="Ej. Filtro 1" @keyup.enter="guardar" />
        </div>
        <div class="field" style="grid-column:span 2">
          <label>Descripción</label>
          <input v-model="form.descripcion" class="input" maxlength="255" placeholder="Opcional" />
        </div>
      </div>
      <div class="toolbar" style="margin:0">
        <button class="btn btn-primary" :disabled="guardando" @click="guardar">
          <span v-if="guardando" class="spinner"></span><AppIcon v-else :name="editando ? 'save' : 'plus'" />
          {{ guardando ? 'Guardando…' : (editando ? 'Guardar cambios' : 'Agregar parte') }}
        </button>
        <span class="muted" style="font-size:.78rem">El orden se cambia con las flechas de cada parte. Al agregar, la parte queda al final y en funcionamiento.</span>
      </div>
    </div>

    <div class="config-lista">
      <div class="config-lista-head">
        <strong>Partes del diagrama</strong>
        <span class="muted">{{ componentes.length }} parte(s)</span>
      </div>
      <p v-if="!componentes.length" class="muted">Aún no hay partes configuradas.</p>
      <div v-for="(componente, index) in componentes" :key="componente.id" class="config-item">
        <span class="config-orden">{{ index + 1 }}</span>
        <div class="config-datos">
          <strong>{{ componente.nombre }}</strong>
          <small v-if="componente.descripcion">{{ componente.descripcion }}</small>
          <span class="badge" :class="componente.estado === 'activo' ? 'badge-ok' : 'badge-muted'">
            {{ componente.estado }}
          </span>
        </div>
        <div class="config-acciones">
          <button class="btn btn-ghost btn-sm" title="Subir" :disabled="reordenando || index === 0" @click="mover(index, -1)">
            <AppIcon name="arrowUp" :size="16" />
          </button>
          <button class="btn btn-ghost btn-sm" title="Bajar" :disabled="reordenando || index === componentes.length - 1" @click="mover(index, 1)">
            <AppIcon name="arrowDown" :size="16" />
          </button>
          <button class="btn btn-ghost btn-sm" title="Editar" @click="editar(componente)">
            <AppIcon name="edit" :size="16" />
          </button>
          <button class="btn btn-ghost btn-sm" :title="componente.estado === 'activo' ? 'Desactivar' : 'Activar'" @click="alternarActivo(componente)">
            <AppIcon :name="componente.estado === 'activo' ? 'eyeOff' : 'eye'" :size="16" />
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-ghost" @click="cerrar">Cerrar</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.config-form { margin-bottom: 1rem; }
.config-form .card-head { margin-bottom: .7rem; }
.config-lista { border-top: 1px solid var(--acr-borde); padding-top: .8rem; }
.config-lista-head { display: flex; align-items: center; justify-content: space-between; gap: .5rem; margin-bottom: .5rem; }
.config-item {
  display: flex;
  align-items: center;
  gap: .55rem;
  padding: .5rem .2rem;
  border-bottom: 1px solid var(--acr-borde);
}
.config-item:last-child { border-bottom: none; }
.config-orden {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--acr-azul-50);
  color: var(--acr-azul);
  display: grid;
  place-items: center;
  font-size: .72rem;
  font-weight: 700;
  flex: none;
}
.config-datos { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: .12rem; }
.config-datos strong { font-size: .88rem; }
.config-datos small { color: var(--acr-texto-suave); font-size: .76rem; }
.config-datos .badge { align-self: flex-start; font-size: .64rem; }
.config-acciones { display: flex; gap: .15rem; flex: none; }
@media (max-width: 600px) {
  .config-item { align-items: flex-start; flex-wrap: wrap; }
  .config-datos { flex-basis: calc(100% - 40px); }
  .config-acciones { margin-left: 30px; }
}
</style>
