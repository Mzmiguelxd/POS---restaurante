import tkinter as tk
from ui.layout import PantallaBase
from ui.salon import MapaSalon
from ui.tema import C, F


class PantallaMesasUsuario(PantallaBase):
    MENU_ACTIVO = "EN ORDEN"

    def construir(self, contenido):
        cab = tk.Frame(contenido, bg="white")
        cab.pack(fill="x", padx=32, pady=(18, 0))
        self.lbl = tk.Label(cab, font=F["normal"], fg=C["suave"], bg="white", anchor="w")
        self.lbl.pack(side="left")
        self.mapa = MapaSalon(contenido, self.tocar_mesa)
        self.mapa.pack(fill="both", expand=True, padx=20, pady=10)
        self.refrescar()
        self.cada(5000, self.refrescar)   # ve los cambios hechos desde otro equipo

    def refrescar(self):
        mesas = self.svc.mesas.listar()
        ocupadas = sum(not m.esta_libre for m in mesas)
        self.lbl.config(text=f"Toque una mesa para tomar o ver su pedido.   "
                             f"Ocupadas: {ocupadas} de {len(mesas)}")
        self.mapa.actualizar(mesas)

    def tocar_mesa(self, mesa):
        if self.svc.pedidos.pedido_activo_de_mesa(mesa.id) is None:
            self.app.ir("ui.usuario.pedido:PantallaPedido", mesa=mesa)
        else:
            self.app.ir("ui.detalle_orden:PantallaDetalleOrden", mesa=mesa, modo="ver")
