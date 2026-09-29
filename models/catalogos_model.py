from config.database import get_connection


# ── Razas ──────────────────────────────────────────────────

def listar_razas() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_raza, nombre FROM razas ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_raza(nombre: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO razas (nombre) VALUES (%s)", (nombre,))
    conn.commit()
    cursor.close()


def actualizar_raza(id_raza: int, nombre: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE razas SET nombre = %s WHERE id_raza = %s",
                   (nombre, id_raza))
    conn.commit()
    cursor.close()


def eliminar_raza(id_raza: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM razas WHERE id_raza = %s", (id_raza,))
    conn.commit()
    cursor.close()


# ── Sexos (solo lectura) ───────────────────────────────────

def listar_sexos() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_sexo, nombre FROM sexos ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas




# ── Categorías ─────────────────────────────────────────────

def listar_categorias() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_categoria, nombre, descripcion
        FROM categorias
        ORDER BY nombre
    """)
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_categoria(nombre: str, descripcion: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (nombre, descripcion) "
        "VALUES (%s, %s)", (nombre, descripcion))
    conn.commit()
    cursor.close()


def actualizar_categoria(id_categoria: int, nombre: str,
                         descripcion: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE categorias SET nombre = %s, descripcion = %s "
        "WHERE id_categoria = %s", (nombre, descripcion, id_categoria))
    conn.commit()
    cursor.close()


def eliminar_categoria(id_categoria: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id_categoria = %s",
                   (id_categoria,))
    conn.commit()
    cursor.close()

# ── Lotes / Potreros ───────────────────────────────────────

def listar_lotes() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_lote, nombre, descripcion, capacidad, activo "
        "FROM lotes ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_lote(nombre: str, descripcion: str | None, capacidad: int | None,
              activo: bool) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lotes (nombre, descripcion, capacidad, activo) "
        "VALUES (%s, %s, %s, %s)", (nombre, descripcion, capacidad, activo))
    conn.commit()
    cursor.close()


def actualizar_lote(id_lote: int, nombre: str, descripcion: str | None,
                    capacidad: int | None, activo: bool) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE lotes SET nombre = %s, descripcion = %s, capacidad = %s, "
        "activo = %s WHERE id_lote = %s",
        (nombre, descripcion, capacidad, activo, id_lote))
    conn.commit()
    cursor.close()


def eliminar_lote(id_lote: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lotes WHERE id_lote = %s", (id_lote,))
    conn.commit()
    cursor.close()


# ── Motivos de baja ────────────────────────────────────────

def listar_motivos_baja() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_motivo_baja, nombre FROM motivos_baja ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_motivo_baja(nombre: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO motivos_baja (nombre) VALUES (%s)", (nombre,))
    conn.commit()
    cursor.close()


def actualizar_motivo_baja(id_motivo_baja: int, nombre: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE motivos_baja SET nombre = %s WHERE id_motivo_baja = %s",
        (nombre, id_motivo_baja))
    conn.commit()
    cursor.close()


def eliminar_motivo_baja(id_motivo_baja: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM motivos_baja WHERE id_motivo_baja = %s",
                   (id_motivo_baja,))
    conn.commit()
    cursor.close()


# ── Tipos de movimiento (solo lectura) ─────────────────────

def listar_tipos_movimiento() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_tipo_movimiento, nombre FROM tipos_movimiento "
        "ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


# ── Fármacos ───────────────────────────────────────────────

def listar_farmacos() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_farmaco, nombre, principio_activo, dias_carencia, "
        "unidad_medida FROM farmacos ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_farmaco(nombre: str, principio_activo: str | None,
                  dias_carencia: int, unidad_medida: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO farmacos (nombre, principio_activo, dias_carencia, "
        "unidad_medida) VALUES (%s, %s, %s, %s)",
        (nombre, principio_activo, dias_carencia, unidad_medida))
    conn.commit()
    cursor.close()


def actualizar_farmaco(id_farmaco: int, nombre: str,
                       principio_activo: str | None, dias_carencia: int,
                       unidad_medida: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE farmacos SET nombre = %s, principio_activo = %s, "
        "dias_carencia = %s, unidad_medida = %s WHERE id_farmaco = %s",
        (nombre, principio_activo, dias_carencia, unidad_medida, id_farmaco))
    conn.commit()
    cursor.close()


def eliminar_farmaco(id_farmaco: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM farmacos WHERE id_farmaco = %s", (id_farmaco,))
    conn.commit()
    cursor.close()


# ── Diagnósticos ───────────────────────────────────────────

def listar_diagnosticos() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_diagnostico, nombre, descripcion FROM diagnosticos "
        "ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_diagnostico(nombre: str, descripcion: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diagnosticos (nombre, descripcion) VALUES (%s, %s)",
        (nombre, descripcion))
    conn.commit()
    cursor.close()


def actualizar_diagnostico(id_diagnostico: int, nombre: str,
                           descripcion: str | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE diagnosticos SET nombre = %s, descripcion = %s "
        "WHERE id_diagnostico = %s", (nombre, descripcion, id_diagnostico))
    conn.commit()
    cursor.close()


def eliminar_diagnostico(id_diagnostico: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diagnosticos WHERE id_diagnostico = %s",
                   (id_diagnostico,))
    conn.commit()
    cursor.close()


# ── Vacunas ────────────────────────────────────────────────

def listar_vacunas() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_vacuna, nombre, laboratorio, intervalo_revacunacion "
        "FROM vacunas ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    return filas


def crear_vacuna(nombre: str, laboratorio: str | None,
                 intervalo_revacunacion: int | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vacunas (nombre, laboratorio, intervalo_revacunacion) "
        "VALUES (%s, %s, %s)",
        (nombre, laboratorio, intervalo_revacunacion))
    conn.commit()
    cursor.close()


def actualizar_vacuna(id_vacuna: int, nombre: str, laboratorio: str | None,
                      intervalo_revacunacion: int | None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE vacunas SET nombre = %s, laboratorio = %s, "
        "intervalo_revacunacion = %s WHERE id_vacuna = %s",
        (nombre, laboratorio, intervalo_revacunacion, id_vacuna))
    conn.commit()
    cursor.close()


def eliminar_vacuna(id_vacuna: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vacunas WHERE id_vacuna = %s", (id_vacuna,))
    conn.commit()
    cursor.close()