"""Registro de ventas (boceto): filtros por fecha y tipo de pago, detalle y total."""
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado, PanelRedondeado
from util.imagenes import BASE

PERIODOS = {"Diario": "DIARIO", "Mensual": "MENSUAL", "Trimestral": "TRIMESTRAL"}
TIPOS = {"Todos": None, "Efectivo": "EFECTIVO", "Tarjeta": "TARJETA", "Yape": "YAPE"}


class PantallaVentas(PantallaBase):
    MENU_ACTIVO = "REGISTRO DE\nVENTAS"

    def construir(self, contenido):
        panel = PanelRedondeado(contenido)
        panel.pack(fill="both", expand=True, padx=50, pady=30)
        p = panel.interior
        tk.Label(p, text="Registro de ventas", font=(F["h1"][0], F["h1"][1], "bold italic"),
                 bg="white", anchor="w").pack(fill="x")
        filtros = tk.Frame(p, bg="white")
        filtros.pack(fill="x", pady=12)
        self.var_periodo = tk.StringVar(value="Diario")
        self.var_tipo = tk.StringVar(value="Todos")
        for etiqueta, var, opciones in (("Fecha", self.var_periodo, PERIODOS),
                                        ("Tipo", self.var_tipo, TIPOS)):
            caja = tk.Frame(filtros, bg="white", relief="solid", bd=2, padx=12, pady=6)
            caja.pack(side="left", padx=(0, 16))
            tk.Label(caja, text=etiqueta, font=F["normal_b"], bg="white").pack(side="left", padx=(0, 8))
            cb = ttk.Combobox(caja, textvariable=var, values=list(opciones), state="readonly",
                              width=12, font=F["normal"])
            cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>", lambda e: self.cargar())
        BotonRedondeado(filtros, "Exportar CSV", self._exportar, ancho=160, alto=40).pack(side="right")

        cuerpo = tk.Frame(p, bg="white")
        cuerpo.pack(fill="both", expand=True)
        cols = (("id", "N° pedido", 90, "center"), ("fecha", "Fecha", 150, "center"),
                ("mesa", "Mesa", 60, "center"), ("detalle", "Detalle del pedido", 420, "w"),
                ("tipo", "Tipo", 100, "center"), ("monto", "Monto", 110, "e"))
        self.tabla = ttk.Treeview(cuerpo, columns=[c[0] for c in cols], show="headings")
        for c, t, w, a in cols:
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=w, anchor=a, stretch=(c == "detalle"))
        barra = ttk.Scrollbar(cuerpo, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="left", fill="y")

        pie = tk.Frame(p, bg="white")
        pie.pack(fill="x", pady=(12, 0))
        self.lbl_resumen = tk.Label(pie, font=F["normal"], fg=C["suave"], bg="white")
        self.lbl_resumen.pack(side="left")
        self.lbl_total = tk.Label(pie, font=F["h2"], bg="white", relief="solid", bd=2, padx=18, pady=6)
        self.lbl_total.pack(side="right")
        self.cargar()

    def cargar(self):
        self.ventas = self.svc.reportes.ventas(PERIODOS[self.var_periodo.get()],
                                               TIPOS[self.var_tipo.get()])
        self.tabla.delete(*self.tabla.get_children())
        for v in self.ventas:
            fecha = v["fecha"].strftime("%d/%m/%Y %H:%M") if hasattr(v["fecha"], "strftime") else str(v["fecha"])[:16]
            self.tabla.insert("", "end", values=(v["id"], fecha, v["mesa"], v["detalle"],
                                                 (v["metodo"] or "").capitalize(), f"S/ {v['total']:.2f}"))
        total = sum(v["total"] for v in self.ventas)
        n = len(self.ventas)
        promedio = total / n if n else 0
        self.lbl_resumen.config(text=f"{n} pedido{'s' if n != 1 else ''}   Ticket promedio: S/ {promedio:.2f}")
        self.lbl_total.config(text=f"TOTAL  S/ {total:.2f}")

    def _exportar(self):
        carpeta = os.path.join(BASE, "reportes")
        os.makedirs(carpeta, exist_ok=True)
        nombre = f"ventas_{self.var_periodo.get().lower()}_{datetime.now():%Y%m%d_%H%M}.csv"
        ruta = os.path.join(carpeta, nombre)
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["N° pedido", "Fecha", "Mesa", "Detalle", "Tipo", "Monto"])
            for v in self.ventas:
                w.writerow([v["id"], v["fecha"], v["mesa"], v["detalle"], v["metodo"], f"{v['total']:.2f}"])
        self.app.aviso(f"Exportado a reportes/{nombre}")
