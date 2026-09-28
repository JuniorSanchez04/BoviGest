from config.database import get_connection


# ── Alertas ────────────────────────────────────────────────────

def animales_en_carencia() -> list[dict]:
    """
    Animales con período de carencia farmacológica activo hoy.
    NO pueden ser vendidos ni sacrificados hasta que venza la carencia.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.caravana,
            c.nombre                AS categoria,
            COALESCE(l.nombre, '—') AS lote,
            f.nombre                AS farmaco,
            t.fecha_inicio,
            t.fecha_fin_carencia,
            DATEDIFF(t.fecha_fin_carencia, CURDATE()) AS dias_restantes
        FROM  tratamientos  t
        JOIN  animales      a ON a.id_animal     = t.id_animal
        JOIN  categorias    c ON c.id_categoria  = a.id_categoria
        LEFT JOIN lotes     l ON l.id_lote       = a.id_lote
        JOIN  farmacos      f ON f.id_farmaco    = t.id_farmaco
        WHERE t.fecha_fin_carencia >= CURDATE()
          AND a.activo = TRUE
        ORDER BY t.fecha_fin_carencia ASC
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def vacunaciones_proximas(dias: int = 30) -> list[dict]:
    """
    Animales cuya próxima vacunación vence dentro de los próximos N días.
    Solo considera la vacunación MÁS RECIENTE de cada animal por vacuna.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.caravana,
            c.nombre                AS categoria,
            COALESCE(l.nombre, '—') AS lote,
            v.nombre                AS vacuna,
            vac.fecha_aplicacion,
            vac.proxima_fecha,
            DATEDIFF(vac.proxima_fecha, CURDATE()) AS dias_para_vencer
        FROM  vacunaciones  vac
        JOIN  animales      a ON a.id_animal    = vac.id_animal
        JOIN  categorias    c ON c.id_categoria = a.id_categoria
        LEFT JOIN lotes     l ON l.id_lote      = a.id_lote
        JOIN  vacunas       v ON v.id_vacuna    = vac.id_vacuna
        WHERE vac.proxima_fecha BETWEEN CURDATE()
                                    AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
          AND a.activo = TRUE
          AND vac.id_vacunacion = (
              SELECT MAX(v2.id_vacunacion)
              FROM   vacunaciones v2
              WHERE  v2.id_animal = vac.id_animal
                AND  v2.id_vacuna = vac.id_vacuna
          )
        ORDER BY vac.proxima_fecha ASC
    """, (dias,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def vacunaciones_vencidas() -> list[dict]:
    """
    Animales con vacunación atrasada (proxima_fecha < hoy).
    Solo la más reciente por animal por vacuna.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            a.caravana,
            c.nombre                AS categoria,
            COALESCE(l.nombre, '—') AS lote,
            v.nombre                AS vacuna,
            vac.fecha_aplicacion,
            vac.proxima_fecha,
            DATEDIFF(CURDATE(), vac.proxima_fecha) AS dias_vencida
        FROM  vacunaciones  vac
        JOIN  animales      a ON a.id_animal    = vac.id_animal
        JOIN  categorias    c ON c.id_categoria = a.id_categoria
        LEFT JOIN lotes     l ON l.id_lote      = a.id_lote
        JOIN  vacunas       v ON v.id_vacuna    = vac.id_vacuna
        WHERE vac.proxima_fecha < CURDATE()
          AND a.activo = TRUE
          AND vac.id_vacunacion = (
              SELECT MAX(v2.id_vacunacion)
              FROM   vacunaciones v2
              WHERE  v2.id_animal = vac.id_animal
                AND  v2.id_vacuna = vac.id_vacuna
          )
        ORDER BY dias_vencida DESC
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def animal_tiene_carencia_activa(id_animal: int) -> bool:
    """
    Verifica si un animal específico tiene carencia activa hoy.
    Usado por el módulo de inventario antes de registrar una baja por venta.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM tratamientos
        WHERE id_animal = %s AND fecha_fin_carencia >= CURDATE()
    """, (id_animal,))
    conteo = cursor.fetchone()[0]
    cursor.close()
    return conteo > 0


