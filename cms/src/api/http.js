import axios from 'axios'

const TOKEN_KEY = 'acr_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}
export function setToken(t) {
  if (t) localStorage.setItem(TOKEN_KEY, t)
  else localStorage.removeItem(TOKEN_KEY)
}

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 20000,
})

let routerRef = null

export function setupHttp(router) {
  routerRef = router
  client.interceptors.request.use((config) => {
    const t = getToken()
    if (t) config.headers.Authorization = `Bearer ${t}`
    return config
  })
  client.interceptors.response.use(
    (r) => r,
    (error) => {
      if (error.response && error.response.status === 401) {
        setToken(null)
        if (routerRef && routerRef.currentRoute.value.name !== 'login') {
          routerRef.replace('/login')
        }
      }
      return Promise.reject(error)
    }
  )
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
