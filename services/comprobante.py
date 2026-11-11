"""Genera el texto de la boleta o factura (comprobante interno del local)."""
from datetime import datetime

IGV = 0.18
ANCHO = 42


def generar(pedido, tipo="BOLETA", cliente=None, ruc=None, paga_con=None):
    total = pedido.total
    base = total / (1 + IGV)
    serie = "F001" if tipo == "FACTURA" else "B001"
    titulo = "FACTURA DE VENTA" if tipo == "FACTURA" else "BOLETA DE VENTA"
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    l = []
    centro = lambda t: l.append(t.center(ANCHO))
    raya = lambda: l.append("-" * ANCHO)
    centro("CHIFA SHUN FA")
    centro(titulo)
    centro(f"{serie}-{pedido.id:08d}")
    raya()
    l.append(f"Fecha: {fecha}")
    l.append(f"Mesa: {pedido.numero_mesa or '-'}")
    if pedido.mozo:
        l.append(f"Atendido por: {pedido.mozo}")
    if tipo == "FACTURA":
        l.append(f"RUC: {ruc}")
        l.append(f"Razón social: {cliente}")
    elif cliente:
        l.append(f"Cliente: {cliente}")
    raya()
    for d in pedido.detalles:
        nombre = d.nombre_plato[:24]
        l.append(f"{d.cantidad:>2} x {nombre:<24}{d.subtotal:>11.2f}")
    raya()
    l.append(f"{'Op. gravada':<28}S/ {base:>9.2f}")
    l.append(f"{'IGV 18%':<28}S/ {total - base:>9.2f}")
    l.append(f"{'TOTAL':<28}S/ {total:>9.2f}")
    raya()
    l.append(f"Pago: {(pedido.metodo_pago or '').capitalize()}")
    if paga_con:
        l.append(f"Paga con: S/ {paga_con:.2f}   Vuelto: S/ {paga_con - total:.2f}")
    raya()
    centro("Gracias por su visita")
    centro("Comprobante interno del local")
    return "\n".join(l)
