from mysql.connector import IntegrityError

from models import produccion_model
from models.animal_model import buscar_activo_por_caravana
from core.session import get_sesion
from utils.fecha_helper import parsear


# ── Consultas ──────────────────────────────────────────────────

def listar_gmd() -> list[dict]:
    return produccion_model.listar_gmd_animales()


def gmd_por_lote() -> list[dict]:
    return produccion_model.gmd_por_lote()


def historial_animal(id_animal: int) -> list[dict]:
    return produccion_model.historial_pesajes_animal(id_animal)


def animales_sin_pesar(dias: int = 30) -> list[dict]:
    return produccion_model.animales_sin_pesaje_reciente(dias)


# ── Búsqueda de animal ─────────────────────────────────────────

def buscar_animal(caravana: str) -> tuple[dict | None, str | None]:
    """Busca un animal activo por caravana. Mismo patrón que sanidad."""
    if not caravana.strip():
        return None, "Ingresá el número de caravana."
    animal = buscar_activo_por_caravana(caravana)
    if animal is None:
        return None, f"No se encontró ningún animal activo con la caravana «{caravana.upper()}»."
    return animal, None


# ── Registro individual ────────────────────────────────────────

def registrar_pesaje(datos_form: dict) -> tuple[bool, str | None]:
    """
    Valida y guarda un pesaje individual.
    """
    if not datos_form.get('id_animal'):
        return False, "Buscá y seleccioná un animal primero."

    if not datos_form.get('fecha', '').strip():
        return False, "La fecha es obligatoria."

    # Parsear y validar peso
    peso_str = datos_form.get('peso_kg', '').strip()
    if not peso_str:
        return False, "El peso es obligatorio."
    try:
        peso = float(peso_str.replace(',', '.'))
        if peso <= 0:
            return False, "El peso debe ser un número positivo."
    except ValueError:
        return False, "El peso debe ser un número válido (ej: 285 o 285.5)."

    try:
        fecha = parsear(datos_form['fecha'])
    except ValueError as e:
        return False, str(e)

    # Verificar duplicado antes de insertar
    if produccion_model.animal_ya_pesado_en_fecha(datos_form['id_animal'], fecha):
        return False, "Este animal ya tiene un pesaje registrado en esa fecha."

    datos = {
        'id_animal':    datos_form['id_animal'],
        'fecha':        fecha,
        'peso_kg':      peso,
        'observaciones': datos_form.get('observaciones', '').strip() or None,
    }

    try:
        produccion_model.registrar_pesaje(datos, get_sesion()['id_usuario'])
        return True, None
    except IntegrityError:
        return False, "Este animal ya tiene un pesaje registrado en esa fecha."
    except Exception as e:
        return False, f"Error al guardar: {e}"


# ── Registro masivo ────────────────────────────────────────────

def validar_item_masivo(
    caravana: str,
    peso_str: str,
    fecha_str: str,
    ids_ya_en_lista: set,
) -> tuple[dict | None, str | None]:
    """
    Valida un ítem antes de agregarlo a la lista de pesaje masivo.
    Retorna (datos_item, None) en éxito o (None, mensaje) en error.
    """
    animal, error = buscar_animal(caravana)
    if error:
        return None, error

    if animal['id_animal'] in ids_ya_en_lista:
        return None, f"La caravana «{caravana.upper()}» ya fue agregada a la lista."

    if not peso_str.strip():
        return None, "Ingresá el peso."
    try:
        peso = float(peso_str.strip().replace(',', '.'))
        if peso <= 0:
            return None, "El peso debe ser positivo."
    except ValueError:
        return None, "El peso debe ser un número válido."

    try:
        fecha = parsear(fecha_str)
    except ValueError as e:
        return None, str(e)

    if produccion_model.animal_ya_pesado_en_fecha(animal['id_animal'], fecha):
        return None, f"«{caravana.upper()}» ya tiene pesaje en esa fecha."

    return {
        'id_animal':  animal['id_animal'],
        'caravana':   animal['caravana'],
        'categoria':  animal['categoria'],
        'fecha':      fecha,
        'peso_kg':    peso,
    }, None


def guardar_pesajes_masivo(lista: list[dict]) -> tuple[bool, str | None]:
    """Guarda todos los pesajes pendientes en una sola transacción."""
    if not lista:
        return False, "La lista está vacía."
    try:
        n = produccion_model.registrar_pesajes_masivo(lista, get_sesion()['id_usuario'])
        return True, f"{n} pesaje{'s' if n != 1 else ''} guardado{'s' if n != 1 else ''} correctamente."
    except Exception as e:
        return False, f"Error al guardar: {e}"