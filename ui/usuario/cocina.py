"""Pedidos en cocina (boceto): una fila por pedido con N° de mesa, detalle y cantidades."""
import tkinter as tk
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, MarcoScroll, rect_redondeado


class PantallaCocina(PantallaBase):
    MENU_ACTIVO = "COCINA"

    def construir(self, contenido):
        cab = tk.Frame(contenido, bg="white")
        cab.pack(fill="x", padx=40, pady=(24, 8))
        self.titulo(cab, "Pedidos en cocina", "Se actualiza sola cada 5 segundos.")
        self.lista = MarcoScroll(contenido, bg="white")
        self.lista.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self._firma = None
        self.refrescar()
        self.cada(5000, self.refrescar)

    def refrescar(self):
        pendientes = self.svc.pedidos.pendientes_cocina()
        datos = []
        for p in pendientes:
            platos = self.svc.pedidos.listar_detalles(p.id, solo_pendientes=True)
            datos.append((p, platos, self.svc.pedidos.tiene_platos_listos(p.id)))
        firma = [(p.id, [(d.id, d.cantidad) for d in pl], p.observaciones) for p, pl, _ in datos]
        if firma == self._firma:
            return            # nada cambió: no redibujar (no pierde el scroll)
        self._firma = firma
        for w in self.lista.interior.winfo_children():
            w.destroy()
        if not datos:
            tk.Label(self.lista.interior, text="No hay pedidos por preparar.", font=F["h2"],
                     fg=C["suave"], bg="white").pack(pady=60)
        for i, (p, platos, adicional) in enumerate(datos, start=1):
            self._fila(i, p, platos, adicional)

    def _fila(self, n, p, platos, adicional):
        alto = max(110, 40 + 30 * len(platos) + (26 if p.observaciones else 0))
        cv = tk.Canvas(self.lista.interior, height=alto, bg="white", highlightthickness=0)
        cv.pack(fill="x", pady=10, padx=6)
        caja = tk.Frame(cv, bg=C["tarjeta"])

        def dibujar(e):
            cv.delete("fondo")
            rect_redondeado(cv, 0, 0, e.width, alto, r=28, fill=C["tarjeta"], outline="", tags="fondo")
            rect_redondeado(cv, 0, 0, 150, alto, r=28, fill=C["azul"], outline="", tags="fondo")
            cv.create_text(75, alto / 2, text=str(n), font=F["grande"], tags="fondo")
            cv.tag_lower("fondo")
            cv.coords(ventana, 175, 14)
            cv.itemconfigure(ventana, width=e.width - 200, height=alto - 28)
        ventana = cv.create_window(175, 14, window=caja, anchor="nw")
        cv.bind("<Configure>", dibujar)

        caja.columnconfigure(0, minsize=190)
        caja.columnconfigure(1, weight=1)
        mesa = tk.Frame(caja, bg=C["tarjeta"])
        mesa.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 30))
        tk.Label(mesa, text=f"Mesa {p.mesa}", font=F["h1"], bg=C["tarjeta"]).pack(anchor="w")
        tk.Label(mesa, text=f"Pedido N° {p.id}", font=F["peq"], fg=C["suave"], bg=C["tarjeta"]).pack(anchor="w")
        if adicional:
            tk.Label(mesa, text="Adicional", font=F["normal_b"], fg="white", bg=C["rojo"],
                     padx=8).pack(anchor="w", pady=(4, 0))
        detalle = tk.Frame(caja, bg=C["tarjeta"])
        detalle.grid(row=0, column=1, sticky="nsew")
        for d in platos:
            fila = tk.Frame(detalle, bg=C["tarjeta"])
            fila.pack(fill="x")
            tk.Label(fila, text=d.nombre_plato, font=F["normal"], bg=C["tarjeta"], anchor="w").pack(side="left")
            tk.Label(fila, text=f"x {d.cantidad}", font=F["h2"], bg=C["tarjeta"]).pack(side="right", padx=20)
        if p.observaciones:
            tk.Label(caja, text=f"Obs.: {p.observaciones}", font=(F["normal"][0], 11, "italic"),
                     fg=C["rojo"], bg=C["tarjeta"], anchor="w").grid(row=1, column=1, sticky="w", pady=(4, 0))
        ids = [d.id for d in platos]
        BotonRedondeado(caja, "LISTO", lambda: self._listo(p.id, ids), ancho=110, alto=44,
                        estilo="lleno", fuente=F["boton"]).grid(row=0, column=2, rowspan=2, padx=(10, 0))

    def _listo(self, id_pedido, ids):
        self.svc.pedidos.marcar_listo(id_pedido, ids)
        self._firma = None
        self.refrescar()
