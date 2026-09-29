from models import usuario_model
from core.session import tiene_permiso
from utils.hash_helper import hashear_password


# ── Obtiene la lista completa de usuarios registrados en el sistema ──
def listar_usuarios() -> list[dict]:
    return usuario_model.listar_usuarios()


# ── Obtiene la lista de roles disponibles para asignar a un usuario ──
def listar_roles() -> list[dict]:
    return usuario_model.listar_roles()


# ── Crea un nuevo usuario en la base de datos previa validación de campos y permisos ──
def crear_usuario(nombre, apellido, ci, telefono, email,
                   username, password, id_rol) -> tuple[bool, str]:
    if not tiene_permiso('acceso.crear'):
        return False, "No tenés permiso para crear usuarios."

    if not nombre or not apellido or not ci:
        return False, "Nombre, apellido y CI son obligatorios."
    if not username or not password:
        return False, "Username y contraseña son obligatorios."
    if id_rol is None:
        return False, "Debés seleccionar un rol."

    try:
        datos = {
            'nombre': nombre, 'apellido': apellido, 'ci': ci,
            'telefono': telefono or None, 'email': email or None,
            'username': username,
            'password_hash': hashear_password(password),
            'id_rol': id_rol,
        }
        usuario_model.crear_usuario(datos)
        return True, ""
    except Exception as e:
        return False, f"No se pudo crear el usuario: {e}"




# ── Actualiza los datos de un usuario existente (username y rol) previa validación ──
def actualizar_usuario(id_usuario, username, id_rol) -> tuple[bool, str]:
    if not tiene_permiso('acceso.modificar'):
        return False, "No tenés permiso para modificar usuarios."

    if not username:
        return False, "El username es obligatorio."
    if id_rol is None:
        return False, "Debés seleccionar un rol."

    try:
        usuario_model.actualizar_usuario(
            id_usuario, {'username': username, 'id_rol': id_rol})
        return True, ""
    except Exception as e:
        return False, f"No se pudo actualizar el usuario: {e}"


# ── Da de baja (inactiva) a un usuario para que no pueda acceder al sistema ──
def eliminar_usuario(id_usuario) -> tuple[bool, str]:
    if not tiene_permiso('acceso.eliminar'):
        return False, "No tenés permiso para dar de baja usuarios."

    try:
        usuario_model.cambiar_estado_usuario(id_usuario, activo=False)
        return True, ""
    except Exception as e:
        return False, f"No se pudo dar de baja al usuario: {e}"


# ── Reactiva a un usuario que estaba dado de baja para que pueda volver a ingresar ──
def activar_usuario(id_usuario) -> tuple[bool, str]:
    if not tiene_permiso('acceso.eliminar'):
        return False, "No tenés permiso para reactivar usuarios."

    try:
        usuario_model.cambiar_estado_usuario(id_usuario, activo=True)
        return True, ""
    except Exception as e:
        return False, f"No se pudo reactivar el usuario: {e}"