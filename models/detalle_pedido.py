class DetallePedido:
    def __init__(self, id, id_plato, nombre_plato, cantidad, precio_unitario, nota=None):
        self.id = id
        self.id_plato = id_plato
        self.nombre_plato = nombre_plato
        self.cantidad = cantidad
        self.precio_unitario = float(precio_unitario)
        self.nota = nota

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
