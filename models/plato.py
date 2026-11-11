class Plato:
    def __init__(self, id, nombre, categoria, precio, activo=True):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.precio = float(precio)
        self.activo = activo

    def __repr__(self):
        return f"Plato({self.nombre}, S/ {self.precio:.2f})"
