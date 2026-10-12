import pytest
from datetime import date, timedelta
from models.gestor import GestorBiblioteca
from models.entidades import Sede, Socio, Libro, Ejemplar
from models.enum import Estado, EstadoEjemplar
from models.excepciones import (
    BibliotecaExcepcion,
    SocioInhabilitadoError,
    EjemplarNoDisponibleError,
    SedeDadaDeBajaError
)


@pytest.fixture(autouse=True)
def reiniciar_gestor():
    """Reinicia la instancia Singleton antes de cada test para aislar el estado."""
    gestor = GestorBiblioteca()
    gestor._inicializar_datos()
    return gestor


def test_autogeneracion_ids_entidades(reiniciar_gestor):
    gestor = reiniciar_gestor
    
    # 1. Sede con ID autogenerado
    sede = Sede(nombre="Sede Belgrano", direccion="Av. Cabildo 100", contacto="b@red.org", horarios="9-18")
    gestor.agregar_sede(sede)
    assert sede.id_sede == "SED-01"

    # Segunda sede
    sede2 = Sede(nombre="Sede Palermo", direccion="Santa Fe 2000", contacto="p@red.org", horarios="9-18")
    gestor.agregar_sede(sede2)
    assert sede2.id_sede == "SED-02"

    # 2. Socio con ID autogenerado
    socio = Socio(nombre="Lionel", apellido="Messi", dni="33111222", email="leo@afa.com")
    gestor.agregar_socio(socio)
    assert socio.id_socio == "SOC-01"

    # Segundo socio
    socio2 = Socio(nombre="Rodrigo", apellido="De Paul", dni="36222333", email="rdp@afa.com")
    gestor.agregar_socio(socio2)
    assert socio2.id_socio == "SOC-02"

    # 3. Libro con ISBN autogenerado
    libro = Libro(titulo="Libro Sin ISBN Inicial", autor="Autor Anónimo", categoria="Varios", editorial="Editorial")
    gestor.agregar_libro(libro)
    assert libro.isbn.startswith("978-AUTO-")

    # 4. Ejemplar con ID autogenerado
    ejemplar = Ejemplar(libro=libro, sede=sede)
    gestor.agregar_ejemplar(ejemplar)
    assert ejemplar.id_ejemplar == "EJ-01"


def test_autogeneracion_id_reserva_y_prestamo(reiniciar_gestor):
    gestor = reiniciar_gestor
    sede = gestor.agregar_sede(Sede(nombre="Central", direccion="Corrientes 100", contacto="c@red.org", horarios="8-20"))
    socio = gestor.agregar_socio(Socio(nombre="Juan", apellido="Perez", dni="30111222", email="jp@test.com"))
    libro = gestor.agregar_libro(Libro(isbn="978-1234567890", titulo="Dune", autor="Frank Herbert", categoria="Sci-Fi", editorial="Ace"))
    ejemplar = gestor.agregar_ejemplar(Ejemplar(libro=libro, sede=sede))

    # Reserva con ID omitido
    reserva = gestor.crear_reserva(id_socio=socio.id_socio, isbn=libro.isbn, id_sede=sede.id_sede)
    assert reserva.id_reserva == "RES-01"
    assert reserva.libro.titulo == "Dune"

    # Segunda reserva
    reserva2 = gestor.crear_reserva(id_socio=socio.id_socio, isbn=libro.isbn, id_sede=sede.id_sede)
    assert reserva2.id_reserva == "RES-02"

    # Préstamo con ID omitido
    prestamo = gestor.crear_prestamo(
        id_socio=socio.id_socio,
        id_ejemplar=ejemplar.id_ejemplar,
        id_sede_origen=sede.id_sede,
        id_sede_destino=sede.id_sede
    )
    assert prestamo.id_prestamo == "PREST-101"
    assert ejemplar.estado_ejemplar == EstadoEjemplar.PRESTADO


def test_validacion_socio_inhabilitado_rechaza_prestamo_y_reserva(reiniciar_gestor):
    gestor = reiniciar_gestor
    sede = gestor.agregar_sede(Sede(nombre="Sede 1", direccion="Dir 1", contacto="c", horarios="h"))
    socio = gestor.agregar_socio(Socio(nombre="Carlos", apellido="Tevez", dni="28999888", email="c@test.com"))
    socio.penalizado_hasta = date.today() + timedelta(days=10)
    libro = gestor.agregar_libro(Libro(isbn="978-1111", titulo="Clean Code", autor="Uncle Bob", categoria="Dev", editorial="PH"))
    ejemplar = gestor.agregar_ejemplar(Ejemplar(libro=libro, sede=sede))

    # Intento de préstamo debe lanzar SocioInhabilitadoError
    with pytest.raises(SocioInhabilitadoError):
        gestor.crear_prestamo(
            id_socio=socio.id_socio,
            id_ejemplar=ejemplar.id_ejemplar,
            id_sede_origen=sede.id_sede
        )

    # Intento de reserva debe lanzar SocioInhabilitadoError
    with pytest.raises(SocioInhabilitadoError):
        gestor.crear_reserva(id_socio=socio.id_socio, isbn=libro.isbn, id_sede=sede.id_sede)


def test_validacion_sede_dada_de_baja(reiniciar_gestor):
    gestor = reiniciar_gestor
    sede_inactiva = gestor.agregar_sede(Sede(nombre="Sede Clausurada", direccion="D", contacto="c", horarios="h", activa=False))
    socio = gestor.agregar_socio(Socio(nombre="Ana", apellido="López", dni="40111222", email="a@test.com"))
    libro = gestor.agregar_libro(Libro(isbn="978-2222", titulo="Libro A", autor="Autor A", categoria="C", editorial="E"))
    ejemplar = gestor.agregar_ejemplar(Ejemplar(libro=libro, sede=sede_inactiva))

    with pytest.raises(SedeDadaDeBajaError):
        gestor.crear_prestamo(
            id_socio=socio.id_socio,
            id_ejemplar=ejemplar.id_ejemplar,
            id_sede_origen=sede_inactiva.id_sede
        )
