from datetime import date
from models.enum import EstadoEjemplar, Estado
from models.entidades import Sede, Socio, Libro, Ejemplar
from models.operaciones import Prestamo, Reserva
from models.remito import Remito
from models.excepciones import (
    BibliotecaExcepcion,
    EjemplarNoDisponibleError,
    SocioInhabilitadoError,
    SedeDadaDeBajaError,
    TransicionInvalidaError
)


class GestorBiblioteca:
    _instancia = None

    def __new__(cls):
        # Patrón Singleton
        if cls._instancia is None:
            cls._instancia = super(GestorBiblioteca, cls).__new__(cls)
            cls._instancia._inicializar_datos()
        return cls._instancia

    def _inicializar_datos(self):
        self.sedes = {}
        self.socios = {}
        self.libros = {}
        self.ejemplares = {}
        self.prestamos = []
        self.reservas = []
        self.remitos = []

    # --- Generadores automáticos de identificadores únicos ---
    def generar_id_sede(self) -> str:
        max_id = 0
        for sid in self.sedes.keys():
            if sid.startswith("SED-"):
                try:
                    num = int(sid.split("-")[1])
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"SED-{max_id + 1:02d}"

    def generar_id_socio(self) -> str:
        max_id = 0
        for sid in self.socios.keys():
            if sid.startswith("SOC-"):
                try:
                    num = int(sid.split("-")[1])
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"SOC-{max_id + 1:02d}"

    def generar_id_ejemplar(self) -> str:
        max_id = 0
        for eid in self.ejemplares.keys():
            if eid.startswith("EJ-"):
                try:
                    num = int(eid.split("-")[1])
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"EJ-{max_id + 1:02d}"

    def generar_id_prestamo(self) -> str:
        max_id = 100
        for p in self.prestamos:
            if p.id_prestamo and p.id_prestamo.startswith("PREST-"):
                try:
                    num = int(p.id_prestamo.split("-")[1])
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"PREST-{max_id + 1:03d}"

    def generar_id_reserva(self) -> str:
        max_id = 0
        for r in self.reservas:
            if r.id_reserva and r.id_reserva.startswith("RES-"):
                try:
                    num = int(r.id_reserva.split("-")[1])
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"RES-{max_id + 1:02d}"

    def generar_isbn(self) -> str:
        max_id = 0
        for isbn in self.libros.keys():
            if isbn.startswith("978-AUTO-"):
                try:
                    num = int(isbn.replace("978-AUTO-", ""))
                    if num > max_id:
                        max_id = num
                except (ValueError, IndexError):
                    pass
        return f"978-AUTO-{max_id + 1:04d}"

    # --- 1. Administrar Sedes ---
    def agregar_sede(self, sede: Sede) -> Sede:
        if not sede.id_sede:
            sede.id_sede = self.generar_id_sede()
        if sede.id_sede in self.sedes:
            raise BibliotecaExcepcion(f"La sede con ID '{sede.id_sede}' ya existe.")
        self.sedes[sede.id_sede] = sede
        return sede

    def obtener_sede(self, id_sede: str) -> Sede:
        sede = self.sedes.get(id_sede)
        if not sede:
            raise BibliotecaExcepcion(f"Sede '{id_sede}' no encontrada.")
        return sede

    def cambiar_estado_sede(self, id_sede: str, activa: bool):
        sede = self.obtener_sede(id_sede)
        sede.activa = activa

    # --- 2. Administrar Socios ---
    def agregar_socio(self, socio: Socio) -> Socio:
        if not socio.id_socio:
            socio.id_socio = self.generar_id_socio()
        if socio.id_socio in self.socios:
            raise BibliotecaExcepcion(f"El socio con ID '{socio.id_socio}' ya existe.")
        if any(s.dni == socio.dni for s in self.socios.values()):
            raise BibliotecaExcepcion(f"Ya existe un socio con DNI '{socio.dni}'.")
        self.socios[socio.id_socio] = socio
        return socio

    def obtener_socio(self, id_socio: str) -> Socio:
        socio = self.socios.get(id_socio)
        if not socio:
            raise BibliotecaExcepcion(f"Socio '{id_socio}' no encontrado.")
        return socio

    # --- 3. Administrar Catálogo de Libros y Ejemplares ---
    def agregar_libro(self, libro: Libro) -> Libro:
        if not libro.isbn:
            libro.isbn = self.generar_isbn()
        if libro.isbn in self.libros:
            raise BibliotecaExcepcion(f"El libro con ISBN '{libro.isbn}' ya existe en el catálogo.")
        self.libros[libro.isbn] = libro
        return libro

    def agregar_ejemplar(self, ejemplar: Ejemplar) -> Ejemplar:
        if not ejemplar.id_ejemplar:
            ejemplar.id_ejemplar = self.generar_id_ejemplar()
        if ejemplar.id_ejemplar in self.ejemplares:
            raise BibliotecaExcepcion(f"El ejemplar '{ejemplar.id_ejemplar}' ya está registrado.")
        self.ejemplares[ejemplar.id_ejemplar] = ejemplar
        return ejemplar

    def obtener_ejemplar(self, id_ejemplar: str) -> Ejemplar:
        ejemplar = self.ejemplares.get(id_ejemplar)
        if not ejemplar:
            raise BibliotecaExcepcion(f"Ejemplar '{id_ejemplar}' no encontrado.")
        return ejemplar

    # --- 4. Préstamos locales e interbibliotecarios ---
    def crear_prestamo(
        self,
        id_prestamo: str = None,
        id_socio: str = None,
        id_ejemplar: str = None,
        id_sede_origen: str = None,
        id_sede_destino: str = None,
        dias_prestamo: int = 14,
        fecha_inicio: date = None
    ) -> Prestamo:
        if not id_prestamo:
            id_prestamo = self.generar_id_prestamo()

        socio = self.obtener_socio(id_socio)
        ejemplar = self.obtener_ejemplar(id_ejemplar)
        sede_origen = self.obtener_sede(id_sede_origen)
        sede_destino = self.obtener_sede(id_sede_destino) if id_sede_destino else sede_origen

        prestamo = Prestamo(
            id_prestamo=id_prestamo,
            socio=socio,
            ejemplar=ejemplar,
            sede_origen=sede_origen,
            sede_destino=sede_destino,
            dias_prestamo=dias_prestamo,
            fecha_inicio=fecha_inicio
        )
        self.prestamos.append(prestamo)

        # Si es interbibliotecario, se genera un remito para logística (Trazabilidad)
        if prestamo.es_interbibliotecario:
            id_remito = f"REM-{id_prestamo}"
            remito = Remito(id_remito, ejemplar, sede_origen, sede_destino)
            self.remitos.append(remito)

        return prestamo

    def registrar_devolucion(self, id_prestamo: str, fecha_devolucion: date, estado_fisico: Estado):
        prestamo = next((p for p in self.prestamos if p.id_prestamo == id_prestamo), None)
        if not prestamo:
            raise BibliotecaExcepcion(f"Préstamo '{id_prestamo}' no encontrado.")
        prestamo.registrar_devolucion(fecha_devolucion, estado_fisico)

    # --- 5. Trazabilidad de Remitos (Patrón State) ---
    def obtener_remito(self, id_remito: str) -> Remito:
        remito = next((r for r in self.remitos if r.id_remito == id_remito), None)
        if not remito:
            raise BibliotecaExcepcion(f"Remito '{id_remito}' no encontrado.")
        return remito

    def empaquetar_remito(self, id_remito: str):
        remito = self.obtener_remito(id_remito)
        remito.empaquetar()
        remito.ejemplar.estado_ejemplar = EstadoEjemplar.EN_PREPARACION

    def despachar_remito(self, id_remito: str):
        remito = self.obtener_remito(id_remito)
        remito.despachar()
        remito.ejemplar.estado_ejemplar = EstadoEjemplar.EN_TRANSITO

    def recibir_remito(self, id_remito: str):
        remito = self.obtener_remito(id_remito)
        remito.recibir()
        remito.ejemplar.sede = remito.sede_destino
        remito.ejemplar.estado_ejemplar = EstadoEjemplar.PRESTADO

    # --- 6. Consultar Disponibilidad ---
    def consultar_disponibilidad(self, isbn: str, id_sede: str = None):
        disponibles = [
            e for e in self.ejemplares.values() 
            if e.libro.isbn == isbn and e.esta_disponible()
        ]
        if id_sede:
            disponibles = [e for e in disponibles if e.sede.id_sede == id_sede]
        return disponibles

    # --- 7. Gestionar Reservas ---
    def crear_reserva(
        self,
        id_socio: str = None,
        isbn: str = None,
        id_sede: str = None,
        id_reserva: str = None
    ) -> Reserva:
        # Compatibilidad si se llamó positional con id_reserva primero: crear_reserva(id_reserva, id_socio, isbn, id_sede)
        if id_socio and id_socio.startswith("RES-"):
            id_reserva, id_socio, isbn, id_sede = id_socio, isbn, id_sede, id_reserva

        if not id_reserva:
            id_reserva = self.generar_id_reserva()

        socio = self.obtener_socio(id_socio)
        sede = self.obtener_sede(id_sede)
        libro = self.libros.get(isbn)
        if not libro:
            raise BibliotecaExcepcion(f"Libro con ISBN '{isbn}' no encontrado.")
        
        reserva = Reserva(id_reserva, socio, libro, sede)
        self.reservas.append(reserva)
        return reserva

    # =========================================================================
    # LOS 4 REPORTES OBLIGATORIOS NO TRIVIALES
    # =========================================================================

    # Reporte 1: Préstamos activos y material en tránsito
    def reporte_prestamos_activos_y_transito(self):
        prestamos_activos = [p for p in self.prestamos if p.fecha_devolucion is None]
        ejemplares_en_transito = [
            e for e in self.ejemplares.values() 
            if e.estado_ejemplar == EstadoEjemplar.EN_TRANSITO
        ]
        
        return {
            "total_prestamos_activos": len(prestamos_activos),
            "prestamos_activos": prestamos_activos,
            "total_en_transito": len(ejemplares_en_transito),
            "ejemplares_en_transito": ejemplares_en_transito
        }

    # Reporte 2: Préstamos vencidos y días de mora
    def reporte_prestamos_vencidos(self, fecha_referencia: date = None):
        if fecha_referencia is None:
            fecha_referencia = date.today()

        vencidos = []
        for p in self.prestamos:
            if p.esta_vencido(fecha_referencia):
                dias_retraso = (fecha_referencia - p.fecha_vencimiento).days
                vencidos.append({
                    "prestamo": p,
                    "dias_retraso": dias_retraso
                })
        return {
            "total_vencidos": len(vencidos),
            "detalle": vencidos
        }

    # Reporte 3: Disponibilidad de catálogo por sede
    def reporte_disponibilidad_por_sede(self):
        resumen = {}
        for sede in self.sedes.values():
            ejemplares_sede = [e for e in self.ejemplares.values() if e.sede.id_sede == sede.id_sede]
            disponibles = [e for e in ejemplares_sede if e.esta_disponible()]
            
            resumen[sede.nombre] = {
                "id_sede": sede.id_sede,
                "total_ejemplares": len(ejemplares_sede),
                "disponibles": len(disponibles),
                "no_disponibles": len(ejemplares_sede) - len(disponibles),
                "activa": sede.activa
            }
        return resumen

    # Reporte 4: Libros más solicitados para préstamos inter-sedes
    def reporte_libros_mas_solicitados_intersedes(self):
        conteo_por_libro = {}
        for p in self.prestamos:
            if p.es_interbibliotecario:
                titulo = p.ejemplar.libro.titulo
                conteo_por_libro[titulo] = conteo_por_libro.get(titulo, 0) + 1
        
        ranking = sorted(conteo_por_libro.items(), key=lambda item: item[1], reverse=True)
        return [{"libro": titulo, "solicitudes_intersede": total} for titulo, total in ranking]