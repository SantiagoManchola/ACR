<script setup>
import AppIcon from './AppIcon.vue'
import { fmtNum } from '../utils/format'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, align?, num? }]
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Sin registros.' },
  error: { type: String, default: '' },
  pageSize: { type: Number, default: 10 },
})

const page = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(props.rows.length / props.pageSize)))
const paginated = computed(() =>
  props.rows.slice((page.value - 1) * props.pageSize, page.value * props.pageSize)
)
const rango = computed(() => {
  if (!props.rows.length) return '0'
  const ini = (page.value - 1) * props.pageSize + 1
  const fin = Math.min(page.value * props.pageSize, props.rows.length)
  return `${ini}–${fin} de ${props.rows.length}`
})

watch(() => props.rows, () => { if (page.value > totalPages.value) page.value = 1 })
watch(totalPages, (t) => { if (page.value > t) page.value = t })

function goto(p) { page.value = Math.min(Math.max(1, p), totalPages.value) }
</script>

<template>
  <div>
    <div v-if="error" class="alert alert-bad" style="margin-bottom:.8rem">
      <span>{{ error }}</span>
    </div>

    <div v-if="loading" class="state-block">
      <div class="spinner"></div>
      <p>Cargando…</p>
    </div>

    <div v-else-if="!rows.length" class="state-block">
      <AppIcon name="search" :size="28" />
      <p style="margin-top:.4rem">{{ emptyText }}</p>
    </div>

    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :class="{ num: col.align === 'right' }">{{ col.label }}</th>
            <th v-if="$slots['row-actions']" class="num">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in paginated" :key="row.id ?? i">
            <td v-for="col in columns" :key="col.key" :class="{ num: col.align === 'right' }">
              <slot name="cell" :row="row" :col="col">
                {{ col.num ? fmtNum(row[col.key]) : (row[col.key] ?? '—') }}
              </slot>
            </td>
            <td v-if="$slots['row-actions']" class="row-actions">
              <slot name="row-actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && rows.length" class="table-pagination">
      <span class="muted">{{ rango }}</span>
      <div class="pager">
        <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="goto(page - 1)">
          <AppIcon name="chevronLeft" :size="14" /> Anterior
        </button>
        <span class="pager-num">Página {{ page }} / {{ totalPages }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="page >= totalPages" @click="goto(page + 1)">
          Siguiente <AppIcon name="chevronRight" :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>
