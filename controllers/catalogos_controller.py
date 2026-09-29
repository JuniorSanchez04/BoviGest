import mysql.connector

from models import catalogos_model as modelo


def _error_bd(error: mysql.connector.Error) -> str:
    """Traduce errores comunes de MySQL a un mensaje para el usuario."""
    if error.errno == 1062:
        return "Ya existe un registro con ese nombre."
    if error.errno in (1451, 1217):
        return "No se puede modificar ni eliminar: hay registros que lo están usando."
    return "Error de base de datos."


# ── Razas ──────────────────────────────────────────────────

def listar_razas() -> list[dict]:
    return modelo.listar_razas()


def crear_raza(nombre: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.crear_raza(nombre.strip())
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_raza(id_raza: int, nombre: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.actualizar_raza(id_raza, nombre.strip())
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_raza(id_raza: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_raza(id_raza)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Sexos (solo lectura) ───────────────────────────────────

def listar_sexos() -> list[dict]:
    return modelo.listar_sexos()


# ── Categorías ─────────────────────────────────────────────

def listar_categorias() -> list[dict]:
    return modelo.listar_categorias()


def crear_categoria(nombre: str, descripcion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.crear_categoria(nombre.strip(), descripcion.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_categoria(id_categoria: int, nombre: str,
                         descripcion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.actualizar_categoria(id_categoria, nombre.strip(),
                                    descripcion.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_categoria(id_categoria: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_categoria(id_categoria)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Vacunas ────────────────────────────────────────────────

def listar_vacunas() -> list[dict]:
    return modelo.listar_vacunas()


def crear_vacuna(nombre: str, laboratorio: str, intervalo_revacunacion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    intervalo = None
    if intervalo_revacunacion.strip():
        if not intervalo_revacunacion.strip().isdigit() or int(intervalo_revacunacion) <= 0:
            return False, "El intervalo de revacunación debe ser un número mayor a 0."
        intervalo = int(intervalo_revacunacion)
    try:
        modelo.crear_vacuna(nombre.strip(), laboratorio.strip() or None, intervalo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_vacuna(id_vacuna: int, nombre: str, laboratorio: str,
                      intervalo_revacunacion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    intervalo = None
    if intervalo_revacunacion.strip():
        if not intervalo_revacunacion.strip().isdigit() or int(intervalo_revacunacion) <= 0:
            return False, "El intervalo de revacunación debe ser un número mayor a 0."
        intervalo = int(intervalo_revacunacion)
    try:
        modelo.actualizar_vacuna(id_vacuna, nombre.strip(),
                                 laboratorio.strip() or None, intervalo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_vacuna(id_vacuna: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_vacuna(id_vacuna)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)

# ── Lotes / Potreros ───────────────────────────────────────

def listar_lotes() -> list[dict]:
    return modelo.listar_lotes()


def crear_lote(nombre: str, descripcion: str, capacidad: str,
              activo: bool) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    cap = None
    if capacidad.strip():
        if not capacidad.strip().isdigit() or int(capacidad) <= 0:
            return False, "La capacidad debe ser un número mayor a 0."
        cap = int(capacidad)
    try:
        modelo.crear_lote(nombre.strip(), descripcion.strip() or None, cap, activo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_lote(id_lote: int, nombre: str, descripcion: str,
                    capacidad: str, activo: bool) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    cap = None
    if capacidad.strip():
        if not capacidad.strip().isdigit() or int(capacidad) <= 0:
            return False, "La capacidad debe ser un número mayor a 0."
        cap = int(capacidad)
    try:
        modelo.actualizar_lote(id_lote, nombre.strip(), descripcion.strip() or None,
                               cap, activo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_lote(id_lote: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_lote(id_lote)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Motivos de baja ────────────────────────────────────────

def listar_motivos_baja() -> list[dict]:
    return modelo.listar_motivos_baja()


def crear_motivo_baja(nombre: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.crear_motivo_baja(nombre.strip())
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_motivo_baja(id_motivo_baja: int, nombre: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.actualizar_motivo_baja(id_motivo_baja, nombre.strip())
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_motivo_baja(id_motivo_baja: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_motivo_baja(id_motivo_baja)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Tipos de movimiento (solo lectura) ─────────────────────

def listar_tipos_movimiento() -> list[dict]:
    return modelo.listar_tipos_movimiento()


# ── Fármacos ───────────────────────────────────────────────

def listar_farmacos() -> list[dict]:
    return modelo.listar_farmacos()


def crear_farmaco(nombre: str, principio_activo: str, dias_carencia: str,
                  unidad_medida: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    if not dias_carencia.strip().isdigit():
        return False, "Los días de carencia deben ser un número entero."
    dias = int(dias_carencia)
    if dias < 0:
        return False, "Los días de carencia no pueden ser negativos."
    try:
        modelo.crear_farmaco(nombre.strip(), principio_activo.strip() or None,
                             dias, unidad_medida.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_farmaco(id_farmaco: int, nombre: str, principio_activo: str,
                       dias_carencia: str, unidad_medida: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    if not dias_carencia.strip().isdigit():
        return False, "Los días de carencia deben ser un número entero."
    dias = int(dias_carencia)
    if dias < 0:
        return False, "Los días de carencia no pueden ser negativos."
    try:
        modelo.actualizar_farmaco(id_farmaco, nombre.strip(),
                                  principio_activo.strip() or None, dias,
                                  unidad_medida.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_farmaco(id_farmaco: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_farmaco(id_farmaco)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Diagnósticos ───────────────────────────────────────────

def listar_diagnosticos() -> list[dict]:
    return modelo.listar_diagnosticos()


def crear_diagnostico(nombre: str, descripcion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.crear_diagnostico(nombre.strip(), descripcion.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_diagnostico(id_diagnostico: int, nombre: str,
                           descripcion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    try:
        modelo.actualizar_diagnostico(id_diagnostico, nombre.strip(),
                                      descripcion.strip() or None)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_diagnostico(id_diagnostico: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_diagnostico(id_diagnostico)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


# ── Vacunas ────────────────────────────────────────────────

def listar_vacunas() -> list[dict]:
    return modelo.listar_vacunas()


def crear_vacuna(nombre: str, laboratorio: str, intervalo_revacunacion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    intervalo = None
    if intervalo_revacunacion.strip():
        if not intervalo_revacunacion.strip().isdigit() or int(intervalo_revacunacion) <= 0:
            return False, "El intervalo de revacunación debe ser un número mayor a 0."
        intervalo = int(intervalo_revacunacion)
    try:
        modelo.crear_vacuna(nombre.strip(), laboratorio.strip() or None, intervalo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def actualizar_vacuna(id_vacuna: int, nombre: str, laboratorio: str,
                      intervalo_revacunacion: str) -> tuple[bool, str | None]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    intervalo = None
    if intervalo_revacunacion.strip():
        if not intervalo_revacunacion.strip().isdigit() or int(intervalo_revacunacion) <= 0:
            return False, "El intervalo de revacunación debe ser un número mayor a 0."
        intervalo = int(intervalo_revacunacion)
    try:
        modelo.actualizar_vacuna(id_vacuna, nombre.strip(),
                                 laboratorio.strip() or None, intervalo)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)


def eliminar_vacuna(id_vacuna: int) -> tuple[bool, str | None]:
    try:
        modelo.eliminar_vacuna(id_vacuna)
        return True, None
    except mysql.connector.Error as error:
        return False, _error_bd(error)