# ── Tratamientos ───────────────────────────────────────────────

def listar_tratamientos(busqueda: str = '') -> list[dict]:
    """Lista todos los tratamientos. Si se da una caravana, filtra por ese animal."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    condiciones = ['a.activo = TRUE']
    valores     = []

    if busqueda.strip():
        condiciones.append('a.caravana LIKE %s')
        valores.append(f'%{busqueda.strip().upper()}%')

    where = ' AND '.join(condiciones)

    cursor.execute(f"""
        SELECT
            a.caravana,
            c.nombre                     AS categoria,
            f.nombre                     AS farmaco,
            COALESCE(d.nombre, '—')      AS diagnostico,
            t.fecha_inicio,
            t.fecha_fin_carencia,
            DATEDIFF(t.fecha_fin_carencia, CURDATE()) AS dias_restantes,
            t.dosis,
            f.unidad_medida,
            CONCAT(p.nombre, ' ', p.apellido) AS registrado_por,
            t.observaciones
        FROM  tratamientos   t
        JOIN  animales       a ON a.id_animal       = t.id_animal
        JOIN  categorias     c ON c.id_categoria    = a.id_categoria
        JOIN  farmacos       f ON f.id_farmaco      = t.id_farmaco
        LEFT JOIN diagnosticos d ON d.id_diagnostico = t.id_diagnostico
        JOIN  usuarios       u ON u.id_usuario      = t.id_usuario
        JOIN  personas       p ON p.id_persona      = u.id_persona
        WHERE {where}
        ORDER BY t.fecha_inicio DESC
    """, valores)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def registrar_tratamiento(datos: dict, id_usuario: int) -> None:
    """Inserta un nuevo tratamiento. Autocommit maneja la transacción."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tratamientos
            (id_animal, id_farmaco, id_diagnostico, fecha_inicio,
             dosis, fecha_fin_carencia, id_usuario, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        datos['id_animal'],
        datos['id_farmaco'],
        datos.get('id_diagnostico'),
        datos['fecha_inicio'],
        datos.get('dosis'),
        datos['fecha_fin_carencia'],
        id_usuario,
        datos.get('observaciones'),
    ))
    cursor.close()


# ── Vacunaciones ───────────────────────────────────────────────

def listar_vacunaciones(busqueda: str = '') -> list[dict]:
    """Lista todas las vacunaciones. Si se da una caravana, filtra por ese animal."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    condiciones = ['a.activo = TRUE']
    valores     = []

    if busqueda.strip():
        condiciones.append('a.caravana LIKE %s')
        valores.append(f'%{busqueda.strip().upper()}%')

    where = ' AND '.join(condiciones)

    cursor.execute(f"""
        SELECT
            a.caravana,
            c.nombre                     AS categoria,
            v.nombre                     AS vacuna,
            vac.fecha_aplicacion,
            vac.proxima_fecha,
            DATEDIFF(vac.proxima_fecha, CURDATE()) AS dias_estado,
            vac.lote_vacuna,
            CONCAT(p.nombre, ' ', p.apellido) AS registrado_por
        FROM  vacunaciones   vac
        JOIN  animales       a ON a.id_animal    = vac.id_animal
        JOIN  categorias     c ON c.id_categoria = a.id_categoria
        JOIN  vacunas        v ON v.id_vacuna    = vac.id_vacuna
        JOIN  usuarios       u ON u.id_usuario   = vac.id_usuario
        JOIN  personas       p ON p.id_persona   = u.id_persona
        WHERE {where}
        ORDER BY vac.fecha_aplicacion DESC
    """, valores)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def registrar_vacunacion(datos: dict, id_usuario: int) -> None:
    """Inserta un nuevo registro de vacunación."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vacunaciones
            (id_animal, id_vacuna, fecha_aplicacion,
             lote_vacuna, proxima_fecha, id_usuario, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        datos['id_animal'],
        datos['id_vacuna'],
        datos['fecha_aplicacion'],
        datos.get('lote_vacuna'),
        datos.get('proxima_fecha'),
        id_usuario,
        datos.get('observaciones'),
    ))
    cursor.close()