"""Ventana para tomar el pedido de una mesa, corregirlo y cerrar la cuenta."""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.cuenta import resumen_cuenta


class TomaPedido(tk.Toplevel):
    def __init__(self, master, mesa, pedido_service, on_cerrar=None):
        super().__init__(master)
        self.title(f"Mesa {mesa.numero}")
        self.geometry("860x560")
        self.mesa = mesa
        self.svc = pedido_service
        self.on_cerrar = on_cerrar
        self.platos = self.svc.listar_platos()
        self.pedido = None
        self._construir()
        self._recargar()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        # Ventana modal: evita abrir otra mesa encima por un doble toque
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.focus_set()

    # ---------- Interfaz ----------
    def _construir(self):
        estilo = ttk.Style(self)
        estilo.configure("Pedido.Treeview", font=("Arial", 12), rowheight=30)
        estilo.configure("Pedido.Treeview.Heading", font=("Arial", 12, "bold"))

        izq = tk.Frame(self); izq.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        der = tk.Frame(self); der.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        tk.Label(izq, text="Menú", font=("Arial", 14, "bold")).pack()
        self.lista = tk.Listbox(izq, font=("Arial", 13), activestyle="none")
        for p in self.platos:
            self.lista.insert("end", f"{p.nombre}  -  S/ {p.precio:.2f}")
        self.lista.pack(fill="both", expand=True)
        self.lista.bind("<Double-Button-1>", lambda e: self._agregar())
        tk.Button(izq, text="Agregar plato", font=("Arial", 13), height=2,
                  command=self._agregar).pack(fill="x", pady=6)

        tk.Label(der, text="Pedido", font=("Arial", 14, "bold")).pack()
        self.tabla = ttk.Treeview(der, columns=("plato", "cant", "sub", "estado"),
                                  show="headings", height=10, style="Pedido.Treeview",
                                  selectmode="browse")
        for col, txt, w, anc in (("plato", "Plato", 210, "w"), ("cant", "Cant", 50, "center"),
                                 ("sub", "Subtotal", 80, "e"), ("estado", "Cocina", 90, "center")):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor=anc)
        self.tabla.tag_configure("listo", foreground="#2E7D32")
        self.tabla.pack(fill="both", expand=True)

        botones = tk.Frame(der); botones.pack(fill="x", pady=4)
        for txt, cmd in (("＋ 1", self._sumar), ("－ 1", self._restar), ("Quitar", self._quitar)):
            tk.Button(botones, text=txt, font=("Arial", 13), height=2, command=cmd)\
                .pack(side="left", expand=True, fill="x", padx=2)

        self.lbl_total = tk.Label(der, text="Total: S/ 0.00", font=("Arial", 16, "bold"))
        self.lbl_total.pack(pady=6)
        tk.Button(der, text="Finalizar y cobrar", font=("Arial", 13), height=2,
                  command=self._finalizar).pack(fill="x")

    def _recargar(self, seleccionar=None):
        """Vuelve a leer el pedido desde la BD y repinta la tabla."""
        self.pedido = self.svc.pedido_activo_de_mesa(self.mesa.id)
        self.tabla.delete(*self.tabla.get_children())
        total = 0.0
        if self.pedido:
            for d in self.pedido.detalles:
                self.tabla.insert("", "end", iid=str(d.id),
                                  values=(d.nombre_plato, d.cantidad, f"{d.subtotal:.2f}",
                                          "Listo" if d.esta_listo else "En cocina"),
                                  tags=("listo",) if d.esta_listo else ())
            total = self.pedido.calcular_total()
            if seleccionar and self.tabla.exists(str(seleccionar)):
                self.tabla.selection_set(str(seleccionar))
        self.lbl_total.config(text=f"Total: S/ {total:.2f}")

    def _detalle_seleccionado(self):
        sel = self.tabla.selection()
        if not sel or not self.pedido:
            messagebox.showinfo("Seleccione", "Toque primero un plato del pedido.", parent=self)
            return None
        return next((d for d in self.pedido.detalles if str(d.id) == sel[0]), None)

    # ---------- Acciones ----------
    def _agregar(self):
        sel = self.lista.curselection()
        if not sel:
            return
        id_pedido = self.svc.abrir_pedido(self.mesa.id)
        self.svc.agregar_detalle(id_pedido, self.platos[sel[0]], 1)
        self._recargar()

    def _sumar(self):
        d = self._detalle_seleccionado()
        if d:
            plato = next((p for p in self.platos if p.id == d.id_plato), None)
            if plato is None:
                return
            self.svc.agregar_detalle(self.pedido.id, plato, 1, d.nota)
            self._recargar(seleccionar=d.id)

    def _restar(self):
        d = self._detalle_seleccionado()
        if d:
            if d.cantidad == 1 and not self._confirmar_quitar(d):
                return
            self.svc.disminuir_detalle(d.id)
            self._recargar(seleccionar=d.id)

    def _quitar(self):
        d = self._detalle_seleccionado()
        if d and self._confirmar_quitar(d):
            self.svc.quitar_detalle(d.id)
            self._recargar()

    def _confirmar_quitar(self, d):
        aviso = "\n\nOjo: este plato ya fue preparado en cocina." if d.esta_listo else ""
        return messagebox.askyesno("Quitar plato", f"¿Quitar {d.nombre_plato}?{aviso}", parent=self)

    def _finalizar(self):
        if not self.pedido or not self.pedido.detalles:
            messagebox.showwarning("Sin pedido", "Esta mesa no tiene platos.", parent=self)
            return
        aviso = ""
        if any(not d.esta_listo for d in self.pedido.detalles):
            aviso = "\n\nOjo: aún hay platos en cocina sin marcar como listos."
        if messagebox.askyesno("Cuenta", resumen_cuenta(self.mesa, self.pedido) + aviso
                               + "\n\n¿Finalizar y liberar la mesa?", parent=self):
            self.svc.finalizar(self.pedido)
            self._cerrar()

    def _cerrar(self):
        self.grab_release()
        if self.on_cerrar:
            self.on_cerrar(self.mesa.id)
        self.destroy()
