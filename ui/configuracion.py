"""Configuración de la cuenta: datos personales, foto y contraseña."""
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, Campo, PanelRedondeado, miniatura, mostrar_errores
from util import imagenes


class PantallaConfiguracion(PantallaBase):
    MENU_ACTIVO = "CONFIGURACIÓN"

    def construir(self, contenido):
        self.u = self.svc.usuarios.obtener(self.app.usuario.id)
        fila = tk.Frame(contenido, bg="white")
        fila.pack(fill="both", expand=True, padx=40, pady=30)
        fila.columnconfigure((0, 1), weight=1, uniform="c")

        datos = PanelRedondeado(fila)
        datos.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        d = datos.interior
        tk.Label(d, text="Mis datos", font=F["h2"], bg="white", anchor="w").pack(fill="x")
        foto = tk.Frame(d, bg="white")
        foto.pack(fill="x", pady=10)
        self.cont_foto = tk.Frame(foto, bg="white")
        self.cont_foto.pack(side="left")
        self._pintar_foto()
        BotonRedondeado(foto, "Cambiar foto", self._cambiar_foto, ancho=150).pack(side="left", padx=16)
        grid = tk.Frame(d, bg="white")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1, uniform="g")
        self.campos = {"nombres": Campo(grid, "NOMBRES", ancho=16),
                       "apellidos": Campo(grid, "APELLIDOS", ancho=16),
                       "telefono": Campo(grid, "TELÉFONO", ancho=16, ayuda="Lo ve el administrador")}
        correo = Campo(grid, "CORREO", ancho=16)
        for i, c in enumerate((*self.campos.values(), correo)):
            c.grid(row=i // 2, column=i % 2, sticky="ew", padx=(0 if i % 2 == 0 else 8, 0), pady=2)
        self.campos["nombres"].poner(self.u.nombres)
        self.campos["apellidos"].poner(self.u.apellidos)
        self.campos["telefono"].poner(self.u.telefono)
        correo.poner(self.u.correo)
        correo.solo_lectura()
        BotonRedondeado(d, "Guardar cambios", self._guardar, ancho=190, estilo="lleno",
                        fuente=F["boton"]).pack(anchor="e", pady=(8, 0))

        clave = PanelRedondeado(fila)
        clave.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        c = clave.interior
        tk.Label(c, text="Cambiar contraseña", font=F["h2"], bg="white", anchor="w").pack(fill="x")
        self.claves = {"actual": Campo(c, "CONTRASEÑA ACTUAL", oculto=True),
                       "nueva": Campo(c, "NUEVA CONTRASEÑA", oculto=True, ayuda="Mínimo 6, con letras y números"),
                       "verificacion": Campo(c, "VERIFICAR CONTRASEÑA", oculto=True)}
        for campo in self.claves.values():
            campo.pack(fill="x", pady=4)
        BotonRedondeado(c, "Actualizar contraseña", self._clave, ancho=230, estilo="lleno",
                        fuente=F["boton"]).pack(anchor="e", pady=(12, 0))

    def _pintar_foto(self):
        for w in self.cont_foto.winfo_children():
            w.destroy()
        miniatura(self.cont_foto, imagenes.ruta_usuario(self.u), 110, 110,
                  self.u.nombre_completo).pack()

    def _cambiar_foto(self):
        ruta = filedialog.askopenfilename(parent=self, title="Elegir foto",
                                          filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.webp")])
        if not ruta:
            return
        ext = os.path.splitext(ruta)[1].lower()
        os.makedirs(imagenes.CARPETA_PERSONAL, exist_ok=True)
        destino = os.path.join(imagenes.CARPETA_PERSONAL, f"{self.u.id}{ext}")
        shutil.copyfile(ruta, destino)
        relativa = os.path.relpath(destino, imagenes.BASE).replace("\\", "/")
        self.svc.usuarios.actualizar_foto(self.u.id, relativa)
        self.u.foto = relativa
        self._pintar_foto()
        self.app.aviso("Foto actualizada")

    def _guardar(self):
        v = {k: c.valor() for k, c in self.campos.items()}
        errores = self.svc.usuarios.actualizar_perfil(self.u.id, v["nombres"], v["apellidos"], v["telefono"])
        if not mostrar_errores(self.campos, errores):
            self.app.usuario = self.svc.usuarios.obtener(self.u.id)
            self.app.ir("ui.configuracion:PantallaConfiguracion")
            self.app.aviso("Datos guardados")

    def _clave(self):
        v = {k: c.valor() for k, c in self.claves.items()}
        errores = self.svc.usuarios.cambiar_password(self.u.id, v["actual"], v["nueva"], v["verificacion"])
        if not mostrar_errores(self.claves, errores):
            for c in self.claves.values():
                c.poner("")
            self.app.aviso("Contraseña actualizada")
