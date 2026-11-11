"""Plano del salón: réplica de la distribución real de las 23 mesas (bocetos)."""
import tkinter as tk
from ui.tema import C, F

# (x, y, ancho, alto) de cada mesa sobre un plano de 1200 x 640, tomados del boceto
CHICA, LARGA = (110, 89), (235, 89)
PLANO = {
    7: (138, 90, *CHICA), 6: (264, 90, *CHICA), 5: (390, 90, *CHICA), 4: (516, 90, *CHICA),
    3: (746, 90, *CHICA), 2: (872, 90, *CHICA), 1: (998, 90, *CHICA),
    8: (29, 202, *CHICA), 9: (29, 313, *CHICA), 10: (29, 424, *CHICA), 11: (29, 535, *CHICA),
    12: (210, 220, *LARGA), 13: (210, 371, *LARGA), 14: (210, 523, *LARGA),
    15: (516, 230, *CHICA), 16: (516, 371, *CHICA), 17: (516, 511, *CHICA),
    18: (750, 232, *CHICA), 19: (750, 373, *CHICA), 20: (750, 513, *CHICA),
    21: (933, 222, *LARGA), 22: (933, 373, *LARGA), 23: (933, 525, *LARGA),
}
ANCHO_PLANO, ALTO_PLANO = 1200, 640


class MapaSalon(tk.Canvas):
    def __init__(self, parent, al_tocar, leyenda=True):
        super().__init__(parent, bg=C["fondo"], highlightthickness=0)
        self.al_tocar, self.leyenda = al_tocar, leyenda
        self.mesas = []
        self.bind("<Configure>", lambda e: self.dibujar())

    def actualizar(self, mesas):
        self.mesas = mesas
        self.dibujar()

    def dibujar(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or not self.mesas:
            return
        alto_leyenda = 40 if self.leyenda else 0
        s = min(w / ANCHO_PLANO, (h - alto_leyenda) / ALTO_PLANO)
        ox = (w - ANCHO_PLANO * s) / 2
        oy = max(0, (h - alto_leyenda - ALTO_PLANO * s) / 2)
        radio = max(14, 21 * s)
        fuente = (F["mesa"][0], max(10, int(14 * s)), "bold")
        for mesa in self.mesas:
            if mesa.numero not in PLANO:
                continue
            x, y, mw, mh = PLANO[mesa.numero]
            x1, y1 = ox + x * s, oy + y * s
            x2, y2 = x1 + mw * s, y1 + mh * s
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            etiqueta = f"mesa{mesa.id}"
            libre = mesa.esta_libre
            self.create_rectangle(x1, y1, x2, y2, fill=C["mesa"], outline="",
                                  tags=(etiqueta, f"{etiqueta}_rect"))
            self.create_oval(cx - radio, cy - radio, cx + radio, cy + radio,
                             fill=C["azul"] if libre else C["rojo"], outline="", tags=etiqueta)
            self.create_text(cx, cy, text=str(mesa.numero), font=fuente,
                             fill="black" if libre else "white", tags=etiqueta)
            self.tag_bind(etiqueta, "<Button-1>", lambda e, m=mesa: self.al_tocar(m))
            self.tag_bind(etiqueta, "<Enter>", lambda e, t=etiqueta: self._hover(t, True))
            self.tag_bind(etiqueta, "<Leave>", lambda e, t=etiqueta: self._hover(t, False))
        if self.leyenda:
            ly = h - alto_leyenda / 2
            for i, (color, texto) in enumerate(((C["rojo"], "Ocupada"), (C["azul"], "Libre"))):
                lx = ox + 20 + i * 140
                self.create_oval(lx, ly - 9, lx + 18, ly + 9, fill=color, outline="")
                self.create_text(lx + 28, ly, text=texto, anchor="w", font=F["normal_b"])

    def _hover(self, etiqueta, dentro):
        self.itemconfigure(f"{etiqueta}_rect", fill=C["mesa_hover"] if dentro else C["mesa"])
        self.configure(cursor="hand2" if dentro else "")
