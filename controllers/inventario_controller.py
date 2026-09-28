from mysql.connector import IntegrityError

from models import animal_model, catalogo_model
from core.session import get_sesion
from utils.fecha_helper import parsear


# ── Catálogos (para poblar comboboxes en los formularios) ──────

def cargar_catalogos() -> dict:
    """
    Devuelve todos los catálogos necesarios para los formularios
    del módulo en un solo diccionario.
    """
    return {
        'razas':       catalogo_model.obtener_razas(),
        'categorias':  catalogo_model.obtener_categorias(),
        'sexos':       catalogo_model.obtener_sexos(),
        'lotes':       catalogo_model.obtener_lotes_activos(),
        'motivos_baja': catalogo_model.obtener_motivos_baja(),
    }


# ── Consulta ───────────────────────────────────────────────────

def listar(
    id_lote: int | None = None,
    id_categoria: int | None = None,
    busqueda: str = '',
    solo_activos: bool = True,
) -> list[dict]:
    return animal_model.listar_animales(id_lote, id_categoria, busqueda, solo_activos)


def obtener_animal(id_animal: int) -> dict | None:
    return animal_model.obtener_animal(id_animal)


def historial(id_animal: int) -> list[dict]:
    return animal_model.obtener_historial_movimientos(id_animal)


def resumen() -> list[dict]:
    return animal_model.contar_por_categoria()


# ── Alta ───────────────────────────────────────────────────────

def dar_alta(datos_form: dict) -> tuple[bool, str | None]:
    """
    Valida los campos del formulario y registra el animal.
    Retorna (True, None) en éxito o (False, mensaje) en error.
    """
    # Campos obligatorios
    if not datos_form.get('caravana', '').strip():
        return False, "El número de caravana es obligatorio."

    if not datos_form.get('id_categoria'):
        return False, "Seleccioná una categoría."

    if not datos_form.get('id_sexo'):
        return False, "Seleccioná el sexo."

    if not datos_form.get('fecha_alta', '').strip():
        return False, "La fecha de alta es obligatoria."

    # Parsear fechas
    try:
        fecha_alta = parsear(datos_form['fecha_alta'])
        fecha_nac  = parsear(datos_form.get('fecha_nacimiento', ''))
    except ValueError as e:
        return False, str(e)

    datos = {
        'caravana':        datos_form['caravana'].strip().upper(),
        'id_raza':         datos_form.get('id_raza'),
        'id_categoria':    datos_form['id_categoria'],
        'id_sexo':         datos_form['id_sexo'],
        'fecha_nacimiento': fecha_nac,
        'fecha_alta':       fecha_alta,
        'id_lote':         datos_form.get('id_lote'),
        'observaciones':   datos_form.get('observaciones', '').strip() or None,
    }

    try:
        animal_model.registrar_alta(datos, get_sesion()['id_usuario'])
        return True, None
    except IntegrityError:
        return False, f"Ya existe un animal con la caravana «{datos['caravana']}»."
    except Exception as e:
        return False, f"Error al guardar: {e}"


# ── Baja ───────────────────────────────────────────────────────

def dar_baja(
    id_animal: int,
    id_motivo: int | None,
    fecha_str: str,
    observaciones: str,
) -> tuple[bool, str | None]:
    if not id_motivo:
        return False, "Seleccioná el motivo de baja."

    try:
        fecha = parsear(fecha_str)
    except ValueError as e:
        return False, str(e)

    if not fecha:
        return False, "La fecha de baja es obligatoria."

    try:
        animal_model.registrar_baja(
            id_animal, id_motivo,
            get_sesion()['id_usuario'],
            fecha,
            observaciones.strip() or None,
        )
        return True, None
    except Exception as e:
        return False, f"Error al registrar la baja: {e}"


# ── Traslado ───────────────────────────────────────────────────

def trasladar(
    id_animal: int,
    id_lote_destino: int | None,
    id_lote_actual: int | None,
    fecha_str: str,
    observaciones: str,
) -> tuple[bool, str | None]:
    if not id_lote_destino:
        return False, "Seleccioná el lote de destino."

    if id_lote_destino == id_lote_actual:
        return False, "El animal ya se encuentra en ese lote."

    try:
        fecha = parsear(fecha_str)
    except ValueError as e:
        return False, str(e)

    if not fecha:
        return False, "La fecha de traslado es obligatoria."

    try:
        animal_model.registrar_traslado(
            id_animal, id_lote_destino,
            get_sesion()['id_usuario'],
            fecha,
            observaciones.strip() or None,
        )
        return True, None
    except Exception as e:
        return False, f"Error al registrar el traslado: {e}"