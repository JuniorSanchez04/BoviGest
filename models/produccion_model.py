from config.database import get_connection


# ── Consultas de GMD ───────────────────────────────────────────

def listar_gmd_animales() -> list[dict]:
    """
    Retorna todos los animales activos que tienen al menos dos pesajes,
    con su GMD calculada a partir de los dos últimos registros.
    Animales con un solo pesaje quedan excluidos (no hay GMD calculable).
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.id_animal,
            a.caravana,
            c.nombre                AS categoria,
            COALESCE(l.nombre, '—') AS lote,
            p1.fecha                AS ultimo_pesaje,
            p1.peso_kg              AS peso_actual,
            p2.fecha                AS pesaje_anterior,
            p2.peso_kg              AS peso_anterior,
            DATEDIFF(p1.fecha, p2.fecha) AS dias_entre_pesajes,
            ROUND(
                (p1.peso_kg - p2.peso_kg)
                / NULLIF(DATEDIFF(p1.fecha, p2.fecha), 0),
            3) AS gmd_kg_dia
        FROM  animales   a
        JOIN  categorias c  ON c.id_categoria = a.id_categoria
        LEFT JOIN lotes  l  ON l.id_lote      = a.id_lote
        -- Último pesaje
        JOIN  pesajes    p1 ON p1.id_animal   = a.id_animal
            AND p1.fecha = (
                SELECT MAX(px.fecha) FROM pesajes px
                WHERE  px.id_animal = a.id_animal
            )
        -- Penúltimo pesaje
        JOIN  pesajes    p2 ON p2.id_animal   = a.id_animal
            AND p2.fecha = (
                SELECT MAX(py.fecha) FROM pesajes py
                WHERE  py.id_animal = a.id_animal
                  AND  py.fecha < p1.fecha
            )
        WHERE a.activo = TRUE
        ORDER BY gmd_kg_dia DESC
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def gmd_por_lote() -> list[dict]:
    """
    Retorna estadísticas de GMD agrupadas por lote:
    cantidad, promedio, mínima y máxima.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            l.nombre AS lote,
            COUNT(a.id_animal) AS animales_con_gmd,
            ROUND(AVG(
                (p1.peso_kg - p2.peso_kg)
                / NULLIF(DATEDIFF(p1.fecha, p2.fecha), 0)
            ), 3) AS gmd_promedio,
            ROUND(MIN(
                (p1.peso_kg - p2.peso_kg)
                / NULLIF(DATEDIFF(p1.fecha, p2.fecha), 0)
            ), 3) AS gmd_minima,
            ROUND(MAX(
                (p1.peso_kg - p2.peso_kg)
                / NULLIF(DATEDIFF(p1.fecha, p2.fecha), 0)
            ), 3) AS gmd_maxima
        FROM  animales   a
        JOIN  lotes      l  ON l.id_lote      = a.id_lote
        JOIN  pesajes    p1 ON p1.id_animal   = a.id_animal
            AND p1.fecha = (
                SELECT MAX(px.fecha) FROM pesajes px
                WHERE  px.id_animal = a.id_animal
            )
        JOIN  pesajes    p2 ON p2.id_animal   = a.id_animal
            AND p2.fecha = (
                SELECT MAX(py.fecha) FROM pesajes py
                WHERE  py.id_animal = a.id_animal
                  AND  py.fecha < p1.fecha
            )
        WHERE a.activo = TRUE
        GROUP BY l.id_lote, l.nombre
        ORDER BY gmd_promedio DESC
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def historial_pesajes_animal(id_animal: int) -> list[dict]:
    """
    Retorna todos los pesajes de un animal con la GMD de cada período.
    Usa la función de ventana LAG() de MySQL 8.0+ para comparar
    cada pesaje con el anterior sin necesidad de una subconsulta.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pe.fecha,
            pe.peso_kg,
            LAG(pe.peso_kg) OVER (ORDER BY pe.fecha) AS peso_anterior,
            LAG(pe.fecha)   OVER (ORDER BY pe.fecha) AS fecha_anterior,
            ROUND(
                (pe.peso_kg - LAG(pe.peso_kg) OVER (ORDER BY pe.fecha))
                / NULLIF(
                    DATEDIFF(pe.fecha, LAG(pe.fecha) OVER (ORDER BY pe.fecha)),
                  0),
            3) AS gmd_periodo
        FROM  pesajes pe
        WHERE pe.id_animal = %s
        ORDER BY pe.fecha ASC
    """, (id_animal,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def animales_sin_pesaje_reciente(dias: int = 30) -> list[dict]:
    """
    Animales activos que no han sido pesados en los últimos N días,
    o que nunca fueron pesados.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.id_animal,
            a.caravana,
            c.nombre                AS categoria,
            COALESCE(l.nombre, '—') AS lote,
            MAX(pe.fecha)           AS ultimo_pesaje,
            DATEDIFF(CURDATE(), MAX(pe.fecha)) AS dias_sin_pesar
        FROM  animales   a
        JOIN  categorias c  ON c.id_categoria = a.id_categoria
        LEFT JOIN lotes  l  ON l.id_lote      = a.id_lote
        LEFT JOIN pesajes pe ON pe.id_animal  = a.id_animal
        WHERE a.activo = TRUE
        GROUP BY a.id_animal, a.caravana, c.nombre, l.nombre
        HAVING MAX(pe.fecha) IS NULL
            OR DATEDIFF(CURDATE(), MAX(pe.fecha)) > %s
        ORDER BY dias_sin_pesar DESC
    """, (dias,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# ── Registro de pesajes ────────────────────────────────────────

def animal_ya_pesado_en_fecha(id_animal: int, fecha: str) -> bool:
    """
    Verifica si un animal ya tiene pesaje registrado en esa fecha.
    Evita el error de la constraint UNIQUE antes de intentar insertar.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM pesajes WHERE id_animal = %s AND fecha = %s",
        (id_animal, fecha)
    )
    conteo = cursor.fetchone()[0]
    cursor.close()
    return conteo > 0


def registrar_pesaje(datos: dict, id_usuario: int) -> None:
    """Inserta un pesaje individual. Autocommit maneja la transacción."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pesajes (id_animal, fecha, peso_kg, id_usuario, observaciones)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        datos['id_animal'],
        datos['fecha'],
        datos['peso_kg'],
        id_usuario,
        datos.get('observaciones'),
    ))
    cursor.close()


def registrar_pesajes_masivo(lista: list[dict], id_usuario: int) -> int:
    """
    Inserta múltiples pesajes en una sola transacción.
    Si cualquier INSERT falla, se deshacen todos.
    Retorna la cantidad de pesajes insertados.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    conn.autocommit = False
    try:
        for item in lista:
            cursor.execute("""
                INSERT INTO pesajes (id_animal, fecha, peso_kg, id_usuario, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                item['id_animal'],
                item['fecha'],
                item['peso_kg'],
                id_usuario,
                item.get('observaciones'),
            ))
        conn.commit()
        return len(lista)
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.autocommit = True