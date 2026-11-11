"""Ventana para tomar el pedido de una mesa y ver/cerrar la cuenta."""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.cuenta import resumen_cuenta


class TomaPedido(tk.Toplevel):
    def __init__(self, master, mesa, pedido_service, on_cerrar=None):
        super().__init__(master)
        self.title(f"Mesa {mesa.numero}")
        self.geometry("760x520")
        self.mesa = mesa
        self.svc = pedido_service
        self.on_cerrar = on_cerrar
        self.platos = self.svc.listar_platos()
        self.pedido = self.svc.pedido_activo_de_mesa(mesa.id)
        self._construir()
        self._pintar_detalle()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _construir(self):
        izq = tk.Frame(self); izq.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        der = tk.Frame(self); der.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        tk.Label(izq, text="Menú", font=("Arial", 14, "bold")).pack()
        self.lista = tk.Listbox(izq, font=("Arial", 13))
        for p in self.platos:
            self.lista.insert("end", f"{p.nombre}  -  S/ {p.precio:.2f}")
        self.lista.pack(fill="both", expand=True)
        tk.Button(izq, text="Agregar plato", font=("Arial", 13), command=self._agregar).pack(fill="x", pady=6)

        tk.Label(der, text="Pedido", font=("Arial", 14, "bold")).pack()
        self.tabla = ttk.Treeview(der, columns=("plato", "cant", "sub"), show="headings", height=12)
        for col, txt, w in (("plato", "Plato", 200), ("cant", "Cant", 50), ("sub", "Subtotal", 80)):
            self.tabla.heading(col, text=txt); self.tabla.column(col, width=w)
        self.tabla.pack(fill="both", expand=True)
        self.lbl_total = tk.Label(der, text="Total: S/ 0.00", font=("Arial", 16, "bold"))
        self.lbl_total.pack(pady=6)
        tk.Button(der, text="Finalizar y cobrar", font=("Arial", 13), command=self._finalizar).pack(fill="x")

    def _agregar(self):
        sel = self.lista.curselection()
        if not sel:
            return
        if self.pedido is None:
            id_pedido = self.svc.abrir_pedido(self.mesa.id)
        else:
            id_pedido = self.pedido.id
        self.svc.agregar_detalle(id_pedido, self.platos[sel[0]], 1)
        self.pedido = self.svc.pedido_activo_de_mesa(self.mesa.id)
        self._pintar_detalle()

    def _pintar_detalle(self):
        self.tabla.delete(*self.tabla.get_children())
        total = 0.0
        if self.pedido:
            for d in self.pedido.detalles:
                self.tabla.insert("", "end", values=(d.nombre_plato, d.cantidad, f"{d.subtotal:.2f}"))
            total = self.pedido.calcular_total()
        self.lbl_total.config(text=f"Total: S/ {total:.2f}")

    def _finalizar(self):
        if not self.pedido or not self.pedido.detalles:
            messagebox.showwarning("Sin pedido", "Esta mesa no tiene platos.")
            return
        if messagebox.askyesno("Cuenta", resumen_cuenta(self.mesa, self.pedido) + "\n\n¿Finalizar y liberar la mesa?"):
            self.svc.finalizar(self.pedido)
            self._cerrar()

    def _cerrar(self):
        if self.on_cerrar:
            self.on_cerrar()
        self.destroy()
