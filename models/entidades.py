from models.excepciones import SedeDadaDeBajaError
from datetime import date
from models.enum import EstadoEjemplar, Estado

class Sede:
    def __init__(self,id_sede: str, nombre: str, direccion: str, contacto: str, horarios: str, activa: bool=True):
        self.id_sede = id_sede
        self.nombre = nombre
        self.direccion = direccion
        self.contacto = contacto
        self.horarios = horarios
        self.activa = activa
    
    @property
    def id_sede(self):
        return self._id_sede
    
    def verificar_sede(self):
        if not self.activa:
            raise SedeDadaDeBajaError(f"La sede {self.nombre} ha sido dada de baja y no está disponible para operaciones.")
        
    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"Sede: {self.nombre}, Dirección: {self.direccion}, Contacto: {self.contacto}, Horarios: {self.horarios}, Estado: {estado}"
    
    

class Socio:
    def __init__(self, id_socio: str, nombre: str, apellido: str, dni: str, email: str):
        self._id_socio = id_socio
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.email = email
        self._penalizado_hasta = None  # Inicialmente no está penalizado
        
    @property
    def id_socio(self):
        return self._id_socio
    
    @property
    def penalizado_hasta(self):
        return self._penalizado_hasta
    
    @penalizado_hasta.setter
    def penalizado_hasta(self, fecha):
        self._penalizado_hasta = fecha
    
    def esta_habilitado(self, fecha_actual: date) -> bool:
        if self._penalizado_hasta and fecha_actual <= self._penalizado_hasta:
            return False
        return True
    
    def __str__(self):
        return f"Socio: {self.nombre} {self.apellido}, DNI: {self.dni}, Email: {self.email}, Penalizado hasta: {self._penalizado_hasta if self._penalizado_hasta else 'No penalizado'}"
    
    
#isbn es un identificador único para cada libro(International Standard Book Number).
class Libro:
    def __init__(self, isbn: str, titulo: str, autor: str, categoria: str, editorial: str ):
        self._isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.editorial = editorial
    
    @property
    def isbn(self):
        return self._isbn
    
    def __str__(self):
        return f"Libro: {self.titulo}, Autor: {self.autor}, ISBN: {self.isbn}, Categoría: {self.categoria}, Editorial: {self.editorial}"
    
    
    
class Ejemplar:
    def __init__(self, id_ejemplar: str, libro: Libro, sede: Sede):
        self._id_ejemplar = id_ejemplar
        self.libro = libro
        self.sede = sede
        self.estado_ejemplar = EstadoEjemplar.DISPONIBLE  # Estado inicial
        self.estado = Estado.OPTIMO  # Estado inicial del libro

    @property
    def id_ejemplar(self):
        return self._id_ejemplar

    @property
    def estado_ejemplar(self):
        return self._estado_ejemplar

    def esta_disponible(self) -> bool:
        return self.estado_ejemplar == EstadoEjemplar.DISPONIBLE

    def __str__(self):
        return f"Ejemplar: {self.id_ejemplar}, Libro: {self.libro.titulo}, Sede: {self.sede.nombre}, Estado: {self.estado_ejemplar.name}"