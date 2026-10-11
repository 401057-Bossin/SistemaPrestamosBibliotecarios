# tests/test_remito.py
import pytest
from models.remito import Remito, Creado, Empaquetado, Despachado, Recibido
from models.excepciones import TransicionInvalidaError

# --- Preparación de datos falsos (Mocks) para la prueba ---
class SedeMock:
    def __init__(self, nombre):
        self.nombre = nombre

class EjemplarMock:
    def __init__(self, id_ejemplar):
        self.id_ejemplar = id_ejemplar

# --- PRUEBAS DEL PATRÓN STATE ---

def test_estado_inicial_es_creado():
    origen = SedeMock("Sede A")
    destino = SedeMock("Sede B")
    ejemplar = EjemplarMock("EJ-1")
    
    remito = Remito("REM-001", ejemplar, origen, destino)
    
    assert isinstance(remito.estado_actual, Creado)
    assert len(remito.historial_trazabilidad) == 1

def test_transicion_valida_creado_a_empaquetado():
    remito = Remito("REM-002", None, None, None)
    remito.empaquetar()
    
    assert isinstance(remito.estado_actual, Empaquetado)
    assert len(remito.historial_trazabilidad) == 2

def test_transicion_invalida_despachar_sin_empaquetar():
    remito = Remito("REM-003", None, None, None)
    
    with pytest.raises(TransicionInvalidaError, match="No se puede despachar un remito que no está empaquetado"):
        remito.despachar()

def test_ciclo_de_vida_completo_y_trazabilidad():
    remito = Remito("REM-004", None, None, None)
    
    remito.empaquetar()
    remito.despachar()
    remito.recibir()
    
    assert isinstance(remito.estado_actual, Recibido)
    assert len(remito.historial_trazabilidad) == 4
    
def test_transicion_invalida_recibido_no_puede_modificarse():
    remito = Remito("REM-005", None, None, None)
    remito.empaquetar()
    remito.despachar()
    remito.recibir()
    
    with pytest.raises(TransicionInvalidaError):
        remito.empaquetar()