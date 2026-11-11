import tkinter as tk
from ui.layout import PantallaBase
from ui.salon import MapaSalon
from ui.tema import C, F


class PantallaMesasAdmin(PantallaBase):
    MENU_ACTIVO = "MESAS"

    def construir(self, contenido):
        cab = tk.Frame(contenido, bg="white")
        cab.pack(fill="x", padx=32, pady=(18, 0))
        self.lbl = tk.Label(cab, font=F["normal"], fg=C["suave"], bg="white", anchor="w")
        self.lbl.pack(side="left")
        self.lbl_ventas = tk.Label(cab, font=F["normal_b"], bg="white")
        self.lbl_ventas.pack(side="right")
        self.mapa = MapaSalon(contenido, self.tocar_mesa)
        self.mapa.pack(fill="both", expand=True, padx=20, pady=10)
        self.refrescar()
        self.cada(5000, self.refrescar)

    def refrescar(self):
        mesas = self.svc.mesas.listar()
        ocupadas = sum(not m.esta_libre for m in mesas)
        self.lbl.config(text=f"Toque una mesa ocupada para ver su pedido o cobrarlo.   "
                             f"Ocupadas: {ocupadas} de {len(mesas)}")
        v = self.svc.reportes.ventas_del_dia()
        n = v["pedidos"]
        self.lbl_ventas.config(text=f"Vendido hoy: S/ {v['total']:.2f} ({n} pedido{'s' if n != 1 else ''})")
        self.mapa.actualizar(mesas)

    def tocar_mesa(self, mesa):
        if self.svc.pedidos.pedido_activo_de_mesa(mesa.id) is None:
            self.app.aviso(f"La mesa {mesa.numero} está libre")
        else:
            self.app.ir("ui.detalle_orden:PantallaDetalleOrden", mesa=mesa, modo="ver")
