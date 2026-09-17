<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { MODULOS } from '../router'
import AppIcon from './AppIcon.vue'

const auth = useAuthStore()
const route = useRoute()
const open = ref(false)

/* Item activo del aside: por NOMBRE de módulo (todas las pestañas comparten
   el nombre de ruta del módulo). router-link-active no sirve aquí porque
   exige además params idénticos y marcaría solo la pestaña por defecto. */
const enModulo = (key) => route.name === key

// Navegación según el rol (fuente única: MODULOS del router).
// Así, p. ej., el rol administrativo (oficina) NO ve la pestaña de Planta.
// Los links apuntan a la PESTAÑA por defecto de cada módulo.
const linksOperacion = [
  { to: '/dashboard', key: 'dashboard' },
  { to: '/inventario/elementos', key: 'inventario' },
  { to: '/micromedidores/suscriptores', key: 'micromedidores' },
  { to: '/planta/parametros', key: 'planta' },
]
const linksAdmin = [{ to: '/usuarios/usuarios', key: 'usuarios' }]
const puedeVer = (key) => (MODULOS[key]?.roles || []).includes(auth.rol)

function toggle() { open.value = !open.value }
function close() { open.value = false }
</script>

<template>
  <div class="app-shell">
    <header class="navbar">
      <button class="icon-btn menu-toggle" @click="toggle" aria-label="Menú">
        <AppIcon name="menu" />
      </button>
      <div class="brand">
        <span class="logo"><img src="/acr-logo.png" alt="ACR" /></span>
        <span>ACR<small>Acueducto Comunitario Acuaricaurte</small></span>
      </div>
      <div class="spacer"></div>
      <div class="user-chip" v-if="auth.user">
        <span class="avatar">{{ (auth.nombre || '?').charAt(0).toUpperCase() }}</span>
        <span class="hide-sm">
          {{ auth.nombre }}<br />
          <small style="opacity:.8;text-transform:capitalize">{{ auth.rol }}</small>
        </span>
      </div>
      <button class="icon-btn" @click="auth.logout(); $router.push('/login')" title="Cerrar sesión" aria-label="Cerrar sesión">
        <AppIcon name="logout" />
      </button>
    </header>

    <div class="app-body">
      <div class="sidebar-backdrop" v-if="open" @click="close"></div>
      <aside class="sidebar" :class="{ open }">
        <div class="nav-group-label">Operación</div>
        <router-link
          v-for="l in linksOperacion"
          :key="l.key"
          v-show="puedeVer(l.key)"
          class="nav-item"
          :class="{ 'is-modulo-activo': enModulo(l.key) }"
          :to="l.to"
          @click="close"
        ><AppIcon :name="MODULOS[l.key].icon" /><span>{{ MODULOS[l.key].label }}</span></router-link>
        <div class="nav-group-label" v-show="puedeVer('usuarios')">Administración</div>
        <router-link
          v-for="l in linksAdmin"
          :key="l.key"
          v-show="puedeVer(l.key)"
          class="nav-item"
          :class="{ 'is-modulo-activo': enModulo(l.key) }"
          :to="l.to"
          @click="close"
        ><AppIcon :name="MODULOS[l.key].icon" /><span>{{ MODULOS[l.key].label }}</span></router-link>
      </aside>

      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 600px) { .hide-sm { display: none; } }
</style>
