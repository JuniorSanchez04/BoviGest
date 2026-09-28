from datetime import datetime, date


def hoy() -> str:
    """Retorna la fecha de hoy en formato DD/MM/AAAA (para campos del formulario)."""
    return date.today().strftime('%d/%m/%Y')


def formatear(d) -> str:
    """
    Convierte datetime.date de MySQL a DD/MM/AAAA para mostrar en la UI.
    Si el valor es None retorna string vacío.
    """
    if d is None:
        return ''
    return d.strftime('%d/%m/%Y')


def parsear(texto: str) -> str | None:
    """
    Convierte DD/MM/AAAA (que escribe el usuario) a YYYY-MM-DD (que espera MySQL).
    Retorna None si el campo está vacío.
    Lanza ValueError si el formato es incorrecto.
    """
    if not texto.strip():
        return None
    try:
        dt = datetime.strptime(texto.strip(), '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Formato de fecha inválido. Usá DD/MM/AAAA.")