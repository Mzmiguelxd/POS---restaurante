from models.mesa import Mesa


class MesaService:
    def __init__(self, conexion):
        self.db = conexion

    def listar(self):
        filas = self.db.consultar("SELECT id, numero, estado FROM Mesa ORDER BY numero")
        return [Mesa(f.id, f.numero, f.estado) for f in filas]

    def cambiar_estado(self, id_mesa, estado):
        self.db.ejecutar("UPDATE Mesa SET estado = ? WHERE id = ?", (estado, id_mesa))
