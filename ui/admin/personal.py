"""Personal (boceto): foto, nombre y estado; al tocar una tarjeta se ve su contacto."""
import tkinter as tk
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, MarcoScroll, miniatura, centrar
from util import imagenes

FOTO = 140


class PantallaPersonal(PantallaBase):
    MENU_ACTIVO = "PERSONAL"

    def construir(self, contenido):
        cab = tk.Frame(contenido, bg="white")
        cab.pack(fill="x", padx=40, pady=(24, 4))
        self.titulo(cab, "Personal", "Toque una tarjeta para ver el contacto.")
        self.grilla = MarcoScroll(contenido, bg="white")
        self.grilla.pack(fill="both", expand=True, padx=30, pady=10)
        self.grilla.canvas.bind("<Configure>", lambda e: self._acomodar(), add="+")
        self.tarjetas = [self._tarjeta(u) for u in self.svc.usuarios.listar_personal()]
        self._cols = None
        self._acomodar()

    def _tarjeta(self, u):
        t = tk.Frame(self.grilla.interior, bg="white", cursor="hand2")
        miniatura(t, imagenes.ruta_usuario(u), FOTO, FOTO, u.nombre_completo).pack()
        tk.Label(t, text=u.nombre_completo, font=F["normal_b"], bg="white", wraplength=FOTO + 20).pack(pady=(6, 0))
        trabajando = u.estado == "TRABAJANDO"
        tk.Label(t, text="Trabajando" if trabajando else "Ausente", font=F["peq"], bg="white",
                 fg=C["verde"] if trabajando else C["suave"]).pack()
        if u.es_admin:
            tk.Label(t, text="Administrador", font=F["peq"], bg="white", fg=C["rojo"]).pack()
        for w in (t, *t.winfo_children()):
            w.bind("<Button-1>", lambda e, x=u: self._contacto(x))
        return t

    def _acomodar(self):
        ancho = self.grilla.canvas.winfo_width()
        cols = max(2, ancho // (FOTO + 60)) if ancho > 1 else 5
        if cols == self._cols:
            return
        self._cols = cols
        for i, t in enumerate(self.tarjetas):
            t.grid(row=i // cols, column=i % cols, padx=18, pady=16, sticky="n")

    def _contacto(self, u):
        v = tk.Toplevel(self)
        v.title("Contacto")
        v.configure(bg="white", padx=30, pady=24)
        v.resizable(False, False)
        v.transient(self.winfo_toplevel())
        miniatura(v, imagenes.ruta_usuario(u), 120, 120, u.nombre_completo).pack()
        tk.Label(v, text=u.nombre_completo, font=F["h2"], bg="white").pack(pady=(10, 0))
        tk.Label(v, text="Administrador" if u.es_admin else "Personal de salón", font=F["peq"],
                 fg=C["suave"], bg="white").pack()
        nac = u.fecha_nacimiento.strftime("%d/%m/%Y") if hasattr(u.fecha_nacimiento, "strftime") \
            else (u.fecha_nacimiento or "No registrada")
        for etiqueta, valor in (("Correo", u.correo), ("Teléfono", u.telefono or "No registrado"),
                                ("Nacimiento", nac),
                                ("Estado", "Trabajando" if u.estado == "TRABAJANDO" else "Ausente")):
            f = tk.Frame(v, bg="white")
            f.pack(fill="x", pady=2)
            tk.Label(f, text=etiqueta, font=F["normal_b"], bg="white", width=11, anchor="w").pack(side="left")
            tk.Label(f, text=valor, font=F["normal"], bg="white", anchor="w").pack(side="left")
        BotonRedondeado(v, "Cerrar", v.destroy, ancho=120).pack(pady=(16, 0))
        centrar(v, self)
        v.grab_set()
