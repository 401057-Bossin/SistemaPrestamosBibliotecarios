import sqlite3
from typing import List, Optional
from models.entidades import Sede
from dao.database import DB_PATH_DEFAULT


class SedeDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, sede: Sede) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO sedes (id_sede, nombre, direccion, contacto, horarios, activa)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sede.id_sede,
                sede.nombre,
                sede.direccion,
                sede.contacto,
                sede.horarios,
                1 if sede.activa else 0
            ))

    def obtener_por_id(self, id_sede: str) -> Optional[Sede]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM sedes WHERE id_sede = ?", (id_sede,))
            row = cur.fetchone()
            if not row:
                return None
            return Sede(
                id_sede=row["id_sede"],
                nombre=row["nombre"],
                direccion=row["direccion"],
                contacto=row["contacto"],
                horarios=row["horarios"],
                activa=bool(row["activa"])
            )

    def listar(self) -> List[Sede]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM sedes ORDER BY id_sede")
            filas = cur.fetchall()
            return [
                Sede(
                    id_sede=row["id_sede"],
                    nombre=row["nombre"],
                    direccion=row["direccion"],
                    contacto=row["contacto"],
                    horarios=row["horarios"],
                    activa=bool(row["activa"])
                )
                for row in filas
            ]

    def actualizar_estado(self, id_sede: str, activa: bool) -> int:
        with self._conn() as cx:
            cur = cx.execute(
                "UPDATE sedes SET activa = ? WHERE id_sede = ?",
                (1 if activa else 0, id_sede)
            )
            return cur.rowcount

    def eliminar(self, id_sede: str) -> int:
        with self._conn() as cx:
            cur = cx.execute("DELETE FROM sedes WHERE id_sede = ?", (id_sede,))
            return cur.rowcount
