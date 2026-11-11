"""Colores, tipografías y estilos de la interfaz (según los bocetos)."""
import tkinter as tk
from tkinter import ttk, font as tkfont

C = {
    "lateral": "#C8D0D9",     # gris azulado de la barra lateral y la cabecera
    "fondo": "#FFFFFF",       # área de trabajo
    "texto": "#000000",
    "suave": "#5F6B7A",       # textos secundarios
    "rojo": "#D93636",        # ocupado / opción activa / alertas
    "azul": "#38B6FF",        # libre
    "mesa": "#C8D0D9",
    "mesa_hover": "#B3BDC9",
    "tarjeta": "#E3E8EE",     # fondo de tarjetas (cocina, carrito)
    "verde": "#2E7D32",
    "linea": "#000000",
}

F = {}


def _familia(preferidas, defecto="TkDefaultFont"):
    disponibles = set(tkfont.families())
    for f in preferidas:
        if f in disponibles:
            return f
    return tkfont.nametofont(defecto).actual("family")


def iniciar(root):
    """Crea las fuentes (después de crear la ventana) y configura ttk."""
    titulo = _familia(["Bebas Neue", "Impact", "Haettenschweiler", "Arial Black"])
    texto = _familia(["Segoe UI", "Open Sans", "Helvetica", "Arial"])
    mono = _familia(["Consolas", "Cascadia Mono", "Courier New", "DejaVu Sans Mono"], "TkFixedFont")
    F.update({
        "marca": (titulo, 40),
        "h1": (texto, 20, "bold"),
        "h2": (texto, 15, "bold"),
        "normal": (texto, 12),
        "normal_b": (texto, 12, "bold"),
        "menu": (texto, 12, "italic"),
        "boton": (texto, 12, "bold italic"),
        "peq": (texto, 10),
        "mesa": (texto, 13),
        "grande": (texto, 30, "bold"),
        "mono": (mono, 12),
    })
    root.configure(bg=C["lateral"])
    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass
    s.configure("Treeview", font=F["normal"], rowheight=32, background="white",
                fieldbackground="white", bordercolor=C["linea"], borderwidth=1)
    s.configure("Treeview.Heading", font=F["normal_b"], background=C["tarjeta"], relief="flat")
    s.map("Treeview", background=[("selected", C["azul"])], foreground=[("selected", "black")])
    s.configure("TCombobox", padding=6)
    root.option_add("*TCombobox*Listbox.font", F["normal"])
