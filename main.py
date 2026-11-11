"""Punto de entrada del POS Chifa Shun Fa."""
import tkinter as tk
from tkinter import messagebox
from types import SimpleNamespace
from database.conexion import Conexion
from services.mesa_service import MesaService
from services.pedido_service import PedidoService
from services.reporte_service import ReporteService
from services.usuario_service import UsuarioService
from ui.app import App


def crear_servicios(db):
    mesas = MesaService(db)
    return SimpleNamespace(mesas=mesas, pedidos=PedidoService(db, mesas),
                           reportes=ReporteService(db), usuarios=UsuarioService(db))


def main():
    try:
        db = Conexion()
        db.abrir()
    except Exception as e:
        raiz = tk.Tk(); raiz.withdraw()
        messagebox.showerror("Base de datos", f"No se pudo conectar a SQL Server:\n{e}")
        return
    svc = crear_servicios(db)
    if svc.usuarios.asegurar_admin():
        print(f"Administrador creado: {UsuarioService.ADMIN_CORREO} / {UsuarioService.ADMIN_PASSWORD}")
    app = App(svc)
    app.mainloop()
    db.cerrar()


if __name__ == "__main__":
    main()
