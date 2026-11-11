from datetime import datetime


class ReporteService:
    PERIODOS = ("DIARIO", "MENSUAL", "TRIMESTRAL")

    def __init__(self, conexion):
        self.db = conexion

    @staticmethod
    def inicio_periodo(periodo, ahora=None):
        ahora = ahora or datetime.now()
        hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        if periodo == "DIARIO":
            return hoy
        if periodo == "MENSUAL":
            return hoy.replace(day=1)
        if periodo == "TRIMESTRAL":
            return hoy.replace(month=(hoy.month - 1) // 3 * 3 + 1, day=1)
        raise ValueError(f"Periodo no válido: {periodo}")

    def ventas(self, periodo="DIARIO", metodo=None):
        """Lista de ventas finalizadas del periodo, cada una con su detalle en texto."""
        desde = self.inicio_periodo(periodo)
        filtro, params = "p.estado = 'FINALIZADO' AND p.fecha_fin >= ?", [desde]
        if metodo:
            filtro += " AND p.metodo_pago = ?"
            params.append(metodo)
        pedidos = self.db.consultar(
            "SELECT p.id, p.fecha_fin, m.numero AS mesa, p.metodo_pago, p.total "
            "FROM Pedido p JOIN Mesa m ON m.id = p.id_mesa "
            f"WHERE {filtro} ORDER BY p.fecha_fin DESC", tuple(params))
        lineas = self.db.consultar(
            "SELECT d.id_pedido, pl.nombre, SUM(d.cantidad) AS cantidad "
            "FROM DetallePedido d JOIN Plato pl ON pl.id = d.id_plato "
            "JOIN Pedido p ON p.id = d.id_pedido "
            f"WHERE {filtro} GROUP BY d.id_pedido, pl.nombre", tuple(params))
        detalle = {}
        for l in lineas:
            detalle.setdefault(l.id_pedido, []).append(f"{l.cantidad} {l.nombre}")
        return [{"id": p.id, "fecha": p.fecha_fin, "mesa": p.mesa, "metodo": p.metodo_pago,
                 "total": float(p.total), "detalle": ", ".join(detalle.get(p.id, []))}
                for p in pedidos]

    def ventas_del_dia(self):
        v = self.ventas("DIARIO")
        return {"pedidos": len(v), "total": sum(x["total"] for x in v)}

    def platos_mas_vendidos(self, top=5):
        return self.db.consultar(
            f"SELECT TOP {int(top)} p.nombre, SUM(d.cantidad) AS vendidos "
            "FROM DetallePedido d JOIN Plato p ON p.id = d.id_plato "
            "JOIN Pedido pe ON pe.id = d.id_pedido WHERE pe.estado='FINALIZADO' "
            "GROUP BY p.nombre ORDER BY vendidos DESC")
