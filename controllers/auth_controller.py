from models.usuario_model import buscar_usuario_por_credenciales, cargar_permisos
from core.session import iniciar_sesion, cerrar_sesion
from utils.hash_helper import hashear_password


def login(username: str, password: str) -> tuple[bool, str | None]:
    """
    Valida credenciales y carga la sesión si son correctas.

    Retorna:
        (True,  None)           — login exitoso
        (False, mensaje_error)  — login fallido
    """
    # ── Validación de campos vacíos ───────────────────────────
    if not username.strip():
        return False, "Ingresá tu nombre de usuario."

    if not password.strip():
        return False, "Ingresá tu contraseña."

    # ── Consulta a la base de datos ───────────────────────────
    password_hash = hashear_password(password)
    usuario = buscar_usuario_por_credenciales(username.strip(), password_hash)

    if usuario is None:
        return False, "Usuario o contraseña incorrectos."

    # ── Cargar permisos y abrir sesión ────────────────────────
    permisos = cargar_permisos(usuario['id_usuario'])

    iniciar_sesion({
        'id_usuario': usuario['id_usuario'],
        'username':   usuario['username'],
        'nombre':     usuario['nombre'],
        'apellido':   usuario['apellido'],
        'rol':        usuario['rol'],
        'permisos':   permisos,
    })

    return True, None


def logout() -> None:
    """Cierra la sesión activa."""
    cerrar_sesion()