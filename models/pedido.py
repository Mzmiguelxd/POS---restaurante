class Pedido:
    PENDIENTE = "PENDIENTE"
    LISTO = "LISTO"
    FINALIZADO = "FINALIZADO"
    METODOS_PAGO = ("EFECTIVO", "TARJETA", "YAPE")

    def __init__(self, id, id_mesa, fecha_inicio, estado=PENDIENTE, total=0, fecha_fin=None,
                 observaciones=None, metodo_pago=None, mozo=None, numero_mesa=None):
        self.id = id
        self.id_mesa = id_mesa
        self.numero_mesa = numero_mesa
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.total = float(total)
        self.observaciones = observaciones
        self.metodo_pago = metodo_pago
        self.mozo = mozo
        self.detalles = []

    def calcular_total(self):
        self.total = sum(d.subtotal for d in self.detalles)
        return self.total

    @property
    def tiene_pendientes(self):
        return any(not d.esta_listo for d in self.detalles)
