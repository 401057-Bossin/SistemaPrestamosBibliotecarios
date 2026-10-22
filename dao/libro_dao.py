import sqlite3
from typing import List, Optional
from models.entidades import Libro
from dao.database import DB_PATH_DEFAULT


class LibroDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, libro: Libro) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO libros (isbn, titulo, autor, categoria, editorial)
                VALUES (?, ?, ?, ?, ?)
            """, (
                libro.isbn,
                libro.titulo,
                libro.autor,
                libro.categoria,
                libro.editorial
            ))

    def obtener_por_isbn(self, isbn: str) -> Optional[Libro]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM libros WHERE isbn = ?", (isbn,))
            row = cur.fetchone()
            if not row:
                return None
            return Libro(
                isbn=row["isbn"],
                titulo=row["titulo"],
                autor=row["autor"],
                categoria=row["categoria"],
                editorial=row["editorial"]
            )

    def listar(self) -> List[Libro]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM libros ORDER BY titulo")
            filas = cur.fetchall()
            return [
                Libro(
                    isbn=row["isbn"],
                    titulo=row["titulo"],
                    autor=row["autor"],
                    categoria=row["categoria"],
                    editorial=row["editorial"]
                )
                for row in filas
            ]

    def eliminar(self, isbn: str) -> int:
        with self._conn() as cx:
            cur = cx.execute("DELETE FROM libros WHERE isbn = ?", (isbn,))
            return cur.rowcount
