import sqlite3
from typing import List, Optional, Dict
from datetime import datetime
from models.remito import Remito, Creado, Empaquetado, Despachado, Recibido
from models.entidades import Ejemplar, Sede
from dao.database import DB_PATH_DEFAULT

ESTADOS_CLASES = {
    "Creado": Creado,
    "Empaquetado": Empaquetado,
    "Despachado": Despachado,
    "Recibido": Recibido
}


class RemitoDAO:
    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def crear(self, remito: Remito) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO remitos (id_remito, id_ejemplar, id_sede_origen, id_sede_destino, estado_actual)
                VALUES (?, ?, ?, ?, ?)
            """, (
                remito.id_remito,
                remito.ejemplar.id_ejemplar,
                remito.sede_origen.id_sede,
                remito.sede_destino.id_sede,
                str(remito.estado_actual)
            ))

            for reg in remito.trazabilidad:
                cx.execute("""
                    INSERT INTO remito_trazabilidad (id_remito, estado, fecha_hora, observacion)
                    VALUES (?, ?, ?, ?)
                """, (
                    remito.id_remito,
                    reg["estado"],
                    reg["fecha_hora"].isoformat(),
                    reg["observacion"]
                ))

    def agregar_trazabilidad(self, id_remito: str, estado: str, fecha_hora: datetime, observacion: str) -> None:
        with self._conn() as cx:
            cx.execute("""
                INSERT INTO remito_trazabilidad (id_remito, estado, fecha_hora, observacion)
                VALUES (?, ?, ?, ?)
            """, (
                id_remito,
                estado,
                fecha_hora.isoformat(),
                observacion
            ))
            cx.execute("""
                UPDATE remitos SET estado_actual = ? WHERE id_remito = ?
            """, (estado, id_remito))

    def obtener_trazabilidad(self, id_remito: str) -> List[dict]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute(
                "SELECT * FROM remito_trazabilidad WHERE id_remito = ? ORDER BY id ASC",
                (id_remito,)
            )
            filas = cur.fetchall()
            return [
                {
                    "estado": r["estado"],
                    "fecha_hora": datetime.fromisoformat(r["fecha_hora"]),
                    "observacion": r["observacion"]
                }
                for r in filas
            ]

    def _fila_a_remito(
        self,
        row: sqlite3.Row,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Remito:
        ejemplar = ejemplares_dict.get(row["id_ejemplar"]) if ejemplares_dict else None
        sede_origen = sedes_dict.get(row["id_sede_origen"]) if sedes_dict else None
        sede_destino = sedes_dict.get(row["id_sede_destino"]) if sedes_dict else None

        remito = Remito.__new__(Remito)
        remito._id_remito = row["id_remito"]
        remito.ejemplar = ejemplar
        remito.sede_origen = sede_origen
        remito.sede_destino = sede_destino

        estado_nombre = row["estado_actual"]
        clase_estado = ESTADOS_CLASES.get(estado_nombre, Creado)
        remito.estado_actual = clase_estado()
        remito.trazabilidad = self.obtener_trazabilidad(row["id_remito"])
        return remito

    def obtener_por_id(
        self,
        id_remito: str,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> Optional[Remito]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM remitos WHERE id_remito = ?", (id_remito,))
            row = cur.fetchone()
            if not row:
                return None
            return self._fila_a_remito(row, ejemplares_dict, sedes_dict)

    def listar(
        self,
        ejemplares_dict: Optional[Dict[str, Ejemplar]] = None,
        sedes_dict: Optional[Dict[str, Sede]] = None
    ) -> List[Remito]:
        with self._conn() as cx:
            cx.row_factory = sqlite3.Row
            cur = cx.execute("SELECT * FROM remitos ORDER BY id_remito")
            filas = cur.fetchall()
            return [self._fila_a_remito(r, ejemplares_dict, sedes_dict) for r in filas]
