import sqlite3
from typing import List, Optional, Dict
from datetime import date
from models.operaciones import Prestamo
from models.entidades import Socio, Ejemplar, Sede
from models.enum import Estado
from dao.database import DB_PATH_DEFAULT


class PrestamoDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, prestamo: Prestamo) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO prestamos (
                    id_prestamo, id_socio, id_ejemplar, id_sede_origen, id_sede_destino,
                    fecha_inicio, fecha_vencimiento, fecha_devolucion, estado_devuelto
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prestamo.id_prestamo,
                prestamo.socio.id_socio,
                prestamo.ejemplar.id_ejemplar,
                prestamo.sede_origen.id_sede,
                prestamo.sede_destino.id_sede,
                prestamo.fecha_inicio.isoformat(),
                prestamo.fecha_vencimiento.isoformat(),
                prestamo.fecha_devolucion.isoformat() if prestamo.fecha_devolucion else None,
                prestamo.estado_devuelto.name if prestamo.estado_devuelto else None
            ))

    def _fila_a_prestamo(
        self,
        row: sqlite3.Row,
        socios_dict: Optional[Dict[str, Socio]] = None,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Prestamo:
        socio = socios_dict.get(row["id_socio"]) if socios_dict else None
        ejemplar = ejemplares_dict.get(row["id_ejemplar"]) if ejemplares_dict else None
        sede_origen = sedes_dict.get(row["id_sede_origen"]) if sedes_dict else None
        sede_destino = sedes_dict.get(row["id_sede_destino"]) if sedes_dict else None

        prestamo = Prestamo.__new__(Prestamo)
        prestamo.id_prestamo = row["id_prestamo"]
        prestamo.socio = socio
        prestamo.ejemplar = ejemplar
        prestamo.sede_origen = sede_origen
        prestamo.sede_destino = sede_destino
        prestamo.fecha_inicio = date.fromisoformat(row["fecha_inicio"])
        prestamo.fecha_vencimiento = date.fromisoformat(row["fecha_vencimiento"])
        prestamo.fecha_devolucion = date.fromisoformat(row["fecha_devolucion"]) if row["fecha_devolucion"] else None
        prestamo.estado_devuelto = Estado[row["estado_devuelto"]] if row["estado_devuelto"] else None
        return prestamo

    def obtener_por_id(
        self,
        id_prestamo: str,
        socios_dict: Optional[Dict[str, Socio]] = None,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Optional[Prestamo]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM prestamos WHERE id_prestamo = ?", (id_prestamo,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_prestamo(row, socios_dict, ejemplares_dict, sedes_dict)

    def listar(
        self,
        socios_dict: Optional[Dict[str, Socio]] = None,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> List[Prestamo]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM prestamos ORDER BY fecha_inicio")
            filas = cur.fetchall()
            return [self._fila_a_prestamo(r, socios_dict, ejemplares_dict, sedes_dict) for r in filas]

    def actualizar_devolucion(self, id_prestamo: str, fecha_devolucion: date, estado_devuelto: Estado) -> int:
        with self._conn() as cx:
            cur = cx.execute("""
                UPDATE prestamos
                SET fecha_devolucion = ?, estado_devuelto = ?
                WHERE id_prestamo = ?
            """, (
                fecha_devolucion.isoformat(),
                estado_devuelto.name,
                id_prestamo
            ))
            return cur.rowcount
