"""Formato de la cuenta de una mesa."""


def resumen_cuenta(mesa, pedido):
    lineas = [f"CUENTA - Mesa {mesa.numero}", "-" * 32]
    for d in pedido.detalles:
        lineas.append(f"{d.cantidad} x {d.nombre_plato:<18} S/ {d.subtotal:>7.2f}")
    lineas += ["-" * 32, f"TOTAL: S/ {pedido.calcular_total():.2f}"]
    return "\n".join(lineas)
