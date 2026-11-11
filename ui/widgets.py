"""Widgets reutilizables: botones redondeados, paneles, campos con alerta, scroll."""
import tkinter as tk
from ui.tema import C, F
from util import imagenes


def rect_redondeado(canvas, x1, y1, x2, y2, r=12, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    puntos = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
              x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(puntos, smooth=True, **kw)


class BotonRedondeado(tk.Canvas):
    """Botón con borde redondeado como en los bocetos.
    estilo: 'contorno' (borde negro) o 'lleno' (fondo negro, texto blanco)."""

    def __init__(self, parent, texto, comando=None, ancho=160, alto=42, estilo="contorno",
                 fuente=None, activo=False):
        bg = parent.cget("bg")
        super().__init__(parent, width=ancho, height=alto, bg=bg, highlightthickness=0,
                         cursor="hand2", takefocus=1)
        self.texto, self.comando, self.estilo = texto, comando, estilo
        self.fuente = fuente or F["menu"]
        self.activo, self._hover, self.habilitado = activo, False, True
        self.bind("<Configure>", lambda e: self._dibujar())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._click)
        self.bind("<Return>", self._click)
        self.bind("<space>", self._click)
        self.bind("<FocusIn>", lambda e: self._dibujar())
        self.bind("<FocusOut>", lambda e: self._dibujar())
        self._dibujar()

    def _set_hover(self, v):
        self._hover = v
        self._dibujar()

    def _click(self, _e=None):
        if self.habilitado and self.comando:
            self.comando()

    def set_activo(self, v):
        self.activo = v
        self._dibujar()

    def set_texto(self, t):
        self.texto = t
        self._dibujar()

    def set_habilitado(self, v):
        self.habilitado = v
        self.configure(cursor="hand2" if v else "arrow")
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1:
            w, h = int(self.cget("width")), int(self.cget("height"))
        lleno = self.estilo == "lleno"
        if lleno:
            fondo = C["rojo"] if (self.activo or self._hover) else "#000000"
            color_txt = "white"
        else:
            fondo = "#EEF1F5" if self._hover else "white"
            color_txt = C["rojo"] if self.activo else C["texto"]
        if not self.habilitado:
            fondo, color_txt = "#E5E7EB", "#9CA3AF"
        try:
            grosor = 3 if self.focus_get() is self else 2
        except (KeyError, tk.TclError):
            grosor = 2
        rect_redondeado(self, 2, 2, w - 2, h - 2, r=12, fill=fondo,
                        outline=C["linea"] if self.habilitado else "#9CA3AF", width=grosor)
        self.create_text(w / 2, h / 2, text=self.texto, fill=color_txt, font=self.fuente,
                         justify="center", width=w - 12)


