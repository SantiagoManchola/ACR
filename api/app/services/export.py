"""Servicio de exportación a CSV / XLSX / PDF (RNF-19)."""
import csv
import io
from datetime import date, datetime
from typing import Iterable, Sequence


def _a_texto(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, (int, float, str, bool)):
        return str(v)
    if hasattr(v, "value"):  # Enum de SQLAlchemy/Pydantic
        return str(v.value)
    return str(v)


def a_csv(filas: Sequence[dict], columnas: Sequence[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(columnas))
    writer.writeheader()
    for f in filas:
        writer.writerow({c: _a_texto(f.get(c)) for c in columnas})
    return buf.getvalue()


def a_xlsx(filas: Sequence[dict], columnas: Sequence[str]) -> bytes:
    import pandas as pd

    datos = [{c: _a_texto(f.get(c)) for c in columnas} for f in filas]
    df = pd.DataFrame(datos, columns=list(columnas))
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="reporte")
    return buf.getvalue()


def a_pdf(filas: Sequence[dict], columnas: Sequence[str], titulo: str) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(letter),
        title=titulo, leftMargin=24, rightMargin=24,
    )
    styles = getSampleStyleSheet()
    encabezado = [titulo]
    tabla_datos = [[str(c).replace("_", " ").title() for c in columnas]]
    for f in filas:
        tabla_datos.append([_a_texto(f.get(c)) for c in columnas])

    tabla = Table([encabezado] + tabla_datos, colWidths=[None] * len(columnas))
    tabla.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#2160AD")),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.white),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 1), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, colors.HexColor("#EEF2FB")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    doc.build([tabla])
    return buf.getvalue()
