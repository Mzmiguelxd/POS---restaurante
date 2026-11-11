"""Detalles de orden según la mesa.
modo 'confirmar': revisa lo elegido antes de enviarlo a cocina.
modo 'ver': mesa ocupada; permite quitar, agregar platos o cobrar."""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, PanelRedondeado


class PantallaDetalleOrden(PantallaBase):
    @property
    def MENU_ACTIVO(self):
        return "MESAS" if self.app.usuario.es_admin else "EN ORDEN"

    def construir(self, contenido, mesa, modo="ver", carrito=None, observaciones=""):
        self.mesa, self.modo = mesa, modo
        self.carrito, self.obs_nueva = carrito or {}, observaciones
        self.pedido = self.svc.pedidos.pedido_activo_de_mesa(mesa.id)
        if modo == "ver" and self.pedido is None:
            self.after(10, self.app.ir_inicio)
            return
        panel = PanelRedondeado(contenido)
        panel.pack(fill="both", expand=True, padx=60, pady=36)
        p = panel.interior
        tk.Label(p, text=f"Detalles de orden: Mesa {mesa.numero}", font=F["h1"], bg="white",
                 anchor="w").pack(fill="x")
        numero = f"Pedido N° {self.pedido.id}" if self.pedido else "Pedido nuevo"
        info = tk.Frame(p, bg="white")
        info.pack(fill="x", pady=(10, 8))
        tk.Label(info, text=numero, font=F["normal_b"], bg="white", relief="solid", bd=2,
                 padx=14, pady=6).pack(side="left")
        if self.pedido and self.pedido.mozo:
            tk.Label(info, text=f"Atiende: {self.pedido.mozo}", font=F["normal"], fg=C["suave"],
                     bg="white").pack(side="left", padx=14)

        cuerpo = tk.Frame(p, bg="white")
        cuerpo.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(cuerpo, columns=("plato", "cant", "precio", "sub", "estado"),
                                  show="headings", selectmode="browse", height=8)
        for col, txt, w, anc in (("plato", "Plato", 320, "w"), ("cant", "Cantidad", 90, "center"),
                                 ("precio", "Precio", 100, "e"), ("sub", "Subtotal", 110, "e"),
                                 ("estado", "Cocina", 120, "center")):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor=anc, stretch=(col == "plato"))
        self.tabla.tag_configure("nuevo", background="#FFF4CC")
        self.tabla.tag_configure("listo", foreground=C["verde"])
        barra = ttk.Scrollbar(cuerpo, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="left", fill="y")

        abajo = tk.Frame(p, bg="white")
        abajo.pack(fill="x", pady=(14, 0))
        obs = tk.Frame(abajo, bg="white", relief="solid", bd=2)
        obs.pack(side="left", fill="x", expand=True)
        tk.Label(obs, text="Observaciones", font=F["normal_b"], bg="white", anchor="w").pack(
            fill="x", padx=10, pady=(6, 0))
        self.lbl_obs = tk.Label(obs, font=F["normal"], bg="white", anchor="w", justify="left",
                                wraplength=560)
        self.lbl_obs.pack(fill="x", padx=10, pady=(0, 8))
        self.lbl_total = tk.Label(abajo, font=F["h2"], bg="white", relief="solid", bd=2,
                                  padx=18, pady=8)
        self.lbl_total.pack(side="right", padx=(20, 0))

        botones = tk.Frame(p, bg="white")
        botones.pack(fill="x", pady=(18, 0))
        BotonRedondeado(botones, "⟵ REGRESAR", self._regresar, ancho=170, fuente=F["boton"]).pack(side="left")
        if modo == "confirmar":
            BotonRedondeado(botones, "CONFIRMAR ⟶", self._confirmar, ancho=190, estilo="lleno",
                            fuente=F["boton"]).pack(side="right")
        else:
            BotonRedondeado(botones, "COBRAR ⟶", self._cobrar, ancho=170, estilo="lleno",
                            fuente=F["boton"]).pack(side="right")
            if not self.app.usuario.es_admin:
                BotonRedondeado(botones, "Agregar platos", self._agregar, ancho=170).pack(side="right", padx=12)
            BotonRedondeado(botones, "Quitar plato", self._quitar, ancho=150).pack(side="right")
        self._pintar()

    def _pintar(self):
        self.tabla.delete(*self.tabla.get_children())
        total = 0.0
        if self.pedido:
            for d in self.pedido.detalles:
                self.tabla.insert("", "end", iid=f"d{d.id}", tags=("listo",) if d.esta_listo else (),
                                  values=(d.nombre_plato, d.cantidad, f"S/ {d.precio_unitario:.2f}",
                                          f"S/ {d.subtotal:.2f}", "Listo" if d.esta_listo else "En cocina"))
                total += d.subtotal
        for id_plato, (plato, cant) in self.carrito.items():
            self.tabla.insert("", "end", iid=f"n{id_plato}", tags=("nuevo",),
                              values=(plato.nombre, cant, f"S/ {plato.precio:.2f}",
                                      f"S/ {plato.precio * cant:.2f}", "Nuevo"))
            total += plato.precio * cant
        partes = [x for x in ((self.pedido.observaciones if self.pedido else None), self.obs_nueva) if x]
        self.lbl_obs.config(text=" | ".join(partes) or "Sin observaciones")
        self.lbl_total.config(text=f"TOTAL  S/ {total:.2f}")

    # ---------- Acciones ----------
    def _regresar(self):
        if self.modo == "confirmar":
            self.app.ir("ui.usuario.pedido:PantallaPedido", mesa=self.mesa,
                        carrito=self.carrito, observaciones=self.obs_nueva)
        else:
            self.app.ir_inicio()

    def _confirmar(self):
        items = [(p, c) for p, c in self.carrito.values()]
        try:
            self.svc.pedidos.confirmar_orden(self.mesa.id, items, self.obs_nueva, self.app.usuario.id)
        except Exception as e:
            messagebox.showerror("No se pudo guardar", str(e), parent=self)
            return
        self.app.ir_inicio()
        self.app.aviso(f"Orden de la mesa {self.mesa.numero} enviada a cocina")

    def _agregar(self):
        self.app.ir("ui.usuario.pedido:PantallaPedido", mesa=self.mesa)

    def _quitar(self):
        sel = self.tabla.selection()
        if not sel:
            self.app.aviso("Toque primero un plato de la lista", error=True)
            return
        d = next(x for x in self.pedido.detalles if f"d{x.id}" == sel[0])
        extra = "\nEste plato ya fue preparado en cocina." if d.esta_listo else ""
        if not messagebox.askyesno("Quitar plato", f"¿Quitar {d.cantidad} x {d.nombre_plato}?{extra}",
                                   parent=self):
            return
        self.svc.pedidos.quitar_detalle(d.id)
        self.pedido = self.svc.pedidos.pedido_activo_de_mesa(self.mesa.id)
        if self.pedido is None:
            self.app.ir_inicio()
            self.app.aviso(f"Pedido anulado: la mesa {self.mesa.numero} quedó libre")
        else:
            self._pintar()

    def _cobrar(self):
        self.app.ir("ui.pago:PantallaPago", mesa=self.mesa)
