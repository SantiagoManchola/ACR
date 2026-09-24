import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getToken } from '../api/http'

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
      /* Cada pestaña de las vistas con tablas tiene su propia URL
         (inventario/elementos, inventario/categorias, …): la pestaña es
         compartible y el back/forward del navegador la conserva. */
      { path: 'inventario', redirect: { name: 'inventario', params: { tab: 'elementos' } } },
      { path: 'inventario/:tab', name: 'inventario', component: () => import('../views/InventarioView.vue') },
      { path: 'micromedidores', redirect: { name: 'micromedidores', params: { tab: 'suscriptores' } } },
      { path: 'micromedidores/:tab', name: 'micromedidores', component: () => import('../views/MicromedidoresView.vue') },
      { path: 'planta', redirect: { name: 'planta', params: { tab: 'parametros' } } },
      { path: 'planta/:tab', name: 'planta', component: () => import('../views/PlantaView.vue') },
      { path: 'usuarios', redirect: { name: 'usuarios', params: { tab: 'usuarios' } } },
      { path: 'usuarios/:tab', name: 'usuarios', component: () => import('../views/UsuariosView.vue'), meta: { roles: ['admin'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'notfound', component: () => import('../views/NotFound.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach(async (to) => {
  /* Red de seguridad: cualquier error inesperado en el guard no debe dejar la
     navegación colgada (pantalla en blanco); se cae siempre al login. */
  try {
    return await resolverAcceso(to)
  } catch (e) {
    return { name: 'login', query: { sesion: 'expirada' } }
  }
})

async function resolverAcceso(to) {
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
      try {
        await auth.fetchMe()
      } catch {
        /* Token muerto: el interceptor ya limpió la sesión. Se consulta el
           storage directo (el store puede tardar un tick en sincronizarse).
           Con el token aún presente el fallo es de red/servidor, no de sesión. */
        if (getToken()) return { name: 'login' }
        return { name: 'login', query: { sesion: 'expirada' } }
      }
    }
    const allowed = to.meta.roles || MODULOS[to.name]?.roles
    if (allowed && auth.rol && !allowed.includes(auth.rol)) {
      return { name: 'dashboard', query: { denied: '1' } }
    }
  }
  return true
}

export default router
