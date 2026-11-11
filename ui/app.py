"""Ventana principal: cambia de pantalla según la sesión y el rol."""
import importlib
import tkinter as tk
from tkinter import messagebox
from ui import tema
from ui.tema import C, F


class App(tk.Tk):
    def __init__(self, servicios):
        super().__init__()
        self.svc = servicios
        self.usuario = None
        self.title("POS - Chifa Shun Fa")
        self.geometry("1280x760")
        self.minsize(1100, 680)
        try:
            self.state("zoomed")              # Windows
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)  # Linux
            except tk.TclError:
                pass
        tema.iniciar(self)
        self.contenedor = tk.Frame(self, bg=C["lateral"])
        self.contenedor.pack(fill="both", expand=True)
        self.pantalla = None
        self._aviso = None
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        self.ir("ui.login:PantallaLogin")

    def ir(self, ruta, **kw):
        """Cambia a otra pantalla. ruta = 'modulo:Clase' (evita importaciones circulares)."""
        modulo, clase = ruta.split(":")
        Clase = getattr(importlib.import_module(modulo), clase)
        if self.pantalla is not None:
            self.pantalla.destroy()
        self.pantalla = Clase(self.contenedor, self, **kw)
        self.pantalla.pack(fill="both", expand=True)

    # ---------- Sesión ----------
    def iniciar_sesion(self, usuario):
        self.usuario = usuario
        self.ir_inicio()

    def ir_inicio(self):
        if self.usuario.es_admin:
            self.ir("ui.admin.mesas:PantallaMesasAdmin")
        else:
            self.ir("ui.usuario.mesas:PantallaMesasUsuario")

    def salir(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar sesión?", parent=self):
            self.svc.usuarios.cerrar_sesion(self.usuario)
            correo = self.usuario.correo
            self.usuario = None
            self.ir("ui.login:PantallaLogin", correo=correo)

    def al_cerrar(self):
        if self.usuario and not messagebox.askyesno(
                "Cerrar programa", "¿Cerrar el programa? Su sesión se cerrará.", parent=self):
            return
        if self.usuario:
            try:
                self.svc.usuarios.cerrar_sesion(self.usuario)
            except Exception:
                pass
        self.destroy()

    # ---------- Avisos ----------
    def aviso(self, texto, error=False):
        """Mensaje corto en la parte inferior que desaparece solo."""
        if self._aviso is not None:
            self._aviso.destroy()
        self._aviso = tk.Label(self, text=texto, font=F["normal_b"], fg="white",
                               bg=C["rojo"] if error else "#000000", padx=22, pady=12)
        self._aviso.place(relx=0.5, rely=0.96, anchor="s")
        etiqueta = self._aviso
        self.after(2800, lambda: etiqueta.winfo_exists() and etiqueta.destroy())
