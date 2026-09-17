import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Acceso por rol (regla de negocio 12): planta restringida a operario/admin
// (el administrativo NO tiene acceso al módulo de planta).
export const MODULOS = {
  dashboard: { label: 'Inicio', icon: 'home', roles: ['admin', 'administrativo', 'operario', 'fontanero'] },
  inventario: { label: 'Inventario', icon: 'inventory', roles: ['admin', 'administrativo'] },
  micromedidores: { label: 'Micromedidores', icon: 'gauge', roles: ['admin', 'administrativo', 'fontanero'] },
  planta: { label: 'Planta de tratamiento', icon: 'drop', roles: ['admin', 'operario'] },
  usuarios: { label: 'Usuarios y roles', icon: 'users', roles: ['admin'] },
}

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'inventario', name: 'inventario', component: () => import('../views/InventarioView.vue') },
      { path: 'micromedidores', name: 'micromedidores', component: () => import('../views/MicromedidoresView.vue') },
      { path: 'planta', name: 'planta', component: () => import('../views/PlantaView.vue') },
      { path: 'usuarios', name: 'usuarios', component: () => import('../views/UsuariosView.vue'), meta: { roles: ['admin'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'notfound', component: () => import('../views/NotFound.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    // Con token en memoria hay que validarlo: si está muerto (expiró y el
    // refresh falló) se limpia y se entra al login; nunca rebote al dashboard.
    if (auth.isAuthenticated && !auth.user) {
      try { await auth.fetchMe() } catch { auth.logout() }
    }
    if (auth.isAuthenticated && to.name === 'login') return { name: 'dashboard' }
    return true
  }
  if (to.meta.requiresAuth) {
    if (!auth.isAuthenticated) return { name: 'login' }
    if (!auth.user) {
      try { await auth.fetchMe() } catch { return { name: 'login' } }
    }
    const allowed = to.meta.roles || MODULOS[to.name]?.roles
    if (allowed && auth.rol && !allowed.includes(auth.rol)) {
      return { name: 'dashboard', query: { denied: '1' } }
    }
  }
  return true
})

export default router
