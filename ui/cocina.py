"""Pantalla de cocina: solo muestra los platos que faltan preparar."""
import tkinter as tk
from config import INTERVALO_COCINA_MS


class VentanaCocina(tk.Toplevel):
    def __init__(self, master, pedido_service, on_cerrar=None):
        super().__init__(master)
        self.title("Cocina")
        self.geometry("560x520")
        self.svc = pedido_service
        self.on_cerrar = on_cerrar
        tk.Label(self, text="Pedidos por preparar", font=("Arial", 16, "bold")).pack(pady=(8, 0))
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True, padx=8, pady=8)
        self._job = None
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._refrescar()

    def _refrescar(self):
        if self._job:
            self.after_cancel(self._job)
        for w in self.contenedor.winfo_children():
            w.destroy()
        pendientes = self.svc.pendientes_cocina()
        if not pendientes:
            tk.Label(self.contenedor, text="Sin pedidos pendientes", font=("Arial", 13),
                     fg="gray").pack(pady=20)
        for p in pendientes:
            platos = self.svc.listar_detalles(p.id, solo_pendientes=True)
            titulo = f"Mesa {p.mesa}  (pedido #{p.id})"
            if self.svc.tiene_platos_listos(p.id):
                titulo += "  - ADICIONAL"
            caja = tk.LabelFrame(self.contenedor, text=titulo, font=("Arial", 13, "bold"))
            caja.pack(fill="x", pady=4)
            for d in platos:
                texto = f"{d.cantidad} x {d.nombre_plato}" + (f"  ({d.nota})" if d.nota else "")
                tk.Label(caja, text=texto, anchor="w", font=("Arial", 13)).pack(fill="x")
            ids = [d.id for d in platos]  # solo lo que el cocinero está viendo
            tk.Button(caja, text="Listo", font=("Arial", 12),
                      command=lambda i=p.id, ids=ids: self._listo(i, ids)).pack(anchor="e", padx=4, pady=4)
        self._job = self.after(INTERVALO_COCINA_MS, self._refrescar)

    def _listo(self, id_pedido, ids_detalle):
        self.svc.marcar_listo(id_pedido, ids_detalle)
        self._refrescar()

    def _cerrar(self):
        if self._job:
            self.after_cancel(self._job)
        if self.on_cerrar:
            self.on_cerrar()
        self.destroy()
