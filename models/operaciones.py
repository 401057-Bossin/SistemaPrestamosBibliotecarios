from datetime import date, timedelta
from models.enum import EstadoEjemplar, Estado
from models.excepciones import (
    SocioInhabilitadoError,
    EjemplarNoDisponibleError,
    SedeDadaDeBajaError,
)
from models.entidades import Socio, Libro, Ejemplar, Sede


class Prestamo:
    def __init__(
        self,
        id_prestamo: str,
        socio: Socio,
        ejemplar: Ejemplar,
        sede_origen: Sede,
        sede_destino: Sede = None,
        dias_prestamo: int = 14,
        fecha_inicio: date = None
    ):
        fecha_ref = fecha_inicio if fecha_inicio else date.today()

        # 1. Validar que el socio esté habilitado (sin penalizaciones activas)
        if not socio.esta_habilitado(fecha_ref):
            raise SocioInhabilitadoError(f"El socio {socio.nombre} {socio.apellido} se encuentra inhabilitado para préstamos.")
        
        # 2. Validar que el ejemplar esté disponible físicamente
        if not ejemplar.esta_disponible():
            raise EjemplarNoDisponibleError(f"El ejemplar {ejemplar.id_ejemplar} no está disponible.")
            
        # 3. Validar que ni la sede origen ni la destino estén dadas de baja
        sede_origen.verificar_sede()
        if sede_destino:
            sede_destino.verificar_sede()

        # 4. Validar que el ejemplar pertenezca a la sede de origen
        if ejemplar.sede.id_sede != sede_origen.id_sede:
            raise EjemplarNoDisponibleError(f"El ejemplar {ejemplar.id_ejemplar} no pertenece a la sede de origen {sede_origen.nombre}.")

        self.id_prestamo: str = id_prestamo
        self.socio: Socio = socio
        self.ejemplar: Ejemplar = ejemplar
        self.sede_origen: Sede = sede_origen
        self.sede_destino: Sede = sede_destino if sede_destino else sede_origen
        
        self.fecha_inicio: date = fecha_ref
        self.fecha_vencimiento: date = self.fecha_inicio + timedelta(days=dias_prestamo)
        self.fecha_devolucion: date = None
        self.estado_devuelto: Estado = None

        # Al concretar el préstamo, el ejemplar pasa a estar PRESTADO
        self.ejemplar.estado_ejemplar = EstadoEjemplar.PRESTADO

    @property
    def es_interbibliotecario(self) -> bool:
        """Indica si el préstamo requirió traslado entre sedes distintas."""
        return self.sede_origen.id_sede != self.sede_destino.id_sede

    def esta_vencido(self, fecha_actual: date = None) -> bool:
        """Chequea si ya venció y todavía no fue devuelto."""
        if fecha_actual is None:
            fecha_actual = date.today()
        return not self.fecha_devolucion and fecha_actual > self.fecha_vencimiento

    def registrar_devolucion(self, fecha_devolucion: date, estado_fisico: Estado):
        """
        Registra la entrega física del libro, actualiza su estado 
        y penaliza al socio si hubo demora.
        """
        self.fecha_devolucion = fecha_devolucion
        self.estado_devuelto = estado_fisico
        self.ejemplar.estado_ejemplar = EstadoEjemplar.DISPONIBLE
        self.ejemplar.estado = estado_fisico
        # Si fue interbibliotecario y se devolvió en la sede destino, el ejemplar queda ahora radicado allí
        self.ejemplar.sede = self.sede_destino
        
        # Si se devolvió pasado el vencimiento, aplicamos sanción
        if fecha_devolucion > self.fecha_vencimiento:
            dias_retraso = (fecha_devolucion - self.fecha_vencimiento).days
            self.socio.penalizado_hasta = fecha_devolucion + timedelta(days=dias_retraso * 2)

    def __str__(self) -> str:
        return f"Préstamo {self.id_prestamo}: Socio {self.socio.dni}, Ejemplar {self.ejemplar.id_ejemplar}, Vence: {self.fecha_vencimiento}"


class Reserva:
    def __init__(self, id_reserva: str, socio: Socio, libro: Libro, sede: Sede):
        sede.verificar_sede()
        
        if not socio.esta_habilitado(date.today()):
            raise SocioInhabilitadoError(f"El socio {socio.nombre} {socio.apellido} está inhabilitado y no puede reservar.")

        self.id_reserva: str = id_reserva
        self.socio: Socio = socio
        self.libro: Libro = libro
        self.sede: Sede = sede
        self.fecha_solicitud: date = date.today()
        self.activa: bool = True

    def cancelar(self):
        self.activa = False

    def __str__(self) -> str:
        return f"Reserva {self.id_reserva}: Libro '{self.libro.titulo}' por {self.socio.nombre} en {self.sede.nombre}"