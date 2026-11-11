from models.plato import Plato
from models.pedido import Pedido
from models.detalle_pedido import DetallePedido
from models.mesa import Mesa


class PedidoService:
    def __init__(self, conexion, mesa_service):
        self.db = conexion
        self.mesas = mesa_service

    # ---------- Menú ----------
    def listar_platos(self):
        filas = self.db.consultar(
            "SELECT id, nombre, categoria, precio, activo FROM Plato "
            "WHERE activo = 1 ORDER BY categoria, nombre")
        return [Plato(f.id, f.nombre, f.categoria, f.precio, f.activo) for f in filas]

    # ---------- Pedido ----------
    def pedido_activo_de_mesa(self, id_mesa):
        """Pedido no finalizado de la mesa (o None)."""
        filas = self.db.consultar(
            "SELECT TOP 1 id, id_mesa, fecha_inicio, estado, total FROM Pedido "
            "WHERE id_mesa = ? AND estado <> 'FINALIZADO' ORDER BY id DESC", (id_mesa,))
        if not filas:
            return None
        f = filas[0]
        pedido = Pedido(f.id, f.id_mesa, f.fecha_inicio, f.estado, f.total)
        pedido.detalles = self.listar_detalles(pedido.id)
        return pedido

    def abrir_pedido(self, id_mesa):
        id_pedido = self.db.insertar("INSERT INTO Pedido (id_mesa) VALUES (?)", (id_mesa,))
        self.mesas.cambiar_estado(id_mesa, Mesa.EN_CURSO)
        return id_pedido

    def agregar_detalle(self, id_pedido, plato, cantidad=1, nota=None):
        self.db.ejecutar(
            "INSERT INTO DetallePedido (id_pedido, id_plato, cantidad, precio_unitario, nota) "
            "VALUES (?, ?, ?, ?, ?)", (id_pedido, plato.id, cantidad, plato.precio, nota))
        self._recalcular_total(id_pedido)
        # Si ya estaba LISTO y se agrega algo, vuelve a pendiente para cocina
        self.db.ejecutar("UPDATE Pedido SET estado='PENDIENTE' WHERE id=? AND estado='LISTO'", (id_pedido,))

    def listar_detalles(self, id_pedido):
        filas = self.db.consultar(
            "SELECT d.id, d.id_plato, p.nombre, d.cantidad, d.precio_unitario, d.nota "
            "FROM DetallePedido d JOIN Plato p ON p.id = d.id_plato WHERE d.id_pedido = ?",
            (id_pedido,))
        return [DetallePedido(f.id, f.id_plato, f.nombre, f.cantidad, f.precio_unitario, f.nota)
                for f in filas]

    def _recalcular_total(self, id_pedido):
        self.db.ejecutar(
            "UPDATE Pedido SET total = (SELECT ISNULL(SUM(cantidad*precio_unitario),0) "
            "FROM DetallePedido WHERE id_pedido = ?) WHERE id = ?", (id_pedido, id_pedido))

    # ---------- Cocina ----------
    def pendientes_cocina(self):
        return self.db.consultar(
            "SELECT p.id, m.numero AS mesa, p.fecha_inicio FROM Pedido p "
            "JOIN Mesa m ON m.id = p.id_mesa WHERE p.estado = 'PENDIENTE' ORDER BY p.fecha_inicio")

    def marcar_listo(self, id_pedido):
        self.db.ejecutar("UPDATE Pedido SET estado='LISTO' WHERE id=?", (id_pedido,))

    # ---------- Cierre ----------
    def finalizar(self, pedido):
        self.db.ejecutar(
            "UPDATE Pedido SET estado='FINALIZADO', fecha_fin=GETDATE() WHERE id=?", (pedido.id,))
        self.mesas.cambiar_estado(pedido.id_mesa, Mesa.LIBRE)
