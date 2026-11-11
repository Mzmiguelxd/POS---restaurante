class DetallePedido:
    PENDIENTE = "PENDIENTE"   # en cocina
    LISTO = "LISTO"           # ya preparado

    def __init__(self, id, id_plato, nombre_plato, cantidad, precio_unitario,
                 nota=None, estado=PENDIENTE):
        self.id = id
        self.id_plato = id_plato
        self.nombre_plato = nombre_plato
        self.cantidad = cantidad
        self.precio_unitario = float(precio_unitario)
        self.nota = nota
        self.estado = estado

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def esta_listo(self):
        return self.estado == DetallePedido.LISTO
