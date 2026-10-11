from abc import ABC, abstractmethod
from datetime import datetime
from models.excepciones import TransicionInvalidaError

#Cualqioer estado q exista tiene q tener los metodos empaquetar, despachar y recibir,
#por eso se define la clase abstracta EstadoRemito
class EstadoRemito(ABC):
    @abstractmethod
    def empaquetar(self, remito):
        pass

    @abstractmethod
    def despachar(self, remito):
        pass

    @abstractmethod
    def recibir(self, remito):
        pass

    def __str__(self):
        return self.__class__.__name__


class Creado(EstadoRemito):
    def empaquetar(self, remito):
        remito.estado_actual = Empaquetado()
        remito.registrar_trazabilidad("Empaquetado")

    def despachar(self, remito):
        raise TransicionInvalidaError("No se puede despachar un remito que no está empaquetado")

    def recibir(self, remito):
        raise TransicionInvalidaError("No se puede recibir un remito que no está empaquetado")


class Empaquetado(EstadoRemito):
    def empaquetar(self, remito):
        raise TransicionInvalidaError("El remito ya ha sido empaquetado")

    def despachar(self, remito):
        remito.estado_actual = Despachado()
        remito.registrar_trazabilidad("Despachado")

    def recibir(self, remito):
        raise TransicionInvalidaError("No se puede recibir un remito que no ha sido despachado")


class Despachado(EstadoRemito):
    def empaquetar(self, remito):
        raise TransicionInvalidaError("No se puede empaquetar un remito que ya ha sido despachado")

    def despachar(self, remito):
        raise TransicionInvalidaError("El remito ya ha sido despachado")

    def recibir(self, remito):
        remito.estado_actual = Recibido()
        remito.registrar_trazabilidad("Recibido")


class Recibido(EstadoRemito):
    def empaquetar(self, remito):
        raise TransicionInvalidaError("No se puede empaquetar un remito que ya ha sido recibido")

    def despachar(self, remito):
        raise TransicionInvalidaError("No se puede despachar un remito que ya ha sido recibido")

    def recibir(self, remito):
        raise TransicionInvalidaError("El remito ya ha sido recibido")


class Remito:
    def __init__(self, id_remito: str, ejemplar, sede_origen, sede_destino):
        self._id_remito = id_remito
        self.ejemplar = ejemplar
        self.sede_origen = sede_origen
        self.sede_destino = sede_destino
        self.estado_actual = Creado()
        self.trazabilidad = []
        self.registrar_trazabilidad("Creado")

    @property
    def id_remito(self):
        return self._id_remito

    @id_remito.setter
    def id_remito(self, value):
        self._id_remito = value

    @property
    def historial_trazabilidad(self):
        return self.trazabilidad

    def registrar_trazabilidad(self, observacion: str):
        registro = {
            "estado": str(self.estado_actual),
            "fecha_hora": datetime.now(),
            "observacion": observacion
        }
        self.trazabilidad.append(registro)

    # delega la accion a su estado actual que es una clase con sus def, que es quien sabe como empaquetar un remito
    def empaquetar(self):
        self.estado_actual.empaquetar(self)

    def despachar(self):
        self.estado_actual.despachar(self)

    def recibir(self):
        self.estado_actual.recibir(self)

    def __str__(self):
        return f"Remito {self.id_remito} - Estado: {self.estado_actual}"