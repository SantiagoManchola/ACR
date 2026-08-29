<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import AppIcon from './AppIcon.vue'

const auth = useAuthStore()
const open = ref(false)

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
        <span class="logo"><AppIcon name="drop" :size="20" /></span>
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
        <router-link class="nav-item" to="/dashboard" @click="close"><AppIcon name="home" /><span>Inicio</span></router-link>
        <router-link class="nav-item" to="/inventario" @click="close" v-if="['admin','administrativo'].includes(auth.rol)"><AppIcon name="inventory" /><span>Inventario</span></router-link>
        <router-link class="nav-item" to="/micromedidores" @click="close" v-if="['admin','administrativo','fontanero'].includes(auth.rol)"><AppIcon name="gauge" /><span>Micromedidores</span></router-link>
        <router-link class="nav-item" to="/planta" @click="close" v-if="['admin','operario','administrativo'].includes(auth.rol)"><AppIcon name="drop" /><span>Planta de tratamiento</span></router-link>
        <div class="nav-group-label" v-if="auth.rol === 'admin'">Administración</div>
        <router-link class="nav-item" to="/usuarios" @click="close" v-if="auth.rol === 'admin'"><AppIcon name="users" /><span>Usuarios y roles</span></router-link>
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
