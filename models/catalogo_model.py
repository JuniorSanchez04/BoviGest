from config.database import get_connection


def obtener_razas() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_raza, nombre FROM razas ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_categorias() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_sexos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_sexo, nombre FROM sexos ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_lotes_activos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_lote, nombre FROM lotes WHERE activo = TRUE ORDER BY nombre"
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_motivos_baja() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_motivo_baja, nombre FROM motivos_baja ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado