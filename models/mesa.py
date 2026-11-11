class Mesa:
    LIBRE = "LIBRE"
    EN_CURSO = "EN_CURSO"

    def __init__(self, id, numero, estado=LIBRE):
        self.id = id
        self.numero = numero
        self.estado = estado

    @property
    def esta_libre(self):
        return self.estado == Mesa.LIBRE

    def __repr__(self):
        return f"Mesa({self.numero}, {self.estado})"
