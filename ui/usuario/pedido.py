"""Toma de pedido (boceto: buscador, tarjetas de platos, pedido a la izquierda,
observaciones abajo y botón Finalizar orden)."""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from ui.tema import C, F
from ui.widgets import BotonRedondeado, MarcoScroll, miniatura, entrada_con_placeholder
from util import imagenes

ANCHO_TARJETA, ALTO_IMG = 180, 130


class PantallaPedido(tk.Frame):
    def __init__(self, parent, app, mesa, carrito=None, observaciones=""):
        super().__init__(parent, bg="white")
        self.app, self.svc, self.mesa = app, app.svc, mesa
        self.platos = self.svc.pedidos.listar_platos()
        self.carrito = dict(carrito or {})        # plato.id -> [plato, cantidad]
        self.categoria = None
        self.tarjetas = []
        self.pedido_actual = self.svc.pedidos.pedido_activo_de_mesa(mesa.id)
        self._construir(observaciones)
        self._pintar_carrito()
        self._filtrar()

    # ---------- Construcción ----------
    def _construir(self, observaciones):
        izq = tk.Frame(self, bg="white", width=340)
        izq.pack(side="left", fill="y", padx=(24, 12), pady=20)
        izq.pack_propagate(False)
        der = tk.Frame(self, bg="white")
        der.pack(side="left", fill="both", expand=True, padx=(12, 24), pady=20)

        # Columna izquierda: el pedido
        BotonRedondeado(izq, "⟵ MESAS", self._volver, ancho=130, alto=38).pack(anchor="w")
        tk.Label(izq, text=f"Mesa {self.mesa.numero}", font=F["h1"], bg="white",
                 anchor="w").pack(fill="x", pady=(12, 0))
        if self.pedido_actual:
            tk.Label(izq, text=f"Pedido N° {self.pedido_actual.id} ya registrado: "
                               f"S/ {self.pedido_actual.total:.2f}\nLo que agregue aquí es adicional.",
                     font=F["peq"], fg=C["suave"], bg="white", justify="left",
                     anchor="w").pack(fill="x")
        caja = tk.Frame(izq, bg=C["linea"], padx=2, pady=2)
        caja.pack(fill="both", expand=True, pady=10)
        self.lista = MarcoScroll(caja, bg="white")
        self.lista.pack(fill="both", expand=True)
        self.lbl_total = tk.Label(izq, font=F["h2"], bg="white", anchor="e")
        self.lbl_total.pack(fill="x")
        self.btn_finalizar = BotonRedondeado(izq, "FINALIZAR ORDEN", self._finalizar, ancho=300,
                                             alto=50, estilo="lleno", fuente=F["boton"])
        self.btn_finalizar.pack(pady=(10, 0))

        # Columna derecha: buscador, categorías, platos, observaciones
        busc, self.var_buscar = entrada_con_placeholder(der, "Buscar plato por nombre…")
        busc.pack(fill="x")
        self.var_buscar.trace_add("write", lambda *a: self._filtrar())
        self.chips = tk.Frame(der, bg="white")
        self.chips.pack(fill="x", pady=(10, 4))
        categorias = [None] + sorted({p.categoria for p in self.platos})
        self._botones_cat = {}
        medir = tkfont.Font(font=F["menu"])
        for cat in categorias:
            b = BotonRedondeado(self.chips, cat or "Todos", lambda c=cat: self._elegir_categoria(c),
                                ancho=medir.measure(cat or "Todos") + 34, alto=34,
                                activo=(cat is None))
            b.pack(side="left", padx=(0, 8))
            self._botones_cat[cat] = b
        self.grilla = MarcoScroll(der, bg="white")
        self.grilla.pack(fill="both", expand=True, pady=6)
        self.grilla.interior.bind("<Configure>", lambda e: self._reacomodar(), add="+")
        self.vacio = tk.Label(self.grilla.interior, text="", font=F["normal"], fg=C["suave"], bg="white")
        for plato in self.platos:
            self.tarjetas.append((plato, self._tarjeta(plato)))
        obs, self.var_obs = entrada_con_placeholder(
            der, "Agregar observaciones (ej. sin cebolla, poco ají, para llevar)")
        obs.pack(fill="x", pady=(8, 0))
        self.var_obs.set(observaciones)

    def _tarjeta(self, plato):
        t = tk.Frame(self.grilla.interior, bg="white", cursor="hand2")
        img = miniatura(t, imagenes.ruta_plato(plato), ANCHO_TARJETA, ALTO_IMG, plato.nombre)
        img.pack()
        tk.Label(t, text=plato.nombre, font=F["normal"], bg="white", anchor="w",
                 wraplength=ANCHO_TARJETA, justify="left").pack(fill="x", pady=(6, 0))
        tk.Label(t, text=f"S/ {plato.precio:.2f}", font=F["peq"], fg=C["suave"], bg="white",
                 anchor="w").pack(fill="x")
        for w in (t, *t.winfo_children()):
            w.bind("<Button-1>", lambda e, p=plato, tj=t: self._agregar(p, tj))
        return t

    # ---------- Catálogo ----------
    def _elegir_categoria(self, cat):
        self.categoria = cat
        for c, b in self._botones_cat.items():
            b.set_activo(c == cat)
        self._filtrar()

    def _filtrar(self):
        texto = imagenes.slug(self.var_buscar.get())
        self.visibles = [(p, t) for p, t in self.tarjetas
                         if (self.categoria is None or p.categoria == self.categoria)
                         and texto in imagenes.slug(p.nombre)]
        self._reacomodar(forzar=True)
        self.grilla.arriba()

    def _reacomodar(self, forzar=False):
        ancho = self.grilla.canvas.winfo_width()
        cols = max(2, ancho // (ANCHO_TARJETA + 24)) if ancho > 1 else 4
        if not forzar and getattr(self, "_cols", None) == cols:
            return
        self._cols = cols
        for _, t in self.tarjetas:
            t.grid_forget()
        self.vacio.grid_forget()
        for i, (_, t) in enumerate(self.visibles):
            t.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky="n")
        if not self.visibles:
            self.vacio.config(text="Ningún plato coincide con la búsqueda.")
            self.vacio.grid(row=0, column=0, columnspan=cols, pady=40)

    # ---------- Carrito ----------
    def _agregar(self, plato, tarjeta=None):
        item = self.carrito.setdefault(plato.id, [plato, 0])
        item[1] += 1
        self._pintar_carrito()
        if tarjeta is not None:   # destello breve para confirmar el toque
            tarjeta.config(bg=C["azul"])
            self.after(180, lambda: tarjeta.winfo_exists() and tarjeta.config(bg="white"))

    def _cambiar(self, id_plato, delta):
        item = self.carrito.get(id_plato)
        if item:
            item[1] += delta
            if item[1] <= 0:
                del self.carrito[id_plato]
            self._pintar_carrito()

    def _quitar(self, id_plato):
        self.carrito.pop(id_plato, None)
        self._pintar_carrito()

    def _pintar_carrito(self):
        for w in self.lista.interior.winfo_children():
            w.destroy()
        if not self.carrito:
            tk.Label(self.lista.interior, text="Toque un plato para agregarlo.",
                     font=F["normal"], fg=C["suave"], bg="white").pack(pady=30)
        for id_plato, (plato, cant) in self.carrito.items():
            fila = tk.Frame(self.lista.interior, bg=C["tarjeta"], padx=10, pady=8)
            fila.pack(fill="x", padx=8, pady=(8, 0))
            arriba = tk.Frame(fila, bg=C["tarjeta"])
            arriba.pack(fill="x")
            tk.Label(arriba, text=plato.nombre, font=F["normal_b"], bg=C["tarjeta"], anchor="w",
                     wraplength=200, justify="left").pack(side="left", fill="x", expand=True)
            x = tk.Label(arriba, text="✕", font=F["h2"], fg=C["rojo"], bg=C["tarjeta"], cursor="hand2")
            x.pack(side="right")
            x.bind("<Button-1>", lambda e, i=id_plato: self._quitar(i))
            abajo = tk.Frame(fila, bg=C["tarjeta"])
            abajo.pack(fill="x", pady=(6, 0))
            for txt, d in (("−", -1), (None, 0), ("+", 1)):
                if txt is None:
                    tk.Label(abajo, text=str(cant), font=F["normal_b"], bg="white", width=3,
                             pady=4).pack(side="left", padx=4)
                    continue
                b = tk.Label(abajo, text=txt, font=F["h2"], bg="#B9C2CD", width=2, cursor="hand2")
                b.pack(side="left")
                b.bind("<Button-1>", lambda e, i=id_plato, dd=d: self._cambiar(i, dd))
            tk.Label(abajo, text=f"S/ {plato.precio * cant:.2f}", font=F["normal"],
                     bg=C["tarjeta"]).pack(side="right")
        total = sum(p.precio * c for p, c in self.carrito.values())
        self.lbl_total.config(text=f"Total: S/ {total:.2f}")
        self.btn_finalizar.set_habilitado(bool(self.carrito))

    # ---------- Navegación ----------
    def _volver(self):
        if self.carrito and not messagebox.askyesno(
                "Volver", "Hay platos sin confirmar. ¿Descartarlos y volver a las mesas?", parent=self):
            return
        self.app.ir_inicio()

    def _finalizar(self):
        if not self.carrito:
            return
        self.app.ir("ui.detalle_orden:PantallaDetalleOrden", mesa=self.mesa, modo="confirmar",
                    carrito=self.carrito, observaciones=self.var_obs.get().strip())
