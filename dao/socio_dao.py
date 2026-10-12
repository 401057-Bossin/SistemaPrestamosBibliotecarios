import sqlite3
from typing import List, Optional
from datetime import date
from models.entidades import Socio
from dao.database import DB_PATH_DEFAULT


class SocioDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, socio: Socio) -> None:
        penalizado_str = socio.penalizado_hasta.isoformat() if socio.penalizado_hasta else None
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO socios (id_socio, nombre, apellido, dni, email, penalizado_hasta)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                socio.id_socio,
                socio.nombre,
                socio.apellido,
                socio.dni,
                socio.email,
                penalizado_str
            ))

    def _fila_a_socio(self, row: sqlite3.Row) -> Socio:
        socio = Socio(
            id_socio=row["id_socio"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            dni=row["dni"],
            email=row["email"]
        )
        if row["penalizado_hasta"]:
            socio.penalizado_hasta = date.fromisoformat(row["penalizado_hasta"])
        return socio

    def obtener_por_id(self, id_socio: str) -> Optional[Socio]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM socios WHERE id_socio = ?", (id_socio,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_socio(row)

    def obtener_por_dni(self, dni: str) -> Optional[Socio]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM socios WHERE dni = ?", (dni,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_socio(row)

    def listar(self) -> List[Socio]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM socios ORDER BY apellido, nombre")
            filas = cur.fetchall()
            return [self._fila_a_socio(row) for row in filas]

    def actualizar_penalizacion(self, id_socio: str, penalizado_hasta: Optional[date]) -> int:
        penalizado_str = penalizado_hasta.isoformat() if penalizado_hasta else None
        with self._conn() as cx:
            cur = cx.execute(
                "UPDATE socios SET penalizado_hasta = ? WHERE id_socio = ?",
                (penalizado_str, id_socio)
            )
            return cur.rowcount

    def eliminar(self, id_socio: str) -> int:
        with self._conn() as cx:
            cur = cx.execute("DELETE FROM socios WHERE id_socio = ?", (id_socio,))
            return cur.rowcount
