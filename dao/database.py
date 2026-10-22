import os
import sqlite3

DB_PATH_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "biblioteca.db")


def inicializar_bd(db_path: str = DB_PATH_DEFAULT):
    """Crea las tablas de la base de datos SQLite si no existen."""
    with sqlite3.connect(db_path) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON;")
        cursor = conexion.cursor()

        # Tabla Sedes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sedes (
                id_sede TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                direccion TEXT,
                contacto TEXT,
                horarios TEXT,
                activa INTEGER NOT NULL DEFAULT 1
            );
        """)

        # Tabla Socios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS socios (
                id_socio TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT NOT NULL UNIQUE,
                email TEXT,
                penalizado_hasta TEXT
            );
        """)

        # Tabla Libros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                isbn TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                categoria TEXT,
                editorial TEXT
            );
        """)

        # Tabla Ejemplares
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ejemplares (
                id_ejemplar TEXT PRIMARY KEY,
                isbn TEXT NOT NULL,
                id_sede TEXT NOT NULL,
                estado_ejemplar TEXT NOT NULL,
                estado TEXT NOT NULL,
                FOREIGN KEY (isbn) REFERENCES libros (isbn),
                FOREIGN KEY (id_sede) REFERENCES sedes (id_sede)
            );
        """)

        # Tabla Prestamos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prestamos (
                id_prestamo TEXT PRIMARY KEY,
                id_socio TEXT NOT NULL,
                id_ejemplar TEXT NOT NULL,
                id_sede_origen TEXT NOT NULL,
                id_sede_destino TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                fecha_devolucion TEXT,
                estado_devuelto TEXT,
                FOREIGN KEY (id_socio) REFERENCES socios (id_socio),
                FOREIGN KEY (id_ejemplar) REFERENCES ejemplares (id_ejemplar),
                FOREIGN KEY (id_sede_origen) REFERENCES sedes (id_sede),
                FOREIGN KEY (id_sede_destino) REFERENCES sedes (id_sede)
            );
        """)

        # Tabla Reservas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id_reserva TEXT PRIMARY KEY,
                id_socio TEXT NOT NULL,
                isbn TEXT NOT NULL,
                id_sede TEXT NOT NULL,
                fecha_solicitud TEXT NOT NULL,
                activa INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_socio) REFERENCES socios (id_socio),
                FOREIGN KEY (isbn) REFERENCES libros (isbn),
                FOREIGN KEY (id_sede) REFERENCES sedes (id_sede)
            );
        """)

        # Tabla Remitos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remitos (
                id_remito TEXT PRIMARY KEY,
                id_ejemplar TEXT NOT NULL,
                id_sede_origen TEXT NOT NULL,
                id_sede_destino TEXT NOT NULL,
                estado_actual TEXT NOT NULL,
                FOREIGN KEY (id_ejemplar) REFERENCES ejemplares (id_ejemplar),
                FOREIGN KEY (id_sede_origen) REFERENCES sedes (id_sede),
                FOREIGN KEY (id_sede_destino) REFERENCES sedes (id_sede)
            );
        """)

        # Tabla Trazabilidad de Remitos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remito_trazabilidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_remito TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                observacion TEXT NOT NULL,
                FOREIGN KEY (id_remito) REFERENCES remitos (id_remito)
            );
        """)

        conexion.commit()


def vaciar_bd(db_path: str = DB_PATH_DEFAULT):
    """Elimina todos los datos de las tablas (utilizado principalmente para tests)."""
    with sqlite3.connect(db_path) as conexion:
        conexion.execute("PRAGMA foreign_keys = OFF;")
        cursor = conexion.cursor()
        tablas = [
            "remito_trazabilidad",
            "remitos",
            "reservas",
            "prestamos",
            "ejemplares",
            "libros",
            "socios",
            "sedes"
        ]
        for t in tablas:
            cursor.execute(f"DELETE FROM {t};")
        conexion.commit()
        conexion.execute("PRAGMA foreign_keys = ON;")
