"""Método de pago (boceto): Efectivo, Tarjeta o Yape, y tipo de comprobante."""
import re
import tkinter as tk
from tkinter import messagebox
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, PanelRedondeado, Campo, MarcoScroll


class PantallaPago(PantallaBase):
    @property
    def MENU_ACTIVO(self):
        return "MESAS" if self.app.usuario.es_admin else "EN ORDEN"

    def construir(self, contenido, mesa):
        self.mesa = mesa
        self.pedido = self.svc.pedidos.pedido_activo_de_mesa(mesa.id)
        if self.pedido is None:
            self.after(10, self.app.ir_inicio)
            return
        self.metodo, self.tipo = None, "BOLETA"
        panel = PanelRedondeado(contenido)
        panel.pack(fill="both", expand=True, padx=60, pady=20)
        p = panel.interior
        # Los botones se ubican primero para que siempre tengan espacio
        botones = tk.Frame(p, bg="white")
        botones.pack(side="bottom", fill="x", pady=(10, 0))
        BotonRedondeado(botones, "⟵ REGRESAR",
                        lambda: self.app.ir("ui.detalle_orden:PantallaDetalleOrden", mesa=mesa, modo="ver"),
                        ancho=170, fuente=F["boton"]).pack(side="left")
        BotonRedondeado(botones, "COMPLETAR ⟶", self._completar, ancho=190, estilo="lleno",
                        fuente=F["boton"]).pack(side="right")
        tk.Label(p, text="Método de pago", font=F["h1"], bg="white", anchor="w").pack(fill="x")
        cajas = tk.Frame(p, bg="white")
        cajas.pack(fill="x", pady=10)
        for texto in (f"Pedido N° {self.pedido.id}   Mesa {mesa.numero}",
                      f"TOTAL  S/ {self.pedido.total:.2f}"):
            tk.Label(cajas, text=texto, font=F["normal_b"], bg="white", relief="solid", bd=2,
                     padx=14, pady=6).pack(side="left", padx=(0, 12))

        marco = tk.Frame(p, bg="white", relief="solid", bd=2)
        marco.pack(fill="x")
        if len(self.pedido.detalles) > 5:        # muchos platos: lista con scroll
            scroll = MarcoScroll(marco, bg="white")
            scroll.configure(height=120)
            scroll.pack_propagate(False)
            scroll.pack(fill="x")
            detalle = scroll.interior
        else:
            detalle = marco
        for d in self.pedido.detalles:
            fila = tk.Frame(detalle, bg="white")
            fila.pack(fill="x", padx=14, pady=2)
            tk.Label(fila, text=f"{d.cantidad} x {d.nombre_plato}", font=F["normal"], bg="white").pack(side="left")
            tk.Label(fila, text=f"S/ {d.subtotal:.2f}", font=F["normal"], bg="white").pack(side="right")
        if self.pedido.observaciones:
            tk.Label(marco, text=f"Obs.: {self.pedido.observaciones}", font=F["peq"], fg=C["suave"],
                     bg="white", anchor="w", wraplength=700, justify="left").pack(fill="x", padx=14, pady=(0, 6))
        if self.pedido.tiene_pendientes:
            tk.Label(p, text="Aún hay platos en cocina sin marcar como listos.", font=F["peq"],
                     fg=C["rojo"], bg="white", anchor="w").pack(fill="x", pady=(4, 0))

        metodos = tk.Frame(p, bg="white")
        metodos.pack(pady=(12, 4))
        self.btn_metodo = {}
        for m in ("EFECTIVO", "TARJETA", "YAPE"):
            b = BotonRedondeado(metodos, m, lambda x=m: self._elegir_metodo(x), ancho=150, fuente=F["boton"])
            b.pack(side="left", padx=20)
            self.btn_metodo[m] = b
        self.lbl_metodo = tk.Label(p, text="Elija cómo paga el cliente.", font=F["peq"], fg=C["suave"], bg="white")
        self.lbl_metodo.pack()

        extra = tk.Frame(p, bg="white")
        extra.pack(fill="x", pady=(8, 0))
        self.efectivo = tk.Frame(extra, bg="white")
        self.campo_paga = Campo(self.efectivo, "PAGA CON (S/)", ancho=12, ayuda="Opcional, para calcular el vuelto")
        self.campo_paga.pack(side="left")
        self.lbl_vuelto = tk.Label(self.efectivo, font=F["h2"], bg="white")
        self.lbl_vuelto.pack(side="left", padx=20)
        self.campo_paga.var.trace_add("write", lambda *a: self._vuelto())

        comp = tk.Frame(extra, bg="white")
        comp.pack(side="right", anchor="n")
        tk.Label(comp, text="Comprobante", font=F["normal_b"], bg="white").pack(anchor="w")
        fila = tk.Frame(comp, bg="white")
        fila.pack(anchor="w")
        self.var_tipo = tk.StringVar(value="BOLETA")
        for t in ("BOLETA", "FACTURA"):
            tk.Radiobutton(fila, text=t.capitalize(), value=t, variable=self.var_tipo, bg="white",
                           font=F["normal"], command=self._tipo).pack(side="left", padx=(0, 10))
        self.factura = tk.Frame(comp, bg="white")
        self.campo_ruc = Campo(self.factura, "RUC", ancho=16)
        self.campo_ruc.pack(side="left", padx=(0, 8))
        self.campo_razon = Campo(self.factura, "RAZÓN SOCIAL", ancho=22)
        self.campo_razon.pack(side="left")


    def _elegir_metodo(self, m):
        self.metodo = m
        for k, b in self.btn_metodo.items():
            b.set_activo(k == m)
        self.lbl_metodo.config(text=f"Pago con {m.capitalize()}", fg=C["texto"])
        if m == "EFECTIVO":
            self.efectivo.pack(side="left", anchor="n")
        else:
            self.efectivo.pack_forget()

    def _monto_paga(self):
        txt = self.campo_paga.valor().replace(",", ".").strip()
        if not txt:
            return None
        try:
            return float(txt)
        except ValueError:
            return -1

    def _vuelto(self):
        v = self._monto_paga()
        if v is None or v < 0:
            self.lbl_vuelto.config(text="")
        elif v < self.pedido.total:
            self.lbl_vuelto.config(text=f"Faltan S/ {self.pedido.total - v:.2f}", fg=C["rojo"])
        else:
            self.lbl_vuelto.config(text=f"Vuelto: S/ {v - self.pedido.total:.2f}", fg=C["verde"])

    def _tipo(self):
        if self.var_tipo.get() == "FACTURA":
            self.factura.pack(anchor="w", pady=(6, 0))
        else:
            self.factura.pack_forget()

    def _completar(self):
        if not self.metodo:
            self.lbl_metodo.config(text="Elija Efectivo, Tarjeta o Yape para continuar.", fg=C["rojo"])
            return
        paga = self._monto_paga() if self.metodo == "EFECTIVO" else None
        if paga is not None and (paga < 0 or paga < self.pedido.total):
            self.campo_paga.error("El monto debe ser igual o mayor al total.")
            return
        tipo, ruc, razon = self.var_tipo.get(), None, None
        if tipo == "FACTURA":
            ruc, razon = self.campo_ruc.valor().strip(), self.campo_razon.valor().strip()
            ok = True
            if not re.fullmatch(r"(10|15|17|20)\d{9}", ruc):
                self.campo_ruc.error("11 dígitos, empieza con 10 o 20.")
                ok = False
            if not razon:
                self.campo_razon.error("Ingrese la razón social.")
                ok = False
            if not ok:
                return
        if not messagebox.askyesno("Completar pago",
                                   f"¿Cobrar S/ {self.pedido.total:.2f} con {self.metodo.capitalize()} "
                                   f"y liberar la mesa {self.mesa.numero}?", parent=self):
            return
        self.svc.pedidos.finalizar(self.pedido, self.metodo)
        self.app.ir("ui.comprobante:PantallaComprobante", pedido=self.pedido, tipo=tipo,
                    cliente=razon, ruc=ruc, paga_con=paga)
        self.app.aviso(f"Pago registrado. Mesa {self.mesa.numero} libre")
