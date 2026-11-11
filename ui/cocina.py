"""Pantalla de cocina: pedidos pendientes, con refresco automático."""
import tkinter as tk
from config import INTERVALO_COCINA_MS


class VentanaCocina(tk.Toplevel):
    def __init__(self, master, pedido_service):
        super().__init__(master)
        self.title("Cocina")
        self.geometry("520x480")
        self.svc = pedido_service
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True, padx=8, pady=8)
        self._job = None
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._refrescar()

    def _refrescar(self):
        for w in self.contenedor.winfo_children():
            w.destroy()
        for p in self.svc.pendientes_cocina():
            caja = tk.LabelFrame(self.contenedor, text=f"Mesa {p.mesa} (pedido #{p.id})", font=("Arial", 12, "bold"))
            caja.pack(fill="x", pady=4)
            for d in self.svc.listar_detalles(p.id):
                tk.Label(caja, text=f"{d.cantidad} x {d.nombre_plato}", anchor="w").pack(fill="x")
            tk.Button(caja, text="Listo", command=lambda i=p.id: self._listo(i)).pack(anchor="e")
        self._job = self.after(INTERVALO_COCINA_MS, self._refrescar)

    def _listo(self, id_pedido):
        self.svc.marcar_listo(id_pedido)
        self._refrescar()

    def _cerrar(self):
        if self._job:
            self.after_cancel(self._job)
        self.destroy()
