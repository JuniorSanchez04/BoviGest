from config.database import get_connection


# ── Lectura ────────────────────────────────────────────────────

def listar_animales(
    id_lote: int | None = None,
    id_categoria: int | None = None,
    busqueda: str = '',
    solo_activos: bool = True,
) -> list[dict]:
    """
    Retorna la lista de animales aplicando filtros opcionales.
    Los filtros que llegan como None o cadena vacía se ignoran.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    condiciones = ['a.activo = %s']
    valores     = [solo_activos]

    if id_lote:
        condiciones.append('a.id_lote = %s')
        valores.append(id_lote)

    if id_categoria:
        condiciones.append('a.id_categoria = %s')
        valores.append(id_categoria)

    if busqueda.strip():
        condiciones.append('a.caravana LIKE %s')
        valores.append(f'%{busqueda.strip()}%')

    where = ' AND '.join(condiciones)

    query = f"""
        SELECT
            a.id_animal,
            a.caravana,
            COALESCE(r.nombre, '—') AS raza,
            c.nombre                AS categoria,
            s.nombre                AS sexo,
            a.fecha_nacimiento,
            a.fecha_alta,
            COALESCE(l.nombre, '—') AS lote,
            a.id_lote,
            a.activo,
            a.observaciones
        FROM  animales   a
        LEFT JOIN razas      r ON r.id_raza      = a.id_raza
        JOIN      categorias c ON c.id_categoria = a.id_categoria
        JOIN      sexos      s ON s.id_sexo      = a.id_sexo
        LEFT JOIN lotes      l ON l.id_lote      = a.id_lote
        WHERE {where}
        ORDER BY a.caravana
    """
    cursor.execute(query, valores)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def obtener_animal(id_animal: int) -> dict | None:
    """Retorna todos los datos de un animal por su ID."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.id_animal,
            a.caravana,
            a.id_raza,
            COALESCE(r.nombre, '—') AS raza,
            a.id_categoria,
            c.nombre                AS categoria,
            a.id_sexo,
            s.nombre                AS sexo,
            a.fecha_nacimiento,
            a.fecha_alta,
            a.id_lote,
            COALESCE(l.nombre, '—') AS lote,
            a.activo,
            a.observaciones
        FROM  animales   a
        LEFT JOIN razas      r ON r.id_raza      = a.id_raza
        JOIN      categorias c ON c.id_categoria = a.id_categoria
        JOIN      sexos      s ON s.id_sexo      = a.id_sexo
        LEFT JOIN lotes      l ON l.id_lote      = a.id_lote
        WHERE a.id_animal = %s
    """, (id_animal,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def obtener_historial_movimientos(id_animal: int) -> list[dict]:
    """Retorna todos los movimientos de un animal en orden cronológico."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            tm.nombre  AS tipo,
            ma.fecha,
            mb.nombre  AS motivo_baja,
            lo.nombre  AS lote_origen,
            ld.nombre  AS lote_destino,
            CONCAT(p.nombre, ' ', p.apellido) AS registrado_por,
            ma.observaciones
        FROM  movimientos_animales ma
        JOIN  tipos_movimiento  tm ON tm.id_tipo_movimiento = ma.id_tipo_movimiento
        LEFT JOIN motivos_baja  mb ON mb.id_motivo_baja    = ma.id_motivo_baja
        LEFT JOIN lotes         lo ON lo.id_lote           = ma.id_lote_origen
        LEFT JOIN lotes         ld ON ld.id_lote           = ma.id_lote_destino
        JOIN  usuarios           u ON u.id_usuario         = ma.id_usuario
        JOIN  personas           p ON p.id_persona         = u.id_persona
        WHERE ma.id_animal = %s
        ORDER BY ma.fecha DESC, ma.id_movimiento DESC
    """, (id_animal,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def contar_por_categoria() -> list[dict]:
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.nombre AS categoria, COUNT(a.id_animal) AS cantidad
        FROM  animales   a
        JOIN  categorias c ON c.id_categoria = a.id_categoria
        WHERE a.activo = TRUE
        GROUP BY c.id_categoria, c.nombre
        ORDER BY cantidad DESC
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# ── Escritura (con transacciones) ──────────────────────────────

def _id_tipo_movimiento(cursor, nombre: str) -> int:
    """Obtiene el id de un tipo de movimiento por su nombre."""
    cursor.execute(
        "SELECT id_tipo_movimiento FROM tipos_movimiento WHERE nombre = %s",
        (nombre,)
    )
    return cursor.fetchone()['id_tipo_movimiento']


def registrar_alta(datos: dict, id_usuario: int) -> int:
    """
    Inserta el animal y su movimiento de ALTA en una transacción.
    Retorna el id_animal generado.
    Lanza IntegrityError si la caravana ya existe.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    conn.autocommit = False
    try:
        cursor.execute("""
            INSERT INTO animales
                (caravana, id_raza, id_categoria, id_sexo,
                 fecha_nacimiento, fecha_alta, id_lote, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos['caravana'],
            datos.get('id_raza'),
            datos['id_categoria'],
            datos['id_sexo'],
            datos.get('fecha_nacimiento'),
            datos['fecha_alta'],
            datos.get('id_lote'),
            datos.get('observaciones'),
        ))
        id_animal = cursor.lastrowid

        cursor.execute("""
            INSERT INTO movimientos_animales
                (id_animal, id_tipo_movimiento, fecha, id_lote_destino, id_usuario)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_animal,
            _id_tipo_movimiento(cursor, 'ALTA'),
            datos['fecha_alta'],
            datos.get('id_lote'),
            id_usuario,
        ))

        conn.commit()
        return id_animal
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.autocommit = True


