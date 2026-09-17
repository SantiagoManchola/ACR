import axios from 'axios'

const TOKEN_KEY = 'acr_token'
const REFRESH_KEY = 'acr_refresh'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}
export function setToken(t) {
  if (t) localStorage.setItem(TOKEN_KEY, t)
  else localStorage.removeItem(TOKEN_KEY)
}
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}
export function setRefreshToken(t) {
  if (t) localStorage.setItem(REFRESH_KEY, t)
  else localStorage.removeItem(REFRESH_KEY)
}
export function limpiarSesion() {
  setToken(null)
  setRefreshToken(null)
}

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 20000,
})

let routerRef = null
let piniaRef = null
// Un solo refresh compartido: si varias peticiones expiran a la vez,
// todas esperan el mismo POST /auth/refresh en vez de multiplicarlo.
let refrescoEnCurso = null

export function setupHttp(router, pinia) {
  routerRef = router
  piniaRef = pinia
  client.interceptors.request.use((config) => {
    const t = getToken()
    if (t) config.headers.Authorization = `Bearer ${t}`
    return config
  })
  client.interceptors.response.use(
    (r) => r,
    (error) => {
      const cfg = error.config || {}
      const url = String(cfg.url || '')
      const esAuthUrl = url.includes('/auth/login') || url.includes('/auth/refresh')
      // 401 en petición normal: intentar refresh una sola vez y reintentar.
      if (error.response && error.response.status === 401 && !cfg.__reintento && !esAuthUrl) {
        return reintentarConRefresh(cfg, error)
      }
      return Promise.reject(error)
    }
  )
}

async function reintentarConRefresh(cfg, error) {
  const rt = getRefreshToken()
  if (!rt) {
    cerrarSesionPorExpiracion()
    return Promise.reject(error)
  }
  try {
    refrescoEnCurso = refrescoEnCurso || client.post('/auth/refresh', { refresh_token: rt })
    const { data } = await refrescoEnCurso
    refrescoEnCurso = null
    setToken(data.access_token)
    setRefreshToken(data.refresh_token)
    cfg.__reintento = true
    cfg.headers = { ...(cfg.headers || {}), Authorization: `Bearer ${data.access_token}` }
    return client(cfg)
  } catch {
    refrescoEnCurso = null
    cerrarSesionPorExpiracion()
    return Promise.reject(error)
  }
}

/* Token (o refresh) inválido: limpiar TODO y volver al login con mensaje claro.
   Se limpia también el store de auth para que el router no rebote de vuelta
   al dashboard con un token muerto (esa era la causa de la pantalla en blanco). */
async function cerrarSesionPorExpiracion() {
  limpiarSesion()
  try {
    const { useAuthStore } = await import('../stores/auth')
    if (piniaRef) {
      const auth = useAuthStore(piniaRef)
      auth.token = null
      auth.user = null
    }
  } catch { /* noop */ }
  if (routerRef && routerRef.currentRoute.value.name !== 'login') {
    routerRef.replace({ name: 'login', query: { sesion: 'expirada' } })
  }
}

export function apiError(e, fallback = 'Ocurrió un error en la solicitud') {
  if (e.response && e.response.data) {
    const d = e.response.data
    if (typeof d.detail === 'string') return d.detail
    if (Array.isArray(d.detail)) return d.detail.map((x) => x.msg || x).join(', ')
  }
  return e.message || fallback
}

// Descarga un reporte (CSV/XLSX/PDF) desde un endpoint GET que devuelve el archivo.
export async function descargarReporte(path, params = {}, nombre = 'reporte') {
  const { data, headers } = await client.get(path, {
    params,
    responseType: 'blob',
  })
  const contentType = headers['content-type'] || ''
  let ext = 'bin'
  if (contentType.includes('csv')) ext = 'csv'
  else if (contentType.includes('spreadsheetml')) ext = 'xlsx'
  else if (contentType.includes('pdf')) ext = 'pdf'
  const url = window.URL.createObjectURL(new Blob([data], { type: contentType }))
  const a = document.createElement('a')
  a.href = url
  a.download = `${nombre}.${ext}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export default client
