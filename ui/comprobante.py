"""Boleta o factura del pago, con opción de guardarla como archivo de texto."""
import os
import tkinter as tk
from ui.layout import PantallaBase
from ui.tema import C, F
from ui.widgets import BotonRedondeado
from services import comprobante
from util.imagenes import BASE


class PantallaComprobante(PantallaBase):
    @property
    def MENU_ACTIVO(self):
        return "MESAS" if self.app.usuario.es_admin else "EN ORDEN"

    def construir(self, contenido, pedido, tipo="BOLETA", cliente=None, ruc=None, paga_con=None):
        self.pedido, self.tipo = pedido, tipo
        self.texto = comprobante.generar(pedido, tipo, cliente, ruc, paga_con)
        cont = tk.Frame(contenido, bg="white")
        cont.pack(expand=True)
        papel = tk.Frame(cont, bg="#FAFAF7", relief="solid", bd=1, padx=26, pady=20)
        papel.pack(pady=(20, 16))
        tk.Label(papel, text=self.texto, font=F["mono"], bg="#FAFAF7", justify="left").pack()
        botones = tk.Frame(cont, bg="white")
        botones.pack()
        BotonRedondeado(botones, "Guardar comprobante", self._guardar, ancho=220).pack(side="left", padx=8)
        BotonRedondeado(botones, "VOLVER A MESAS", self.app.ir_inicio, ancho=200, estilo="lleno",
                        fuente=F["boton"]).pack(side="left", padx=8)
        self.lbl = tk.Label(cont, text="", font=F["peq"], fg=C["suave"], bg="white")
        self.lbl.pack(pady=8)

    def _guardar(self):
        carpeta = os.path.join(BASE, "comprobantes")
        os.makedirs(carpeta, exist_ok=True)
        serie = "F001" if self.tipo == "FACTURA" else "B001"
        ruta = os.path.join(carpeta, f"{serie}-{self.pedido.id:08d}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.texto)
        self.lbl.config(text=f"Guardado en {ruta}")
        self.app.aviso("Comprobante guardado")
