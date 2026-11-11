"""Punto de entrada del POS Chifa Shun Fa."""
import tkinter as tk
from tkinter import messagebox
from database.conexion import Conexion
from services.mesa_service import MesaService
from services.pedido_service import PedidoService
from services.reporte_service import ReporteService
from ui.mapa_salon import MapaSalon


def main():
    root = tk.Tk()
    root.title("POS - Chifa Shun Fa")
    root.geometry("1000x650")
    # root.attributes("-fullscreen", True)  # activar en la tablet de pared

    try:
        db = Conexion()
        db.abrir()
    except Exception as e:
        messagebox.showerror("Base de datos", f"No se pudo conectar a SQL Server:\n{e}")
        return

    mesas = MesaService(db)
    pedidos = PedidoService(db, mesas)
    reportes = ReporteService(db)
    MapaSalon(root, mesas, pedidos, reportes).pack(fill="both", expand=True)
    root.mainloop()
    db.cerrar()


if __name__ == "__main__":
    main()


    
