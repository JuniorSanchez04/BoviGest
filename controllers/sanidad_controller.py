from datetime import datetime, timedelta

from models import sanidad_model, catalogo_model
from models.animal_model import buscar_activo_por_caravana
from core.session import get_sesion
from utils.fecha_helper import parsear, formatear


# ── Catálogos ──────────────────────────────────────────────────

def cargar_catalogos_sanidad() -> dict:
    """Devuelve los catálogos necesarios para los formularios del módulo."""
    return {
        'farmacos':     catalogo_model.obtener_farmacos(),
        'diagnosticos': catalogo_model.obtener_diagnosticos(),
        'vacunas':      catalogo_model.obtener_vacunas(),
    }


# ── Búsqueda de animal ─────────────────────────────────────────

def buscar_animal(caravana: str) -> tuple[dict | None, str | None]:
    """
    Busca un animal activo por caravana.
    Retorna (animal, None) si lo encuentra o (None, mensaje_error) si no.
    """
    if not caravana.strip():
        return None, "Ingresá el número de caravana."
    animal = buscar_activo_por_caravana(caravana)
    if animal is None:
        return None, f"No se encontró ningún animal activo con la caravana «{caravana.upper()}»."
    return animal, None


# ── Alertas ────────────────────────────────────────────────────

def resumen_alertas() -> dict:
    """
    Retorna los conteos de los tres tipos de alerta para las tarjetas del dashboard.
    """
    return {
        'en_carencia': len(sanidad_model.animales_en_carencia()),
        'proximas':    len(sanidad_model.vacunaciones_proximas(30)),
        'vencidas':    len(sanidad_model.vacunaciones_vencidas()),
    }


def alertas_carencia() -> list[dict]:
    return sanidad_model.animales_en_carencia()


def alertas_proximas() -> list[dict]:
    return sanidad_model.vacunaciones_proximas(30)


def alertas_vencidas() -> list[dict]:
    return sanidad_model.vacunaciones_vencidas()


# ── Listados ───────────────────────────────────────────────────

def listar_tratamientos(busqueda: str = '') -> list[dict]:
    return sanidad_model.listar_tratamientos(busqueda)


def listar_vacunaciones(busqueda: str = '') -> list[dict]:
    return sanidad_model.listar_vacunaciones(busqueda)


# ── Cálculos automáticos de fecha ──────────────────────────────

def calcular_fin_carencia(fecha_inicio_str: str, dias_carencia: int) -> str | None:
    """
    Calcula la fecha de fin de carencia sumando días al inicio.
    Retorna la fecha en formato DD/MM/AAAA para mostrar en el formulario.
    """
    try:
        fecha_mysql = parsear(fecha_inicio_str)
        if fecha_mysql is None:
            return None
        fecha = datetime.strptime(fecha_mysql, '%Y-%m-%d')
        fin   = fecha + timedelta(days=dias_carencia)
        return formatear(fin.date())
    except Exception:
        return None


def calcular_proxima_vacunacion(fecha_aplicacion_str: str, intervalo_dias: int) -> str | None:
    """
    Calcula la próxima fecha de vacunación sumando el intervalo a la aplicación.
    Retorna la fecha en formato DD/MM/AAAA para mostrar en el formulario.
    """
    try:
        fecha_mysql = parsear(fecha_aplicacion_str)
        if fecha_mysql is None:
            return None
        fecha   = datetime.strptime(fecha_mysql, '%Y-%m-%d')
        proxima = fecha + timedelta(days=intervalo_dias)
        return formatear(proxima.date())
    except Exception:
        return None


# ── Registro de tratamiento ────────────────────────────────────

def registrar_tratamiento(datos_form: dict) -> tuple[bool, str | None]:
    """
    Valida y guarda un nuevo tratamiento.
    Retorna (True, None) en éxito o (False, mensaje) en error.
    """
    if not datos_form.get('id_animal'):
        return False, "Buscá y seleccioná un animal primero."

    if not datos_form.get('id_farmaco'):
        return False, "Seleccioná un fármaco."

    if not datos_form.get('fecha_inicio', '').strip():
        return False, "La fecha de inicio es obligatoria."

    if not datos_form.get('fecha_fin_carencia', '').strip():
        return False, "La fecha de fin de carencia es obligatoria."

    # Parsear fechas
    try:
        fecha_inicio   = parsear(datos_form['fecha_inicio'])
        fecha_carencia = parsear(datos_form['fecha_fin_carencia'])
    except ValueError as e:
        return False, str(e)

    # La fecha de carencia no puede ser anterior al inicio
    if fecha_carencia and fecha_inicio and fecha_carencia < fecha_inicio:
        return False, "La fecha de fin de carencia no puede ser anterior a la fecha de inicio."

    # Parsear dosis (campo numérico opcional)
    dosis = None
    dosis_str = datos_form.get('dosis', '').strip()
    if dosis_str:
        try:
            dosis = float(dosis_str.replace(',', '.'))
            if dosis <= 0:
                return False, "La dosis debe ser un número positivo."
        except ValueError:
            return False, "La dosis debe ser un número válido (ej: 5 o 2.5)."

    datos = {
        'id_animal':         datos_form['id_animal'],
        'id_farmaco':        datos_form['id_farmaco'],
        'id_diagnostico':    datos_form.get('id_diagnostico'),
        'fecha_inicio':      fecha_inicio,
        'dosis':             dosis,
        'fecha_fin_carencia': fecha_carencia,
        'observaciones':     datos_form.get('observaciones', '').strip() or None,
    }

    try:
        sanidad_model.registrar_tratamiento(datos, get_sesion()['id_usuario'])
        return True, None
    except Exception as e:
        return False, f"Error al guardar: {e}"


# ── Registro de vacunación ─────────────────────────────────────

def registrar_vacunacion(datos_form: dict) -> tuple[bool, str | None]:
    """
    Valida y guarda una nueva vacunación.
    """
    if not datos_form.get('id_animal'):
        return False, "Buscá y seleccioná un animal primero."

    if not datos_form.get('id_vacuna'):
        return False, "Seleccioná una vacuna."

    if not datos_form.get('fecha_aplicacion', '').strip():
        return False, "La fecha de aplicación es obligatoria."

    try:
        fecha_aplicacion = parsear(datos_form['fecha_aplicacion'])
        proxima_fecha_str = datos_form.get('proxima_fecha', '').strip()
        proxima_fecha = parsear(proxima_fecha_str) if proxima_fecha_str and proxima_fecha_str != 'N/A (dosis única)' else None
    except ValueError as e:
        return False, str(e)

    datos = {
        'id_animal':       datos_form['id_animal'],
        'id_vacuna':       datos_form['id_vacuna'],
        'fecha_aplicacion': fecha_aplicacion,
        'lote_vacuna':     datos_form.get('lote_vacuna', '').strip() or None,
        'proxima_fecha':   proxima_fecha,
        'observaciones':   datos_form.get('observaciones', '').strip() or None,
    }

    try:
        sanidad_model.registrar_vacunacion(datos, get_sesion()['id_usuario'])
        return True, None
    except Exception as e:
        return False, f"Error al guardar: {e}"