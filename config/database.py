import mysql.connector
from mysql.connector import Error

# ── Configuración de conexión ─────────────────────────────────
# Ajustar user/password según el entorno local.
DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'database': 'bovigest',
    'user':     'root',
    'password': 'admin123',
    'autocommit': True,
    'charset':  'utf8mb4',
}

_connection = None


def get_connection():
    """
    Retorna la conexión activa. Si no existe o se cortó, la (re)abre.
    Lanza ConnectionError con mensaje legible si MySQL no está disponible.
    """
    global _connection
    try:
        if _connection is None or not _connection.is_connected():
            _connection = mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise ConnectionError(
            f"No se pudo conectar a la base de datos.\n"
            f"Verificá que MySQL esté activo y que las credenciales en\n"
            f"config/database.py sean correctas.\n\nDetalle: {e}"
        )
    return _connection


def close_connection():
    """Cierra la conexión si está abierta."""
    global _connection
    if _connection and _connection.is_connected():
        _connection.close()
        _connection = None