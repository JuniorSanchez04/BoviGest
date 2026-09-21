-- ============================================================
-- SEED: Usuario Administrador inicial de BoviGest
-- Ejecutar UNA SOLA VEZ después del script bovigest.sql
-- ============================================================

USE bovigest;

-- Contraseña por defecto: admin123
-- Hash SHA-256 de 'admin123':
-- 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- ⚠️  Cambiar la contraseña en el primer ingreso.

INSERT INTO personas (nombre, apellido, ci, telefono, email)
VALUES ('Administrador', 'BoviGest', '0000001', NULL, NULL);

INSERT INTO usuarios (username, password_hash, id_persona, id_rol)
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    (SELECT id_persona FROM personas WHERE ci = '0000001'),
    (SELECT id_rol     FROM roles    WHERE nombre = 'Administrador')
);

-- ============================================================
-- Para crear usuarios adicionales desde Python usar:
--
--   from utils.hash_helper import hashear_password
--   hash = hashear_password("contraseña_elegida")
--   # Luego insertar en personas + usuarios con ese hash
-- ============================================================