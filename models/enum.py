#Agrupas cjto de constantes para que sean más fáciles de usar y mantener.

from enum import Enum

class EstadoEjemplar(Enum):
    DISPONIBLE = "Disponible"
    PRESTADO = "Prestado"
    EN_PREPARACION = "En preparación"
    EN_TRANSITO = "En tránsito"
    RESERVADO = "Reservado"
    
class Estado(Enum):
    OPTIMO = "Óptimo"
    BUENO = "Bueno"
    DETERIORADO = "Deteriorado"
    DANADO = "Dañado"