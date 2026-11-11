"""Pantallas de inicio de sesión y registro (bocetos LOGIN / REGISTRO)."""
import tkinter as tk
from ui.tema import C, F
from ui.widgets import BotonRedondeado, Campo, PanelRedondeado, mostrar_errores


class _PantallaAcceso(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["lateral"])
        self.app, self.svc = app, app.svc
        tk.Label(self, text="CHIFA SHUN FA", font=F["marca"], bg=C["lateral"]).pack(pady=(28, 0))
        tk.Frame(self, bg=C["linea"], height=5, width=380).pack()
        self.panel = PanelRedondeado(self, relleno=36)
        self.panel.pack(pady=24, ipadx=10)

    def enlace(self, parent, pregunta, accion, comando):
        f = tk.Frame(parent, bg="white")
        f.pack(pady=(14, 0))
        tk.Label(f, text=pregunta, font=F["peq"], bg="white").pack(side="left")
        l = tk.Label(f, text=accion, font=(F["peq"][0], F["peq"][1], "bold underline"),
                     fg=C["rojo"], bg="white", cursor="hand2")
        l.pack(side="left", padx=4)
        l.bind("<Button-1>", lambda e: comando())


class PantallaLogin(_PantallaAcceso):
    def __init__(self, parent, app, correo=""):
        super().__init__(parent, app)
        p = self.panel.interior
        tk.Label(p, text="Iniciar sesión", font=F["h1"], bg="white").pack(pady=(0, 16))
        self.campos = {"correo": Campo(p, "CORREO"), "password": Campo(p, "CONTRASEÑA", oculto=True)}
        for c in self.campos.values():
            c.pack(fill="x", pady=4)
        self.campos["correo"].poner(correo)
        BotonRedondeado(p, "INGRESAR", self.ingresar, ancho=200, alto=46, estilo="lleno",
                        fuente=F["boton"]).pack(pady=(16, 0))
        self.enlace(p, "¿No tiene una cuenta?", "Regístrese aquí",
                    lambda: app.ir("ui.login:PantallaRegistro"))
        for c in self.campos.values():
            c.entry.bind("<Return>", lambda e: self.ingresar())
        (self.campos["password"] if correo else self.campos["correo"]).entry.focus_set()

    def ingresar(self):
        usuario, errores = self.svc.usuarios.iniciar_sesion(
            self.campos["correo"].valor(), self.campos["password"].valor())
        if not mostrar_errores(self.campos, errores):
            self.app.iniciar_sesion(usuario)
            self.app.aviso(f"Bienvenido, {usuario.nombres}")


class PantallaRegistro(_PantallaAcceso):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        p = self.panel.interior
        tk.Label(p, text="Complete los datos", font=F["h1"], bg="white").pack(pady=(0, 10))
        grid = tk.Frame(p, bg="white")
        grid.pack()
        defs = [("nombres", "NOMBRES", False, None), ("apellidos", "APELLIDOS", False, None),
                ("correo", "CORREO", False, None), ("fecha", "FECHA DE NACIMIENTO", False, "DD/MM/AAAA"),
                ("password", "CONTRASEÑA", True, "Mínimo 6, con letras y números"),
                ("verificacion", "VERIFICAR CONTRASEÑA", True, None)]
        self.campos = {}
        for i, (clave, etiqueta, oculto, ayuda) in enumerate(defs):
            c = Campo(grid, etiqueta, oculto=oculto, ancho=26, ayuda=ayuda)
            c.grid(row=i // 2, column=i % 2, padx=10, pady=4, sticky="ew")
            c.entry.bind("<Return>", lambda e: self.registrar())
            self.campos[clave] = c
        BotonRedondeado(p, "REGISTRARSE", self.registrar, ancho=220, alto=46, estilo="lleno",
                        fuente=F["boton"]).pack(pady=(14, 0))
        self.enlace(p, "¿Ya tiene una cuenta?", "Inicie sesión aquí",
                    lambda: app.ir("ui.login:PantallaLogin"))
        self.campos["nombres"].entry.focus_set()

    def registrar(self):
        v = {k: c.valor() for k, c in self.campos.items()}
        usuario, errores = self.svc.usuarios.registrar(
            v["nombres"], v["apellidos"], v["correo"], v["password"], v["verificacion"], v["fecha"])
        if not mostrar_errores(self.campos, errores):
            self.app.ir("ui.login:PantallaLogin", correo=usuario.correo)
            self.app.aviso("Cuenta creada. Ya puede iniciar sesión.")
