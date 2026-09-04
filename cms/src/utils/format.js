// Formateo de números para la UI del ACR.
// Muestra decimales solo si el valor los tiene; de lo contrario los omite.
// "0.00" -> "0", "12000.00" -> "12000", "2.50" -> "2.5", "7.5000" -> "7.5".
export function fmtNum(value, maxDecimals = 4) {
  if (value === null || value === undefined || value === '') return '—'
  const n = typeof value === 'number' ? value : Number(value)
  if (Number.isNaN(n)) return '—'
  if (Number.isInteger(n)) return String(n)
  // Recorta ceros decimales sobrantes sin pasar de maxDecimals.
  const fixed = n.toFixed(maxDecimals)
  return fixed.replace(/\.?0+$/, '')
}

// Formatea un rango min/máx (valores pueden ser null). Usa fmtNum por componente.
export function fmtRango(min, max) {
  const a = min != null && min !== '' ? fmtNum(min) : '—'
  const b = max != null && max !== '' ? fmtNum(max) : '—'
  return `${a} / ${b}`
}

// Fecha de hoy en Colombia (America/Bogota, UTC-5) en formato YYYY-MM-DD.
// Se usa como valor por defecto de todos los filtros de fecha para que las
// vistas arranquen filtradas al día de hoy.
export function hoyColombia() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date())
}

// Opciones del selector de formato de reporte (CSV/XLSX/PDF), compartidas
// por todas las vistas para un estilo único de selectores.
export const formatoOptions = [
  { value: 'csv', label: 'CSV' },
  { value: 'xlsx', label: 'XLSX' },
  { value: 'pdf', label: 'PDF' },
]