def registrar_baja(
    id_animal: int,
    id_motivo: int,
    id_usuario: int,
    fecha: str,
    observaciones: str | None,
) -> None:
    """
    Marca el animal como inactivo y registra el movimiento de BAJA.
    Guarda el lote en el que estaba antes de sacarlo del inventario.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    conn.autocommit = False
    try:
        # Obtener lote actual ANTES de limpiar el campo
        cursor.execute(
            "SELECT id_lote FROM animales WHERE id_animal = %s", (id_animal,)
        )
        id_lote_actual = cursor.fetchone()['id_lote']

        cursor.execute(
            "UPDATE animales SET activo = FALSE, id_lote = NULL WHERE id_animal = %s",
            (id_animal,)
        )

        cursor.execute("""
            INSERT INTO movimientos_animales
                (id_animal, id_tipo_movimiento, fecha,
                 id_motivo_baja, id_lote_origen, id_usuario, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_animal,
            _id_tipo_movimiento(cursor, 'BAJA'),
            fecha,
            id_motivo,
            id_lote_actual,
            id_usuario,
            observaciones,
        ))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.autocommit = True


def registrar_traslado(
    id_animal: int,
    id_lote_destino: int,
    id_usuario: int,
    fecha: str,
    observaciones: str | None,
) -> None:
    """
    Actualiza el lote del animal y registra el movimiento de TRASLADO.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    conn.autocommit = False
    try:
        # Lote de origen antes del cambio
        cursor.execute(
            "SELECT id_lote FROM animales WHERE id_animal = %s", (id_animal,)
        )
        id_lote_origen = cursor.fetchone()['id_lote']

        cursor.execute(
            "UPDATE animales SET id_lote = %s WHERE id_animal = %s",
            (id_lote_destino, id_animal)
        )

        cursor.execute("""
            INSERT INTO movimientos_animales
                (id_animal, id_tipo_movimiento, fecha,
                 id_lote_origen, id_lote_destino, id_usuario, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_animal,
            _id_tipo_movimiento(cursor, 'TRASLADO'),
            fecha,
            id_lote_origen,
            id_lote_destino,
            id_usuario,
            observaciones,
        ))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.autocommit = True


def buscar_por_caravana(caravana: str) -> dict | None:
    """
    Busca un animal activo por su número de caravana exacto.
    Usado por los formularios de sanidad para identificar el animal.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.id_animal,
            a.caravana,
            c.nombre                AS categoria,
            s.nombre                AS sexo,
            COALESCE(l.nombre, '—') AS lote,
            a.id_lote,
            a.activo
        FROM  animales   a
        JOIN  categorias c ON c.id_categoria = a.id_categoria
        JOIN  sexos      s ON s.id_sexo      = a.id_sexo
        LEFT JOIN lotes  l ON l.id_lote      = a.id_lote
        WHERE a.caravana = %s AND a.activo = TRUE
    """, (caravana.strip().upper(),))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def buscar_activo_por_caravana(caravana: str) -> dict | None:
    """
    Busca un animal activo por su número de caravana.
    Usado en los formularios de sanidad para identificar al animal.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.id_animal,
            a.caravana,
            c.nombre                AS categoria,
            s.nombre                AS sexo,
            COALESCE(l.nombre, 'Sin lote') AS lote
        FROM  animales   a
        JOIN  categorias c ON c.id_categoria = a.id_categoria
        JOIN  sexos      s ON s.id_sexo      = a.id_sexo
        LEFT JOIN lotes  l ON l.id_lote      = a.id_lote
        WHERE a.caravana = %s AND a.activo = TRUE
    """, (caravana.upper().strip(),))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado