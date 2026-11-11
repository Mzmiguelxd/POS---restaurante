class Pedido:
    PENDIENTE = "PENDIENTE"
    LISTO = "LISTO"
    FINALIZADO = "FINALIZADO"

    def __init__(self, id, id_mesa, fecha_inicio, estado=PENDIENTE, total=0, fecha_fin=None):
        self.id = id
        self.id_mesa = id_mesa
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.total = float(total)
        self.detalles = []

    def calcular_total(self):
        self.total = sum(d.subtotal for d in self.detalles)
        return self.total
