"""Plantilla común: cabecera con la marca, barra lateral con el menú según el rol,
área blanca de contenido y enlaces 'Acerca de' / 'FAQ'."""
import tkinter as tk
from tkinter import messagebox
from ui.tema import C, F
from ui.widgets import BotonRedondeado

MENU_USUARIO = [
    ("EN ORDEN", "ui.usuario.mesas:PantallaMesasUsuario"),
    ("COCINA", "ui.usuario.cocina:PantallaCocina"),
    ("CONFIGURACIÓN", "ui.configuracion:PantallaConfiguracion"),
]
MENU_ADMIN = [
    ("MESAS", "ui.admin.mesas:PantallaMesasAdmin"),
    ("PERSONAL", "ui.admin.personal:PantallaPersonal"),
    ("REGISTRO DE\nVENTAS", "ui.admin.ventas:PantallaVentas"),
    ("CONFIGURACIÓN", "ui.configuracion:PantallaConfiguracion"),
]

ACERCA = ("POS Chifa Shun Fa\nVersión 3.0\n\n"
          "Proyecto de POO-2 del equipo POODEROSOS.\n"
          "Python + Tkinter + SQL Server.")
FAQ = ("¿Cómo tomo un pedido?\nToque una mesa azul, elija los platos y pulse Finalizar orden.\n\n"
       "¿Qué significan los colores?\nAzul: mesa libre. Rojo: mesa ocupada.\n\n"
       "¿Cómo agrego platos a una mesa ocupada?\nToque la mesa roja y pulse Agregar platos.\n\n"
       "¿Cómo cobro?\nToque la mesa roja, pulse Cobrar y elija Efectivo, Tarjeta o Yape.")


class PantallaBase(tk.Frame):
    MENU_ACTIVO = None   # texto del botón del menú que se marca en rojo

    def __init__(self, parent, app, **kw):
        super().__init__(parent, bg=C["lateral"])
        self.app = app
        self.svc = app.svc
        self._tareas = []
        self._construir_marco()
        self.construir(self.contenido, **kw)

    # Las subclases implementan esto
    def construir(self, contenido, **kw):
        raise NotImplementedError

    # ---------- Marco común ----------
    def _construir_marco(self):
        cab = tk.Frame(self, bg=C["lateral"], height=100)
        cab.pack(fill="x")
        cab.pack_propagate(False)
        marca = tk.Frame(cab, bg=C["lateral"])
        marca.place(x=196, y=8)
        tk.Label(marca, text="CHIFA SHUN FA", font=F["marca"], bg=C["lateral"],
                 fg=C["texto"]).pack(anchor="w")
        tk.Frame(marca, bg=C["linea"], height=5).pack(fill="x")

        cuerpo = tk.Frame(self, bg=C["lateral"])
        cuerpo.pack(fill="both", expand=True)
        lateral = tk.Frame(cuerpo, bg=C["lateral"], width=255)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.contenido = tk.Frame(cuerpo, bg=C["fondo"])
        self.contenido.pack(side="left", fill="both", expand=True)

        u = self.app.usuario
        menu = MENU_ADMIN if u.es_admin else MENU_USUARIO
        caja = tk.Frame(lateral, bg=C["lateral"])
        caja.pack(pady=(24, 0))
        for texto, ruta in menu:
            alto = 64 if "\n" in texto else 42
            BotonRedondeado(caja, texto, lambda r=ruta: self.app.ir(r), ancho=160, alto=alto,
                            activo=(texto == self.MENU_ACTIVO)).pack(pady=7)
        BotonRedondeado(caja, "SALIR", self.app.salir, ancho=160).pack(pady=7)

        pie = tk.Frame(lateral, bg=C["lateral"])
        pie.pack(side="bottom", fill="x", padx=18, pady=12)
        for texto, msg in (("Acerca de", ACERCA), ("FAQ", FAQ)):
            l = tk.Label(pie, text=texto, font=F["peq"], bg=C["lateral"], cursor="hand2")
            l.pack(side="left", expand=True)
            l.bind("<Button-1>", lambda e, t=texto, m=msg: messagebox.showinfo(t, m, parent=self))
        sesion = tk.Frame(lateral, bg=C["lateral"])
        sesion.pack(side="bottom", fill="x", padx=18, pady=(0, 6))
        tk.Label(sesion, text=u.nombre_completo, font=F["normal_b"], bg=C["lateral"],
                 anchor="w", wraplength=210, justify="left").pack(fill="x")
        tk.Label(sesion, text="Administrador" if u.es_admin else "Personal de salón",
                 font=F["peq"], bg=C["lateral"], fg=C["suave"], anchor="w").pack(fill="x")

    # ---------- Tareas periódicas (se cancelan al cambiar de pantalla) ----------
    def cada(self, ms, funcion):
        def ciclo():
            if not self.winfo_exists():
                return
            try:
                funcion()
            finally:
                self._tareas.append(self.after(ms, ciclo))
        self._tareas.append(self.after(ms, ciclo))

    def destroy(self):
        for t in self._tareas:
            try:
                self.after_cancel(t)
            except tk.TclError:
                pass
        super().destroy()

    def titulo(self, parent, texto, sub=None):
        tk.Label(parent, text=texto, font=F["h1"], bg=parent.cget("bg"), anchor="w").pack(fill="x")
        if sub:
            tk.Label(parent, text=sub, font=F["normal"], fg=C["suave"], bg=parent.cget("bg"),
                     anchor="w").pack(fill="x", pady=(2, 0))
