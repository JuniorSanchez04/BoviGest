import hashlib


def hashear_password(password: str) -> str:
    """
    Retorna el hash SHA-256 de la contraseña en hexadecimal.
    Este mismo algoritmo se usa al crear usuarios y al hacer login.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()