import sqlite3
from typing import List, Optional, Dict
from models.entidades import Ejemplar, Libro, Sede
from models.enum import EstadoEjemplar, Estado
from dao.database import DB_PATH_DEFAULT


class EjemplarDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, ejemplar: Ejemplar) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO ejemplares (id_ejemplar, isbn, id_sede, estado_ejemplar, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ejemplar.id_ejemplar,
                ejemplar.libro.isbn,
                ejemplar.sede.id_sede,
                ejemplar.estado_ejemplar.name,
                ejemplar.estado.name
            ))

    def _fila_a_ejemplar(
        self,
        row: sqlite3.Row,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Ejemplar:
        libro = libros_dict.get(row["isbn"]) if libros_dict else None
        sede = sedes_dict.get(row["id_sede"]) if sedes_dict else None
        
        ej = Ejemplar(
            id_ejemplar=row["id_ejemplar"],
            libro=libro,
            sede=sede
        )
        ej.estado_ejemplar = EstadoEjemplar[row["estado_ejemplar"]]
        ej.estado = Estado[row["estado"]]
        return ej

    def obtener_por_id(
        self,
        id_ejemplar: str,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Optional[Ejemplar]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM ejemplares WHERE id_ejemplar = ?", (id_ejemplar,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_ejemplar(row, libros_dict, sedes_dict)

    def listar(
        self,
        libros_dict: Optional[Dict[str, Libro]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> List[Ejemplar]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM ejemplares ORDER BY id_ejemplar")
            filas = cur.fetchall()
            return [self._fila_a_ejemplar(row, libros_dict, sedes_dict) for row in filas]

    def actualizar(self, ejemplar: Ejemplar) -> int:
        with self._conn() as cx:
            cur = cx.execute("""
                UPDATE ejemplares
                SET id_sede = ?, estado_ejemplar = ?, estado = ?
                WHERE id_ejemplar = ?
            """, (
                ejemplar.sede.id_sede,
                ejemplar.estado_ejemplar.name,
                ejemplar.estado.name,
                ejemplar.id_ejemplar
            ))
            return cur.rowcount

    def eliminar(self, id_ejemplar: str) -> int:
        with self._conn() as cx:
            cur = cx.execute("DELETE FROM ejemplares WHERE id_ejemplar = ?", (id_ejemplar,))
            return cur.rowcount
