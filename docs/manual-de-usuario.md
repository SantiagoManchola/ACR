# Manual de usuario — ACR (Acueducto Comunitario Acuaricaurte)

> Guía para los actores que usarán el sistema. La interfaz es web y funciona en computador
> o celular (navegador). Colores: azul `#2160AD` y blanco.

---

## 1. Acceso al sistema

1. Abre el navegador en la dirección del sistema (URL provista por el administrador).
2. En **Iniciar sesión**, escribe tu **usuario** y **contraseña**.
3. Pulsa **Entrar**. Si olvidaste la contraseña, solicítala al Administrador.
4. Verás el menú según tu rol (Administrador, Personal administrativo, Operario de planta,
   Fontanero).

> El sistema registra quién hace cada acción (trazabilidad). Usa siempre tu cuenta.

## 2. Personal administrativo — Inventario

- **Ver elementos:** menú *Inventario* → listado con nombre, categoría, ubicación y existencia.
- **Nuevo elemento:** botón *Nuevo* → completa nombre, categoría (equipo/herramienta/lab/
  accesorio), ubicación, cantidad, proveedor y valor si aplica.
- **Entrada:** en el elemento → *Entrada* → cantidad recibida y observación.
- **Salida:** en el elemento → *Salida* → cantidad, **responsable** y **motivo**.
- **Alertas:** los elementos por debajo del mínimo aparecen marcados en ámbar/rojo.
- **Historial:** *Movimientos* muestra entradas/salidas con fecha y responsable.
- **Reporte:** *Exportar* (Excel/CSV/PDF).

## 3. Personal administrativo — Micromedidores

- **Suscriptores:** *Micromedidores → Suscriptores* → alta con nombre, cédula, código,
  tipo (residencial/comercial), sector y dirección.
- **Medidor:** asocia un *micromedidor* (serial, tipo, fecha de instalación) al suscriptor.
- **Lectura mensual:** *Lecturas → Nueva* → selecciona medidor, registra valor y fecha.
  - Si no se pudo leer (caja obstruida, acceso negado): marca **Novedad** y el sistema
    usará el **promedio histórico** como referencia.
- **Histórico:** abre un suscriptor/medidor para ver consumos anteriores.
- **Por sector:** *Consulta por sector* agrupa consumos del barrio seleccionado.
- **Reporte:** exporta el consumo histórico.

### Preparar archivo mensual de facturación (administrador / administrativo)

1. En *Micromedidores → Facturación*, selecciona el archivo `.xlsx` del software contable.
2. Elige el mes y año que vas a facturar. El rango de lecturas sugerido inicia el día 25
   del mes y termina el día 5 del siguiente; puedes ajustar ambas fechas.
3. Pulsa *Previsualizar* y revisa las novedades agrupadas antes de generar el archivo.
   Para los medidores se usa la lectura más reciente dentro del rango elegido. Si hay un
   medidor sin lectura, códigos que no aparecen en ACR o diferencias de serial, quedan
   identificados para revisión.
4. Para usuarios sin medidor, desde marzo se calcula el valor numérico con la regla
   `mes anterior - mes anteanterior + mes anterior`. Si falta el historial necesario, la
   fila se reporta como pendiente.
5. La columna del mes de la plantilla normalmente viene en 0 o vacía: esas celdas se completan
   sin confirmación. Solo si ya trae valores distintos de cero, el sistema pide confirmar que
   deseas reemplazarlos en la copia que se descargará. El archivo que subiste permanece intacto.
6. Pulsa *Descargar Excel completado*. El detalle de procesamiento y las novedades se
   pueden descargar aparte. Esta función no crea ni modifica lecturas en ACR.

## 4. Operario de planta — Planta de tratamiento

- **Parámetros:** *Planta → Mediciones* → registra valor de pH, color, turbiedad, cloro
  residual o temperatura (cruda/tratada). La fecha y hora se guardan solas.
- **Fuera de rango:** si el valor supera el mínimo/máximo configurado, la casilla se marca
  en rojo; registra la **acción correctiva** (p. ej. ajustar cloro).
- **Dosificación:** *Químicos* → registra producto y cantidad usada; controla existencias.
- **Actividades:** registra limpieza, desinfección, lavado de tanques o bocatoma.
- **Horas de servicio:** registra el tiempo de operación del día.
- **Historial:** consulta mediciones y actividades por fecha.

## 5. Administrador — Usuarios y permisos

- *Admin → Usuarios*: crear, editar, desactivar usuarios y asignarles un rol.
- *Admin → Roles*: definir qué puede hacer cada rol.
- La información de la planta queda restringida a roles autorizados.

## 6. Reportes (todos los roles según permiso)

- Menú *Reportes* → elige módulo (Inventario / Consumo / Planta), filtra por fecha o sector
  y pulsa *Exportar*.

## 7. Buenas prácticas

- Registra las lecturas apenas las tomás (evita acumular 2 días de trabajo).
- No compartas tu contraseña. Cada acción queda a tu nombre.
- Si ves una alerta roja (inventario bajo o parámetro fuera de rango), avisa al responsable.
- El sistema reemplaza los papeles y el Excel: usa siempre el sistema, no anotes aparte.

## 8. Respaldo y disponibilidad

El sistema está disponible en línea (24/7 para consulta). La información se respalda
automáticamente; no necesitas guardar copias manuales.
