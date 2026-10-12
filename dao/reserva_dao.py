import sqlite3
from typing import List, Optional, Dict
from datetime import date
from models.operaciones import Reserva
from models.entidades import Socio, Libro, Sede
from dao.database import DB_PATH_DEFAULT


class ReservaDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, reserva: Reserva) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO reservas (id_reserva, id_socio, isbn, id_sede, fecha_solicitud, activa)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reserva.id_reserva,
                reserva.socio.id_socio,
                reserva.libro.isbn,
                reserva.sede.id_sede,
                reserva.fecha_solicitud.isoformat(),
                1 if reserva.activa else 0
            ))

    def _fila_a_reserva(
        self,
        row: sqlite3.Row,
        socios_dict: Optional[Dict[str, Socio]] = None,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Reserva:
        socio = socios_dict.get(row["id_socio"]) if socios_dict else None
        libro = libros_dict.get(row["isbn"]) if libros_dict else None
        sede = sedes_dict.get(row["id_sede"]) if sedes_dict else None

        reserva = Reserva.__new__(Reserva)
        reserva.id_reserva = row["id_reserva"]
        reserva.socio = socio
        reserva.libro = libro
        reserva.sede = sede
        reserva.fecha_solicitud = date.fromisoformat(row["fecha_solicitud"])
        reserva.activa = bool(row["activa"])
        return reserva

    def obtener_por_id(
        self,
        id_reserva: str,
        socios_dict: Optional[Dict[str, Socio]] = None,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Optional[Reserva]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM reservas WHERE id_reserva = ?", (id_reserva,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_reserva(row, socios_dict, libros_dict, sedes_dict)

    def listar(
        self,
        socios_dict: Optional[Dict[str, Socio]] = None,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> List[Reserva]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM reservas ORDER BY fecha_solicitud")
            filas = cur.fetchall()
            return [self._fila_a_reserva(r, socios_dict, libros_dict, sedes_dict) for r in filas]

    def actualizar_activa(self, id_reserva: str, activa: bool) -> int:
        with self._conn() as cx:
            cur = cx.execute(
                "UPDATE reservas SET activa = ? WHERE id_reserva = ?",
                (1 if activa else 0, id_reserva)
            )
            return cur.rowcount
