"""Router de reportes con exportación CSV/XLSX/PDF (RF-20, RF-36, RF-54)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..security import get_current_user, get_db, require_role
from ..services import export as svc_export

router = APIRouter(prefix="/reportes", tags=["Reportes"])
_LECTORES = ["admin", "administrativo", "operario"]


def _responder(filas, columnas, formato: str, nombre: str, titulo: str):
    formato = (formato or "json").lower()
    if formato == "json":
        from fastapi.encoders import jsonable_encoder

        return filas
    if formato == "csv":
        contenido = svc_export.a_csv(filas, columnas)
        return Response(content=contenido, media_type="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={nombre}.csv"})
    if formato == "xlsx":
        contenido = svc_export.a_xlsx(filas, columnas)
        return Response(content=contenido,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f"attachment; filename={nombre}.xlsx"})
    if formato == "pdf":
        contenido = svc_export.a_pdf(filas, columnas, titulo)
        return Response(content=contenido, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={nombre}.pdf"})
    raise HTTPException(400, "formato debe ser csv, xlsx o pdf")


@router.get("/inventario", summary="Reporte de inventario")
def reporte_inventario(
    formato: str = Query(default="json"),
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    filas = db.execute(select(models.ElementoInventario)).scalars().all()
    datos = [
        {
            "id": e.id, "nombre": e.nombre, "categoria_id": e.categoria_id,
            "ubicacion": e.ubicacion, "cantidad": e.cantidad, "unidad": e.unidad,
            "minimo": e.minimo, "estado": e.estado,
        }
        for e in filas
    ]
    columnas = ["id", "nombre", "categoria_id", "ubicacion", "cantidad", "unidad", "minimo", "estado"]
    return _responder(datos, columnas, formato, "reporte_inventario", "Inventario ACR")


@router.get("/consumo", summary="Reporte de consumo de micromedidores")
def reporte_consumo(
    sector: str | None = None,
    formato: str = Query(default="json"),
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = (
        select(models.Lectura, models.Suscriptor.nombre, models.Suscriptor.sector)
        .join(models.Suscriptor, models.Lectura.suscriptor_id == models.Suscriptor.id)
    )
    if sector:
        stmt = stmt.where(models.Suscriptor.sector == sector)
    resultados = db.execute(stmt).all()
    datos = [
        {
            "lectura_id": l.id, "fecha": l.fecha, "sector": sec, "suscriptor": nom,
            "micromedidor_id": l.micromedidor_id, "lectura": l.lectura,
            "consumo": l.consumo, "promedio_usado": l.promedio_usado,
            "irregular": l.irregular,
        }
        for (l, nom, sec) in resultados
    ]
    columnas = ["lectura_id", "fecha", "sector", "suscriptor", "micromedidor_id",
                "lectura", "consumo", "promedio_usado", "irregular"]
    return _responder(datos, columnas, formato, "reporte_consumo", "Consumo micromedidores ACR")


@router.get("/planta", summary="Reporte de planta de tratamiento")
def reporte_planta(
    fuera_rango: bool | None = None,
    formato: str = Query(default="json"),
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = (
        select(models.Medicion, models.ParametroPlanta.nombre)
        .join(models.ParametroPlanta, models.Medicion.parametro_id == models.ParametroPlanta.id)
    )
    if fuera_rango is not None:
        stmt = stmt.where(models.Medicion.fuera_rango.is_(fuera_rango))
    resultados = db.execute(stmt).all()
    datos = [
        {
            "medicion_id": m.id, "fecha": m.fecha, "parametro": nom, "valor": m.valor,
            "fuera_rango": m.fuera_rango, "accion_correctiva": m.accion_correctiva,
        }
        for (m, nom) in resultados
    ]
    columnas = ["medicion_id", "fecha", "parametro", "valor", "fuera_rango", "accion_correctiva"]
    return _responder(datos, columnas, formato, "reporte_planta", "Planta de tratamiento ACR")
