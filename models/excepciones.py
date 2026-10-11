class BibliotecaExcepcion(Exception):
    pass


class EjemplarNoDisponibleError(BibliotecaExcepcion):
    pass


class SocioInhabilitadoError(BibliotecaExcepcion):
    pass


class SedeDadaDeBajaError(BibliotecaExcepcion):
    pass


class TransicionInvalidaError(BibliotecaExcepcion):
    pass


