# ── Sesión activa ─────────────────────────────────────────────
# Almacena los datos del usuario logueado en memoria durante la
# ejecución. Se limpia al cerrar sesión o salir del sistema.

_sesion = {
    'id_usuario': None,
    'username':   None,
    'nombre':     None,
    'apellido':   None,
    'rol':        None,
    'permisos':   set(),   # conjunto de claves: {'inventario.crear', ...}
}


def iniciar_sesion(datos: dict) -> None:
    """Carga los datos del usuario autenticado en la sesión."""
    _sesion.update(datos)


def cerrar_sesion() -> None:
    """Resetea la sesión a su estado inicial."""
    _sesion.update({
        'id_usuario': None,
        'username':   None,
        'nombre':     None,
        'apellido':   None,
        'rol':        None,
        'permisos':   set(),
    })


def get_sesion() -> dict:
    """Retorna el diccionario de sesión completo."""
    return _sesion


def tiene_permiso(clave: str) -> bool:
    """
    Verifica si el usuario logueado tiene un permiso específico.
    Uso: if tiene_permiso('inventario.crear'): ...
    """
    return clave in _sesion['permisos']


def esta_logueado() -> bool:
    """Retorna True si hay un usuario en sesión."""
    return _sesion['id_usuario'] is not None


def nombre_completo() -> str:
    """Retorna 'Nombre Apellido' del usuario logueado."""
    return f"{_sesion['nombre']} {_sesion['apellido']}"