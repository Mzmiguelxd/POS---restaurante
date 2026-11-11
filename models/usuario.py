class Usuario:
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"
    TRABAJANDO = "TRABAJANDO"
    AUSENTE = "AUSENTE"

    def __init__(self, id, nombres, apellidos, correo, rol=USUARIO, telefono=None,
                 foto=None, estado=AUSENTE, fecha_nacimiento=None):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.rol = rol
        self.telefono = telefono
        self.foto = foto
        self.estado = estado
        self.fecha_nacimiento = fecha_nacimiento

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def es_admin(self):
        return self.rol == Usuario.ADMIN

    @property
    def iniciales(self):
        return (self.nombres[:1] + self.apellidos[:1]).upper()

    def __repr__(self):
        return f"Usuario({self.correo}, {self.rol})"
