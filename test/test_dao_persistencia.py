import os
import tempfile
import pytest
from datetime import date, datetime, timedelta
from models.entidades import Sede, Socio, Libro, Ejemplar
from models.enum import Estado, EstadoEjemplar
from models.operaciones import Prestamo, Reserva
from models.remito import Remito
from dao.database import inicializar_bd, vaciar_bd
from dao.sede_dao import SedeDAO
from dao.socio_dao import SocioDAO
from dao.libro_dao import LibroDAO
from dao.ejemplar_dao import EjemplarDAO
from dao.prestamo_dao import PrestamoDAO
from dao.reserva_dao import ReservaDAO
from dao.remito_dao import RemitoDAO
from models.gestor import GestorBiblioteca


@pytest.fixture
def temp_db():
    import gc
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    inicializar_bd(path)
    yield path
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_sede_dao_crud(temp_db):
    dao = SedeDAO(temp_db)
    sede = Sede(id_sede="SED-01", nombre="Central", direccion="Corrientes 100", contacto="c@red.org", horarios="8-20", activa=True)
    dao.crear(sede)

    obtenida = dao.obtener_por_id("SED-01")
    assert obtenida is not None
    assert obtenida.nombre == "Central"
    assert obtenida.activa is True

    dao.actualizar_estado("SED-01", False)
    actualizada = dao.obtener_por_id("SED-01")
    assert actualizada.activa is False

    sedes = dao.listar()
    assert len(sedes) == 1


def test_socio_dao_crud(temp_db):
    dao = SocioDAO(temp_db)
    socio = Socio(id_socio="SOC-01", nombre="Juan", apellido="Perez", dni="12345678", email="juan@test.com")
    dao.crear(socio)

    obtenido = dao.obtener_por_dni("12345678")
    assert obtenido is not None
    assert obtenido.id_socio == "SOC-01"

    fecha_penal = date.today() + timedelta(days=5)
    dao.actualizar_penalizacion("SOC-01", fecha_penal)
    actualizado = dao.obtener_por_id("SOC-01")
    assert actualizado.penalizado_hasta == fecha_penal


def test_libro_y_ejemplar_dao_crud(temp_db):
    sede_dao = SedeDAO(temp_db)
    sede = Sede(id_sede="SED-01", nombre="Central", activa=True)
    sede_dao.crear(sede)

    libro_dao = LibroDAO(temp_db)
    libro = Libro(isbn="978-01", titulo="Fundación", autor="Isaac Asimov", categoria="Sci-Fi", editorial="DeBolsillo")
    libro_dao.crear(libro)

    ej_dao = EjemplarDAO(temp_db)
    ejemplar = Ejemplar(id_ejemplar="EJ-01", libro=libro, sede=sede)
    ej_dao.crear(ejemplar)

    ejemplares = ej_dao.listar(libros_dict={"978-01": libro}, sedes_dict={"SED-01": sede})
    assert len(ejemplares) == 1
    assert ejemplares[0].libro.titulo == "Fundación"

    ejemplares[0].estado_ejemplar = EstadoEjemplar.PRESTADO
    ej_dao.actualizar(ejemplares[0])
    ej_actualizado = ej_dao.obtener_por_id("EJ-01", libros_dict={"978-01": libro}, sedes_dict={"SED-01": sede})
    assert ej_actualizado.estado_ejemplar == EstadoEjemplar.PRESTADO


def test_prestamo_reserva_remito_dao(temp_db):
    # Setup base data
    sede_dao = SedeDAO(temp_db)
    sede1 = Sede("SED-01", "Central", activa=True)
    sede2 = Sede("SED-02", "Norte", activa=True)
    sede_dao.crear(sede1)
    sede_dao.crear(sede2)

    socio_dao = SocioDAO(temp_db)
    socio = Socio("SOC-01", "Ana", "Gomez", "20111222", "ana@test.com")
    socio_dao.crear(socio)

    libro_dao = LibroDAO(temp_db)
    libro = Libro("978-02", "1984", "George Orwell", "Ficción", "Penguin")
    libro_dao.crear(libro)

    ej_dao = EjemplarDAO(temp_db)
    ej = Ejemplar("EJ-02", libro=libro, sede=sede1)
    ej_dao.crear(ej)

    # PrestamoDAO
    prestamo_dao = PrestamoDAO(temp_db)
    prestamo = Prestamo("PREST-001", socio, ej, sede1, sede2, dias_prestamo=14, fecha_inicio=date.today())
    prestamo_dao.crear(prestamo)

    prestamos = prestamo_dao.listar({"SOC-01": socio}, {"EJ-02": ej}, {"SED-01": sede1, "SED-02": sede2})
    assert len(prestamos) == 1
    assert prestamos[0].es_interbibliotecario is True

    # ReservaDAO
    reserva_dao = ReservaDAO(temp_db)
    reserva = Reserva("RES-001", socio, libro, sede1)
    reserva_dao.crear(reserva)
    reservas = reserva_dao.listar({"SOC-01": socio}, {"978-02": libro}, {"SED-01": sede1})
    assert len(reservas) == 1
    assert reservas[0].activa is True

    reserva_dao.actualizar_activa("RES-001", False)
    res_actualizada = reserva_dao.obtener_por_id("RES-001", {"SOC-01": socio}, {"978-02": libro}, {"SED-01": sede1})
    assert res_actualizada.activa is False

    # RemitoDAO
    remito_dao = RemitoDAO(temp_db)
    remito = Remito("REM-PREST-001", ej, sede1, sede2)
    remito_dao.crear(remito)
    remito_dao.agregar_trazabilidad("REM-PREST-001", "Empaquetado", datetime.now(), "Empaquetado para despacho")
    
    traz = remito_dao.obtener_trazabilidad("REM-PREST-001")
    assert len(traz) == 2
    assert traz[1]["estado"] == "Empaquetado"


def test_persistencia_recarga_en_gestor():
    # Usar el gestor y verificar persistencia
    gestor = GestorBiblioteca()
    gestor.reiniciar_para_tests("test_biblioteca.db")

    s = gestor.agregar_sede(Sede(nombre="Sede Prueba Persistencia", activa=True))
    soc = gestor.agregar_socio(Socio(nombre="Mario", apellido="Bros", dni="99887766", email="m@bros.com"))
    lib = gestor.agregar_libro(Libro(titulo="El Aleph", autor="Jorge Luis Borges"))
    ej = gestor.agregar_ejemplar(Ejemplar(libro=lib, sede=s))

    # Recargar datos desde la BD SQLite simulando reinicio
    gestor._cargar_desde_bd()

    assert s.id_sede in gestor.sedes
    assert gestor.sedes[s.id_sede].nombre == "Sede Prueba Persistencia"
    assert soc.id_socio in gestor.socios
    assert gestor.socios[soc.id_socio].dni == "99887766"
    assert lib.isbn in gestor.libros
    assert ej.id_ejemplar in gestor.ejemplares
