from config.database import get_connection


# Busca usuario por credenciales (sin filtrar por activo); usada en login()
def buscar_usuario_por_credenciales(username: str, password_hash: str) -> dict | None:

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            u.id_usuario,
            u.username,
            u.activo,
            p.nombre,
            p.apellido,
            r.nombre AS rol
        FROM  usuarios  u
        JOIN  personas  p ON p.id_persona = u.id_persona
        JOIN  roles     r ON r.id_rol     = u.id_rol
        WHERE u.username      = %s
          AND u.password_hash = %s
    """
    cursor.execute(query, (username, password_hash))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado


# Trae los permisos del rol del usuario logueado
def cargar_permisos(id_usuario: int) -> set:
    """
    Carga todas las claves de permiso asignadas al rol del usuario.
    Retorna un set de strings: {'inventario.crear', 'sanidad.consultar', ...}
    """
    conn   = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT pe.clave
        FROM  usuarios    u
        JOIN  rol_permiso rp ON rp.id_rol     = u.id_rol
        JOIN  permisos    pe ON pe.id_permiso = rp.id_permiso
        WHERE u.id_usuario = %s
    """
    cursor.execute(query, (id_usuario,))
    permisos = {fila[0] for fila in cursor.fetchall()}
    cursor.close()
    return permisos



# Trae todos los usuarios con su persona y rol, para la tabla

def listar_usuarios() -> list[dict]:
    """Retorna todos los usuarios con datos de persona y rol."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            u.id_usuario,
            u.username,
            u.activo,
            p.nombre,
            p.apellido,
            p.ci,
            p.email,
            r.id_rol,
            r.nombre AS rol
        FROM  usuarios  u
        JOIN  personas  p ON p.id_persona = u.id_persona
        JOIN  roles     r ON r.id_rol     = u.id_rol
        ORDER BY p.apellido, p.nombre
    """
    cursor.execute(query)
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado


# Trae los roles, para el combobox del formulario
def listar_roles() -> list[dict]:
    """Retorna todos los roles disponibles (para el combobox del formulario)."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_rol, nombre FROM roles ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado


# Crea persona + usuario en una sola transacción
def crear_usuario(datos: dict) -> int:
    """
    Crea una persona y su usuario asociado en una sola transacción.
    Si falla el insert de usuarios, se revierte también el de personas.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO personas (nombre, apellido, ci, telefono, email)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (datos['nombre'], datos['apellido'], datos['ci'],
             datos.get('telefono'), datos.get('email'))
        )
        id_persona = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO usuarios (username, password_hash, id_persona, id_rol)
            VALUES (%s, %s, %s, %s)
            """,
            (datos['username'], datos['password_hash'], id_persona, datos['id_rol'])
        )
        id_usuario = cursor.lastrowid

        conn.commit()
        return id_usuario

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# Actualiza username y rol de un usuario existente
def actualizar_usuario(id_usuario: int, datos: dict) -> None:
    """Actualiza username y/o rol de un usuario existente."""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET username = %s, id_rol = %s WHERE id_usuario = %s",
        (datos['username'], datos['id_rol'], id_usuario)
    )
    conn.commit()
    cursor.close()
    conn.close()


# Activa o desactiva un usuario (baja lógica)
def cambiar_estado_usuario(id_usuario: int, activo: bool) -> None:

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET activo = %s WHERE id_usuario = %s",
        (activo, id_usuario)
    )
    conn.commit()
    cursor.close()
    conn.close()