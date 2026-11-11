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
            "SELECT id, nombre, categoria, precio, activo, imagen FROM Plato "
            "WHERE activo = 1 ORDER BY categoria, nombre")
        return [Plato(f.id, f.nombre, f.categoria, f.precio, f.activo, f.imagen) for f in filas]

    # ---------- Pedido ----------
    def pedido_activo_de_mesa(self, id_mesa):
        """Pedido no finalizado de la mesa (o None)."""
        filas = self.db.consultar(
            "SELECT TOP 1 p.id, p.id_mesa, m.numero, p.fecha_inicio, p.estado, p.total, "
            "p.observaciones, p.metodo_pago, u.nombres, u.apellidos "
            "FROM Pedido p JOIN Mesa m ON m.id = p.id_mesa "
            "LEFT JOIN Usuario u ON u.id = p.id_usuario "
            "WHERE p.id_mesa = ? AND p.estado <> 'FINALIZADO' ORDER BY p.id DESC", (id_mesa,))
        if not filas:
            return None
        f = filas[0]
        mozo = f"{f.nombres} {f.apellidos}" if f.nombres else None
        pedido = Pedido(f.id, f.id_mesa, f.fecha_inicio, f.estado, f.total,
                        observaciones=f.observaciones, metodo_pago=f.metodo_pago,
                        mozo=mozo, numero_mesa=f.numero)
        pedido.detalles = self.listar_detalles(pedido.id)
        return pedido

    def confirmar_orden(self, id_mesa, items, observaciones="", id_usuario=None):
        """Guarda una ronda de platos (items = [(plato, cantidad), ...]) y la envía a cocina."""
        items = [(p, c) for p, c in items if c > 0]
        if not items:
            raise ValueError("La orden no tiene platos.")
        id_pedido = self.abrir_pedido(id_mesa, id_usuario)
        for plato, cantidad in items:
            self.agregar_detalle(id_pedido, plato, cantidad)
        if observaciones and observaciones.strip():
            self.agregar_observacion(id_pedido, observaciones)
        return id_pedido

    def agregar_observacion(self, id_pedido, texto):
        texto = texto.strip()[:150]
        actual = self.db.consultar("SELECT observaciones FROM Pedido WHERE id = ?",
                                   (id_pedido,))[0].observaciones
        nuevo = f"{actual} | {texto}" if actual else texto
        self.db.ejecutar("UPDATE Pedido SET observaciones = ? WHERE id = ?", (nuevo[:400], id_pedido))

    def abrir_pedido(self, id_mesa, id_usuario=None):
        """Devuelve el pedido abierto de la mesa; si no hay, crea uno.
        Nunca deja dos pedidos abiertos para la misma mesa."""
        existente = self.pedido_activo_de_mesa(id_mesa)
        if existente:
            return existente.id
        try:
            id_pedido = self.db.insertar(
                "INSERT INTO Pedido (id_mesa, id_usuario) VALUES (?, ?)", (id_mesa, id_usuario))
        except Exception:
            # Otro equipo lo abrió justo antes (lo impide el índice único)
            existente = self.pedido_activo_de_mesa(id_mesa)
            if existente:
                return existente.id
            raise
        self.mesas.cambiar_estado(id_mesa, Mesa.EN_CURSO)
        return id_pedido

    def agregar_detalle(self, id_pedido, plato, cantidad=1, nota=None):
        """Si el plato ya está pendiente en cocina, suma la cantidad;
        si ya fue preparado (o tiene otra nota), crea una línea nueva."""
        filtro_nota = "nota IS NULL" if nota is None else "nota = ?"
        params = (id_pedido, plato.id) if nota is None else (id_pedido, plato.id, nota)
        filas = self.db.consultar(
            "SELECT id FROM DetallePedido WHERE id_pedido = ? AND id_plato = ? "
            f"AND estado = 'PENDIENTE' AND {filtro_nota}", params)
        if filas:
            self.db.ejecutar("UPDATE DetallePedido SET cantidad = cantidad + ? WHERE id = ?",
                             (cantidad, filas[0].id))
        else:
            self.db.ejecutar(
                "INSERT INTO DetallePedido (id_pedido, id_plato, cantidad, precio_unitario, nota) "
                "VALUES (?, ?, ?, ?, ?)", (id_pedido, plato.id, cantidad, plato.precio, nota))
        self._actualizar(id_pedido)

    def disminuir_detalle(self, id_detalle):
        """Resta 1 a la línea; si llega a 0, la elimina."""
        f = self._detalle(id_detalle)
        if f is None:
            return
        if f.cantidad > 1:
            self.db.ejecutar("UPDATE DetallePedido SET cantidad = cantidad - 1 WHERE id = ?",
                             (id_detalle,))
            self._actualizar(f.id_pedido)
        else:
            self.quitar_detalle(id_detalle)

    def quitar_detalle(self, id_detalle):
        """Elimina la línea. Si el pedido queda vacío, se anula y la mesa se libera."""
        f = self._detalle(id_detalle)
        if f is None:
            return
        self.db.ejecutar("DELETE FROM DetallePedido WHERE id = ?", (id_detalle,))
        quedan = self.db.consultar(
            "SELECT COUNT(*) AS n FROM DetallePedido WHERE id_pedido = ?", (f.id_pedido,))[0].n
        if quedan == 0:
            self._anular_pedido_vacio(f.id_pedido)
        else:
            self._actualizar(f.id_pedido)

    def listar_detalles(self, id_pedido, solo_pendientes=False):
        extra = " AND d.estado = 'PENDIENTE'" if solo_pendientes else ""
        filas = self.db.consultar(
            "SELECT d.id, d.id_plato, p.nombre, d.cantidad, d.precio_unitario, d.nota, d.estado "
            "FROM DetallePedido d JOIN Plato p ON p.id = d.id_plato "
            "WHERE d.id_pedido = ?" + extra + " ORDER BY d.id", (id_pedido,))
        return [DetallePedido(f.id, f.id_plato, f.nombre, f.cantidad, f.precio_unitario,
                              f.nota, f.estado) for f in filas]

    # ---------- Internos ----------
    def _detalle(self, id_detalle):
        filas = self.db.consultar(
            "SELECT id, id_pedido, cantidad FROM DetallePedido WHERE id = ?", (id_detalle,))
        return filas[0] if filas else None

    def _actualizar(self, id_pedido):
        """Recalcula el total y el estado del pedido (PENDIENTE si algo falta en cocina)."""
        self.db.ejecutar(
            "UPDATE Pedido SET total = (SELECT ISNULL(SUM(cantidad*precio_unitario),0) "
            "FROM DetallePedido WHERE id_pedido = ?) WHERE id = ?", (id_pedido, id_pedido))
        self.db.ejecutar(
            "UPDATE Pedido SET estado = CASE WHEN EXISTS (SELECT 1 FROM DetallePedido "
            "WHERE id_pedido = ? AND estado = 'PENDIENTE') THEN 'PENDIENTE' ELSE 'LISTO' END "
            "WHERE id = ? AND estado <> 'FINALIZADO'", (id_pedido, id_pedido))

    def _anular_pedido_vacio(self, id_pedido):
        f = self.db.consultar("SELECT id_mesa FROM Pedido WHERE id = ?", (id_pedido,))[0]
        self.db.ejecutar("DELETE FROM Pedido WHERE id = ?", (id_pedido,))
        self.mesas.cambiar_estado(f.id_mesa, Mesa.LIBRE)

    # ---------- Cocina ----------
    def pendientes_cocina(self):
        return self.db.consultar(
            "SELECT p.id, m.numero AS mesa, p.fecha_inicio, p.observaciones FROM Pedido p "
            "JOIN Mesa m ON m.id = p.id_mesa WHERE p.estado = 'PENDIENTE' ORDER BY p.fecha_inicio")

    def tiene_platos_listos(self, id_pedido):
        return self.db.consultar(
            "SELECT COUNT(*) AS n FROM DetallePedido WHERE id_pedido = ? AND estado = 'LISTO'",
            (id_pedido,))[0].n > 0

    def marcar_listo(self, id_pedido, ids_detalle=None):
        """Marca como preparados los platos indicados (los que cocina tenía en pantalla).
        Si no se indican, marca todos los pendientes."""
        if ids_detalle:
            marcas = ",".join("?" * len(ids_detalle))
            self.db.ejecutar(
                f"UPDATE DetallePedido SET estado = 'LISTO' WHERE id_pedido = ? AND id IN ({marcas})",
                (id_pedido, *ids_detalle))
        else:
            self.db.ejecutar(
                "UPDATE DetallePedido SET estado = 'LISTO' WHERE id_pedido = ?", (id_pedido,))
        self._actualizar(id_pedido)

    # ---------- Cierre ----------
    def finalizar(self, pedido, metodo_pago):
        if metodo_pago not in Pedido.METODOS_PAGO:
            raise ValueError("Elija un método de pago.")
        self.db.ejecutar(
            "UPDATE Pedido SET estado='FINALIZADO', fecha_fin=GETDATE(), metodo_pago=? WHERE id=?",
            (metodo_pago, pedido.id))
        pedido.estado, pedido.metodo_pago = Pedido.FINALIZADO, metodo_pago
        self.mesas.cambiar_estado(pedido.id_mesa, Mesa.LIBRE)
