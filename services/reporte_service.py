class ReporteService:
    def __init__(self, conexion):
        self.db = conexion

    def ventas_del_dia(self):
        f = self.db.consultar(
            "SELECT COUNT(*) AS pedidos, ISNULL(SUM(total),0) AS total FROM Pedido "
            "WHERE estado='FINALIZADO' AND CAST(fecha_fin AS DATE) = CAST(GETDATE() AS DATE)")[0]
        return {"pedidos": f.pedidos, "total": float(f.total)}

    def platos_mas_vendidos(self, top=5):
        return self.db.consultar(
            f"SELECT TOP {int(top)} p.nombre, SUM(d.cantidad) AS vendidos "
            "FROM DetallePedido d JOIN Plato p ON p.id = d.id_plato "
            "JOIN Pedido pe ON pe.id = d.id_pedido WHERE pe.estado='FINALIZADO' "
            "GROUP BY p.nombre ORDER BY vendidos DESC")

    def tiempo_promedio_por_mesa_min(self):
        f = self.db.consultar(
            "SELECT ISNULL(AVG(DATEDIFF(MINUTE, fecha_inicio, fecha_fin)),0) AS minutos "
            "FROM Pedido WHERE estado='FINALIZADO'")[0]
        return float(f.minutos)
