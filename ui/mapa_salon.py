"""Pantalla principal: réplica visual del salón (mesas 1-23)."""
import tkinter as tk
from tkinter import messagebox
from config import COLOR_LIBRE, COLOR_EN_CURSO
from ui.toma_pedido import TomaPedido
from ui.cocina import VentanaCocina


class MapaSalon(tk.Frame):
    COLUMNAS = 6

    def __init__(self, master, mesa_service, pedido_service, reporte_service):
        super().__init__(master)
        self.mesa_service = mesa_service
        self.pedido_service = pedido_service
        self.reporte_service = reporte_service
        self.botones = {}
        self._ventanas = {}     # mesa.id -> ventana abierta (evita duplicados)
        self._cocina = None
        self._construir()
        self.refrescar()

    def _construir(self):
        barra = tk.Frame(self)
        barra.pack(fill="x", pady=8)
        tk.Label(barra, text="Chifa Shun Fa - Salón", font=("Arial", 20, "bold")).pack(side="left", padx=12)
        tk.Button(barra, text="Cocina", font=("Arial", 14), command=self._abrir_cocina).pack(side="right", padx=6)
        tk.Button(barra, text="Reporte", font=("Arial", 14), command=self._mostrar_reporte).pack(side="right", padx=6)

        self.grilla = tk.Frame(self)
        self.grilla.pack(expand=True, fill="both", padx=12, pady=12)

    def refrescar(self):
        for mesa in self.mesa_service.listar():
            color = COLOR_LIBRE if mesa.esta_libre else COLOR_EN_CURSO
            if mesa.id not in self.botones:
                fila, col = divmod(mesa.numero - 1, self.COLUMNAS)
                btn = tk.Button(self.grilla, text=f"Mesa {mesa.numero}", font=("Arial", 16, "bold"),
                                fg="white", activeforeground="white", width=10, height=3,
                                command=lambda m=mesa: self._abrir_mesa(m))
                btn.grid(row=fila, column=col, padx=6, pady=6, sticky="nsew")
                self.botones[mesa.id] = btn
            self.botones[mesa.id].config(bg=color, activebackground=color)
        for c in range(self.COLUMNAS):
            self.grilla.columnconfigure(c, weight=1)

    def _abrir_mesa(self, mesa):
        ventana = self._ventanas.get(mesa.id)
        if ventana is not None and ventana.winfo_exists():
            ventana.lift(); ventana.focus_set()      # ya estaba abierta: solo traerla al frente
            return
        self._ventanas[mesa.id] = TomaPedido(self, mesa, self.pedido_service,
                                             on_cerrar=self._al_cerrar_mesa)

    def _al_cerrar_mesa(self, id_mesa):
        self._ventanas.pop(id_mesa, None)
        self.refrescar()

    def _abrir_cocina(self):
        if self._cocina is not None and self._cocina.winfo_exists():
            self._cocina.lift()
            return
        self._cocina = VentanaCocina(self, self.pedido_service, on_cerrar=self._al_cerrar_cocina)

    def _al_cerrar_cocina(self):
        self._cocina = None

    def _mostrar_reporte(self):
        v = self.reporte_service.ventas_del_dia()
        top = self.reporte_service.platos_mas_vendidos()
        prom = self.reporte_service.tiempo_promedio_por_mesa_min()
        texto = (f"Pedidos finalizados hoy: {v['pedidos']}\n"
                 f"Total vendido hoy: S/ {v['total']:.2f}\n"
                 f"Tiempo promedio por mesa: {prom:.0f} min\n\n"
                 "Más vendidos:\n" + "\n".join(f"- {r.nombre}: {r.vendidos}" for r in top))
        messagebox.showinfo("Reporte del día", texto)
