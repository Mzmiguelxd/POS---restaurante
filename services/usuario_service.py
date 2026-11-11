"""Registro, inicio de sesión y gestión del personal."""
import hashlib
import os
import re
from datetime import date, datetime
from models.usuario import Usuario

CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
CAMPOS = "id, nombres, apellidos, correo, rol, telefono, foto, estado, fecha_nacimiento"


class UsuarioService:
    ITERACIONES = 120_000
    ADMIN_CORREO = "admin@shunfa.pe"
    ADMIN_PASSWORD = "Admin123"

    def __init__(self, conexion):
        self.db = conexion

    # ---------- Contraseñas ----------
    @classmethod
    def _hash(cls, password, sal=None):
        sal = sal or os.urandom(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, cls.ITERACIONES)
        return f"{sal.hex()}${h.hex()}"

    @classmethod
    def _verificar(cls, password, guardado):
        try:
            sal_hex, _ = guardado.split("$", 1)
        except ValueError:
            return False
        return cls._hash(password, bytes.fromhex(sal_hex)) == guardado

    # ---------- Validaciones ----------
    @staticmethod
    def _validar_password(password, verificacion, errores, campo="password"):
        if len(password) < 6:
            errores[campo] = "Debe tener al menos 6 caracteres."
        elif not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
            errores[campo] = "Debe combinar letras y números."
        if verificacion != password:
            errores["verificacion"] = "Las contraseñas no coinciden."

    @staticmethod
    def parsear_fecha(texto):
        try:
            return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None

    # ---------- Registro / sesión ----------
    def registrar(self, nombres, apellidos, correo, password, verificacion, fecha_nac):
        """Devuelve (usuario, errores). errores es {campo: mensaje}."""
        nombres, apellidos, correo = nombres.strip(), apellidos.strip(), correo.strip().lower()
        errores = {}
        if not nombres:
            errores["nombres"] = "Ingrese sus nombres."
        if not apellidos:
            errores["apellidos"] = "Ingrese sus apellidos."
        if not CORREO_RE.match(correo):
            errores["correo"] = "Ingrese un correo válido (ej. nombre@correo.com)."
        elif self._buscar_por_correo(correo):
            errores["correo"] = "Ya existe una cuenta con este correo."
        self._validar_password(password, verificacion, errores)
        nacimiento = self.parsear_fecha(fecha_nac)
        if nacimiento is None:
            errores["fecha"] = "Use el formato DD/MM/AAAA."
        else:
            hoy = date.today()
            edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
            if nacimiento > hoy:
                errores["fecha"] = "La fecha no puede ser futura."
            elif edad < 16:
                errores["fecha"] = "Debe tener al menos 16 años."
        if errores:
            return None, errores
        nuevo_id = self.db.insertar(
            "INSERT INTO Usuario (nombres, apellidos, correo, password_hash, fecha_nacimiento, rol) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nombres, apellidos, correo, self._hash(password), nacimiento, Usuario.USUARIO))
        return self.obtener(nuevo_id), {}

    def iniciar_sesion(self, correo, password):
        correo = correo.strip().lower()
        errores = {}
        if not correo:
            errores["correo"] = "Ingrese su correo."
        if not password:
            errores["password"] = "Ingrese su contraseña."
        if errores:
            return None, errores
        filas = self.db.consultar(
            "SELECT id, password_hash, activo FROM Usuario WHERE correo = ?", (correo,))
        if not filas or not self._verificar(password, filas[0].password_hash):
            return None, {"password": "Correo o contraseña incorrectos."}
        if not filas[0].activo:
            return None, {"correo": "Esta cuenta está desactivada. Consulte al administrador."}
        self.db.ejecutar("UPDATE Usuario SET estado = 'TRABAJANDO' WHERE id = ?", (filas[0].id,))
        return self.obtener(filas[0].id), {}

    def cerrar_sesion(self, usuario):
        self.db.ejecutar("UPDATE Usuario SET estado = 'AUSENTE' WHERE id = ?", (usuario.id,))

    def asegurar_admin(self):
        """Crea el administrador inicial si no existe ninguno. Devuelve True si lo creó."""
        hay = self.db.consultar("SELECT COUNT(*) AS n FROM Usuario WHERE rol = 'ADMIN'")[0].n
        if hay:
            return False
        self.db.insertar(
            "INSERT INTO Usuario (nombres, apellidos, correo, password_hash, rol) VALUES (?, ?, ?, ?, ?)",
            ("Administrador", "Shun Fa", self.ADMIN_CORREO, self._hash(self.ADMIN_PASSWORD), Usuario.ADMIN))
        return True

    # ---------- Consultas ----------
    def _a_usuario(self, f):
        return Usuario(f.id, f.nombres, f.apellidos, f.correo, f.rol, f.telefono, f.foto,
                       f.estado, f.fecha_nacimiento)

    def _buscar_por_correo(self, correo):
        filas = self.db.consultar(f"SELECT {CAMPOS} FROM Usuario WHERE correo = ?", (correo,))
        return self._a_usuario(filas[0]) if filas else None

    def obtener(self, id_usuario):
        filas = self.db.consultar(f"SELECT {CAMPOS} FROM Usuario WHERE id = ?", (id_usuario,))
        return self._a_usuario(filas[0]) if filas else None

    def listar_personal(self):
        filas = self.db.consultar(
            f"SELECT {CAMPOS} FROM Usuario WHERE activo = 1 "
            "ORDER BY CASE WHEN estado = 'TRABAJANDO' THEN 0 ELSE 1 END, nombres")
        return [self._a_usuario(f) for f in filas]

    # ---------- Perfil ----------
    def actualizar_perfil(self, id_usuario, nombres, apellidos, telefono):
        nombres, apellidos, telefono = nombres.strip(), apellidos.strip(), telefono.strip()
        errores = {}
        if not nombres:
            errores["nombres"] = "Ingrese sus nombres."
        if not apellidos:
            errores["apellidos"] = "Ingrese sus apellidos."
        if telefono and not re.fullmatch(r"\+?\d[\d ]{5,18}", telefono):
            errores["telefono"] = "Solo números (ej. 987 654 321)."
        if not errores:
            self.db.ejecutar(
                "UPDATE Usuario SET nombres = ?, apellidos = ?, telefono = ? WHERE id = ?",
                (nombres, apellidos, telefono or None, id_usuario))
        return errores

    def cambiar_password(self, id_usuario, actual, nueva, verificacion):
        f = self.db.consultar("SELECT password_hash FROM Usuario WHERE id = ?", (id_usuario,))[0]
        errores = {}
        if not self._verificar(actual, f.password_hash):
            errores["actual"] = "La contraseña actual no es correcta."
        self._validar_password(nueva, verificacion, errores, campo="nueva")
        if not errores:
            self.db.ejecutar("UPDATE Usuario SET password_hash = ? WHERE id = ?",
                             (self._hash(nueva), id_usuario))
        return errores

    def actualizar_foto(self, id_usuario, ruta):
        self.db.ejecutar("UPDATE Usuario SET foto = ? WHERE id = ?", (ruta, id_usuario))
