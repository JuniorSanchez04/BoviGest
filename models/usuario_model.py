from config.database import get_connection


def buscar_usuario_por_credenciales(username: str, password_hash: str) -> dict | None:
    """
    Busca un usuario activo que coincida con username y password_hash.
    Retorna un diccionario con los datos o None si no existe.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            u.id_usuario,
            u.username,
            p.nombre,
            p.apellido,
            r.nombre AS rol
        FROM  usuarios  u
        JOIN  personas  p ON p.id_persona = u.id_persona
        JOIN  roles     r ON r.id_rol     = u.id_rol
        WHERE u.username      = %s
          AND u.password_hash = %s
          AND u.activo        = TRUE
    """
    cursor.execute(query, (username, password_hash))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


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