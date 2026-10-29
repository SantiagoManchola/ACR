// Metadatos compartidos del semáforo de la planta.
// El color nunca es la única señal: siempre se muestra la etiqueta de texto.
export const ESTADOS_PLANTA = {
  funcionando: {
    value: 'funcionando',
    label: 'En funcionamiento',
    short: 'Funcionando',
    color: 'ok',
    descripcion: 'Opera normalmente',
  },
  afectacion: {
    value: 'afectacion',
    label: 'Afectación',
    short: 'Afectación',
    color: 'warn',
    descripcion: 'Opera parcialmente o con restricción',
  },
  fuera_servicio: {
    value: 'fuera_servicio',
    label: 'Fuera de funcionamiento',
    short: 'Fuera de servicio',
    color: 'bad',
    descripcion: 'No está operando',
  },
  sin_estado: {
    value: 'sin_estado',
    label: 'Sin reportar',
    short: 'Sin reportar',
    color: 'muted',
    descripcion: 'Aún no tiene un estado registrado',
  },
}

export const ESTADOS_PLANTA_OPTIONS = [
  ESTADOS_PLANTA.funcionando,
  ESTADOS_PLANTA.afectacion,
  ESTADOS_PLANTA.fuera_servicio,
]

export function estadoPlantaMeta(estado) {
  return ESTADOS_PLANTA[estado] || ESTADOS_PLANTA.sin_estado
}
