"""Helpers de auditoría (trazabilidad RNF-07)."""


def sellar(obj, usuario, nuevo: bool = True) -> None:
    """Inyecta created_by/updated_by según el usuario autenticado."""
    if nuevo:
        obj.created_by = usuario.id
    obj.updated_by = usuario.id
