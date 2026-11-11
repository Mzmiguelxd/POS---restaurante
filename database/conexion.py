"""Capa de acceso a SQL Server mediante pyodbc."""
import pyodbc
from config import DB_CONFIG


class Conexion:
    """Encapsula la conexión y ofrece métodos simples para consultar y ejecutar."""

    def __init__(self, config=None):
        self._cfg = config or DB_CONFIG
        self._conn = None

    def _cadena(self):
        c = self._cfg
        base = (
            f"DRIVER={{{c['driver']}}};SERVER={c['server']};"
            f"DATABASE={c['database']};TrustServerCertificate=yes;"
        )
        if c.get("trusted_connection"):
            return base + "Trusted_Connection=yes;"
        return base + f"UID={c['user']};PWD={c['password']};"

    def abrir(self):
        if self._conn is None:
            self._conn = pyodbc.connect(self._cadena())
        return self._conn

    def cerrar(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def consultar(self, sql, params=()):
        """Devuelve una lista de filas (SELECT)."""
        cur = self.abrir().cursor()
        cur.execute(sql, params)
        filas = cur.fetchall()
        cur.close()
        return filas

    def ejecutar(self, sql, params=()):
        """Ejecuta INSERT/UPDATE/DELETE y confirma. Devuelve filas afectadas."""
        conn = self.abrir()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            afectadas = cur.rowcount
            conn.commit()
            return afectadas
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    def insertar(self, sql, params=()):
        """INSERT que devuelve el id generado (usar con OUTPUT o SCOPE_IDENTITY)."""
        conn = self.abrir()
        cur = conn.cursor()
        try:
            cur.execute(sql + "; SELECT CAST(SCOPE_IDENTITY() AS INT);", params)
            cur.nextset()
            nuevo_id = cur.fetchone()[0]
            conn.commit()
            return nuevo_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
