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


def obtener_farmacos() -> list[dict]:
    """Incluye dias_carencia y unidad_medida para los formularios de tratamiento."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_farmaco, nombre, dias_carencia, unidad_medida
        FROM farmacos ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_diagnosticos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_diagnostico, nombre FROM diagnosticos ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_vacunas() -> list[dict]:
    """Incluye intervalo_revacunacion para calcular la próxima fecha automáticamente."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_vacuna, nombre, intervalo_revacunacion
        FROM vacunas ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# ── Catálogos sanitarios ────────────────────────────────────────

def obtener_farmacos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_farmaco, nombre, principio_activo,
               dias_carencia, unidad_medida
        FROM farmacos ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_diagnosticos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_diagnostico, nombre FROM diagnosticos ORDER BY nombre"
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_vacunas_lista() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_vacuna, nombre, intervalo_revacunacion
        FROM vacunas ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_farmaco_por_id(id_farmaco: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM farmacos WHERE id_farmaco = %s", (id_farmaco,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def obtener_vacuna_por_id(id_vacuna: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM vacunas WHERE id_vacuna = %s", (id_vacuna,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def obtener_farmacos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_farmaco, nombre, dias_carencia, unidad_medida
        FROM farmacos ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_diagnosticos() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_diagnostico, nombre FROM diagnosticos ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_vacunas() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_vacuna, nombre, intervalo_revacunacion
        FROM vacunas ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado