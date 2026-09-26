import client from './http'

function crearFormulario(archivo, opciones) {
  const form = new FormData()
  form.append('archivo', archivo)
  form.append('mes', String(opciones.mes))
  form.append('anio', String(opciones.anio))
  form.append('fecha_desde', opciones.fecha_desde)
  form.append('fecha_hasta', opciones.fecha_hasta)
  if (opciones.confirmar_reemplazo !== undefined) {
    form.append('confirmar_reemplazo', String(Boolean(opciones.confirmar_reemplazo)))
  }
  return form
}

export async function previsualizarFacturacion(archivo, opciones) {
  const { data } = await client.post(
    '/facturacion/previsualizar',
    crearFormulario(archivo, opciones),
  )
  return data
}

export async function generarArchivoFacturacion(archivo, opciones) {
  let response
  try {
    response = await client.post(
      '/facturacion/generar',
      crearFormulario(archivo, opciones),
      { responseType: 'blob' },
    )
  } catch (error) {
    const blob = error?.response?.data
    if (blob instanceof Blob) {
      let cuerpo = null
      try {
        cuerpo = JSON.parse(await blob.text())
      } catch { /* conservar el error HTTP original si no era JSON */ }
      if (cuerpo?.detail) throw new Error(cuerpo.detail)
    }
    throw error
  }
  const { data, headers } = response
  const blob = new Blob([data], {
    type: headers['content-type'] || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `Facturacion_${opciones.mes}_${opciones.anio}.xlsx`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