class PanelRedondeado(tk.Frame):
    """Marco blanco con borde negro redondeado; el contenido va en .interior"""

    def __init__(self, parent, radio=24, relleno=28, fondo="white", borde=None, grosor=2):
        super().__init__(parent, bg=parent.cget("bg"))
        self.radio, self.relleno, self.fondo = radio, relleno, fondo
        self.borde = C["linea"] if borde is None else borde
        self.grosor = grosor
        self.canvas = tk.Canvas(self, bg=parent.cget("bg"), highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.interior = tk.Frame(self, bg=fondo)
        self.interior.pack(fill="both", expand=True, padx=relleno, pady=relleno)
        self.bind("<Configure>", self._dibujar)

    def _dibujar(self, _e=None):
        self.canvas.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        rect_redondeado(self.canvas, 2, 2, w - 2, h - 2, r=self.radio, fill=self.fondo,
                        outline=self.borde or self.fondo, width=self.grosor)


class Campo(tk.Frame):
    """Etiqueta + caja de texto + alerta de verificación debajo (como en el boceto)."""

    def __init__(self, parent, etiqueta, oculto=False, ancho=34, ayuda=None):
        super().__init__(parent, bg=parent.cget("bg"))
        tk.Label(self, text=etiqueta, font=F["normal_b"], bg=self.cget("bg"),
                 anchor="w").pack(fill="x")
        borde = tk.Frame(self, bg=C["linea"], padx=2, pady=2)
        borde.pack(fill="x", pady=(4, 0))
        self.var = tk.StringVar()
        self.entry = tk.Entry(borde, textvariable=self.var, font=F["normal"], relief="flat",
                              width=ancho, show="•" if oculto else "")
        self.entry.pack(fill="x", ipady=6, ipadx=6)
        self.alerta = tk.Label(self, text=ayuda or "", font=F["peq"], bg=self.cget("bg"),
                               fg=C["suave"], anchor="w", justify="left")
        self.alerta.pack(fill="x")
        self._ayuda = ayuda or ""
        self.var.trace_add("write", lambda *a: self.limpiar())

    def valor(self):
        return self.var.get()

    def poner(self, texto):
        self.var.set(texto or "")

    def error(self, msg):
        self.alerta.config(text=msg, fg=C["rojo"])

    def limpiar(self):
        self.alerta.config(text=self._ayuda, fg=C["suave"])

    def solo_lectura(self):
        self.entry.config(state="readonly", readonlybackground="#F3F4F6")


def mostrar_errores(campos, errores):
    """campos: {clave: Campo}. Marca errores y devuelve True si hubo alguno."""
    for clave, campo in campos.items():
        if clave in errores:
            campo.error(errores[clave])
        else:
            campo.limpiar()
    return bool(errores)


class MarcoScroll(tk.Frame):
    """Contenedor con scroll vertical (rueda del mouse y arrastre en pantallas táctiles)."""

    def __init__(self, parent, bg="white"):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.barra = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.interior = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.barra.pack(side="right", fill="y")
        self.interior.bind("<Configure>",
                           lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.bind("<Enter>", lambda e: self._rueda(True))
        self.bind("<Leave>", lambda e: self._rueda(False))

    def _rueda(self, activar):
        if activar:
            self.bind_all("<MouseWheel>", self._mover)
            self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
            self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))
        else:
            for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.unbind_all(ev)

    def _mover(self, e):
        self.canvas.yview_scroll(int(-e.delta / 120) * 2, "units")

    def arriba(self):
        self.canvas.yview_moveto(0)


TONOS = ("#9AA8B8", "#B08D7A", "#8FA392", "#A39070", "#8E95B5", "#B58A8F")


def miniatura(parent, ruta, ancho, alto, texto, bg=None, color=None):
    """Canvas con la imagen recortada; si no hay imagen, un recuadro con iniciales."""
    cv = tk.Canvas(parent, width=ancho, height=alto, highlightthickness=0,
                   bg=bg or parent.cget("bg"), cursor="hand2")
    img = imagenes.cargar(ruta, ancho, alto)
    if img is not None:
        cv.create_image(0, 0, image=img, anchor="nw")
        cv.imagen = img  # mantener referencia
    else:
        color = color or TONOS[sum(map(ord, texto)) % len(TONOS)]
        cv.create_rectangle(0, 0, ancho, alto, fill=color, outline="")
        palabras = [p for p in texto.split() if p[0].isalpha()]
        iniciales = "".join(p[0] for p in palabras[:2]).upper()
        cv.create_text(ancho / 2, alto / 2, text=iniciales, font=F["grande"], fill="white")
    return cv


def entrada_con_placeholder(parent, placeholder, font=None, ancho=40):
    """Entry con texto guía gris que desaparece al escribir. Devuelve (frame, StringVar)."""
    borde = tk.Frame(parent, bg=C["linea"], padx=2, pady=2)
    var = tk.StringVar()
    e = tk.Entry(borde, textvariable=var, font=font or F["normal"], relief="flat", width=ancho)
    e.pack(fill="both", expand=True, ipady=8, ipadx=8)
    guia = tk.Label(borde, text=placeholder, font=font or F["normal"], fg="#9CA3AF", bg="white",
                    cursor="xterm")
    def actualizar(*_):
        if var.get():
            guia.place_forget()
        else:
            guia.place(x=10, rely=0.5, anchor="w")
    guia.bind("<Button-1>", lambda ev: e.focus_set())
    var.trace_add("write", actualizar)
    actualizar()
    borde.entry = e
    return borde, var


def centrar(ventana, padre):
    """Coloca una ventana emergente en el centro de la principal."""
    ventana.update_idletasks()
    raiz = padre.winfo_toplevel()
    x = raiz.winfo_rootx() + (raiz.winfo_width() - ventana.winfo_reqwidth()) // 2
    y = raiz.winfo_rooty() + (raiz.winfo_height() - ventana.winfo_reqheight()) // 3
    ventana.geometry(f"+{max(0, x)}+{max(0, y)}")
