from datetime import date, timedelta
from models.entidades import Sede, Socio, Libro, Ejemplar
from models.enum import Estado
from models.gestor import GestorBiblioteca


def cargar_datos_iniciales(gestor: GestorBiblioteca):
    """
    Carga un conjunto completo y realista de datos iniciales para la red bibliotecaria:
    - Sedes activas y una sede dada de baja (para probar validaciones).
    - Socios habilitados y un socio penalizado (para probar restricciones).
    - Catálogo amplio con clásicos de Ciencia Ficción, Fantasía, Matemática, Física e Ingeniería.
    - Ejemplares físicos distribuidos estratégicamente entre sedes.
    - Escenarios operativos representativos: préstamos locales, interbibliotecarios con remitos
      en diversos estados (Creado, Empaquetado, Despachado/En Tránsito), préstamos vencidos
      con cálculo de mora para reportes, préstamos devueltos y reservas activas.
    """
    if gestor.sedes:
        return  # Ya fue inicializado

    # =========================================================================
    # 1. SEDES DE LA RED
    # =========================================================================
    sede_central = Sede(
        id_sede="SED-01",
        nombre="Sede Central",
        direccion="Av. Corrientes 1234, CABA",
        contacto="central@bibliored.org / 011-4381-1111",
        horarios="Lun a Vie 8:00 - 20:00, Sáb 9:00 - 13:00",
        activa=True
    )
    sede_norte = Sede(
        id_sede="SED-02",
        nombre="Sede Norte",
        direccion="Av. Cabildo 2450, Belgrano",
        contacto="norte@bibliored.org / 011-4782-2222",
        horarios="Lun a Sáb 9:00 - 18:00",
        activa=True
    )
    sede_patricios = Sede(
        id_sede="SED-03",
        nombre="Sede Parque Patricios (Polo Tec)",
        direccion="Av. Caseros 3010, Parque Patricios",
        contacto="patricios@bibliored.org / 011-4943-3333",
        horarios="Lun a Vie 9:00 - 19:00",
        activa=True
    )
    sede_sur = Sede(
        id_sede="SED-04",
        nombre="Sede Sur (En refacción)",
        direccion="Av. Montes de Oca 780, Barracas",
        contacto="sur@bibliored.org / 011-4301-4444",
        horarios="Cerrada temporalmente por obras",
        activa=False  # Sede inhabilitada / dada de baja para validar regla de negocio
    )

    gestor.agregar_sede(sede_central)
    gestor.agregar_sede(sede_norte)
    gestor.agregar_sede(sede_patricios)
    gestor.agregar_sede(sede_sur)

    # =========================================================================
    # 2. PADRÓN DE SOCIOS
    # =========================================================================
    s1 = Socio("SOC-01", "Martín", "Palermo", "30111222", "mpalermo@email.com")
    s2 = Socio("SOC-02", "Lucía", "Gómez", "35444555", "lucia.gomez@email.com")
    s3 = Socio("SOC-03", "Carlos", "Tevez", "28999888", "carlitos@email.com")
    # Carlos Tevez tiene una penalización activa para probar validación de Socio Inhabilitado
    s3.penalizado_hasta = date(2026, 12, 31)

    s4 = Socio("SOC-04", "Valentina", "Rossi", "41234567", "valentina.rossi@email.com")
    s5 = Socio("SOC-05", "Matías", "Fernández", "39876543", "mfernandez@email.com")
    s6 = Socio("SOC-06", "Sofía", "Benítez", "42111222", "sbenitez@email.com")
    s7 = Socio("SOC-07", "Lucas", "Navarro", "37555666", "lucas.navarro@email.com")
    s8 = Socio("SOC-08", "Camila", "Herrera", "40333444", "cherrera@email.com")

    gestor.agregar_socio(s1)
    gestor.agregar_socio(s2)
    gestor.agregar_socio(s3)
    gestor.agregar_socio(s4)
    gestor.agregar_socio(s5)
    gestor.agregar_socio(s6)
    gestor.agregar_socio(s7)
    gestor.agregar_socio(s8)

    # =========================================================================
    # 3. CATÁLOGO DE LIBROS (Ciencia Ficción, Fantasía, Matemática, Física, Software)
    # =========================================================================
    # --- Ciencia Ficción ---
    l_dune = Libro("978-0441013593", "Dune", "Frank Herbert", "Ciencia Ficción", "Ace Books")
    l_fundacion = Libro("978-0553293357", "Fundación", "Isaac Asimov", "Ciencia Ficción", "Spectra")
    l_neuromante = Libro("978-0441569595", "Neuromante", "William Gibson", "Ciencia Ficción", "Minotauro")
    l_f451 = Libro("978-1451673319", "Fahrenheit 451", "Ray Bradbury", "Ciencia Ficción", "Simon & Schuster")
    l_3cuerpos = Libro("978-0765382030", "El Problema de los Tres Cuerpos", "Cixin Liu", "Ciencia Ficción", "Tor Books")
    l_androides = Libro("978-0345404473", "¿Sueñan los androides con ovejas eléctricas?", "Philip K. Dick", "Ciencia Ficción", "Del Rey")

    # --- Fantasía ---
    l_esdla = Libro("978-0547928210", "El Señor de los Anillos: La Comunidad del Anillo", "J.R.R. Tolkien", "Fantasía", "Minotauro")
    l_viento = Libro("978-0756404741", "El Nombre del Viento", "Patrick Rothfuss", "Fantasía", "Plaza & Janés")
    l_tronos = Libro("978-0553103540", "Juego de Tronos (Canción de Hielo y Fuego I)", "George R.R. Martin", "Fantasía", "Bantam Books")
    l_hp = Libro("978-8478884452", "Harry Potter y la Piedra Filosofal", "J.K. Rowling", "Fantasía", "Salamandra")
    l_elantris = Libro("978-8466658829", "Elantris", "Brandon Sanderson", "Fantasía", "Nova")

    # --- Matemática ---
    l_calculo = Libro("978-6075265506", "Cálculo de una Variable: Trascendentes Tempranas", "James Stewart", "Matemática", "Cengage Learning")
    l_algebra = Libro("978-6073213981", "Álgebra Lineal y sus Aplicaciones", "David C. Lay", "Matemática", "Pearson Educación")
    l_topologia = Libro("978-0070573956", "Introducción a la Topología y al Análisis Moderno", "George F. Simmons", "Matemática", "McGraw-Hill")
    l_calculaba = Libro("978-9500419369", "El Hombre que Calculaba", "Malba Tahan", "Matemática", "Emecé Editores")

    # --- Física ---
    l_fisica_univ = Libro("978-6073221245", "Física Universitaria (Volumen 1)", "Young & Freedman (Sears-Zemansky)", "Física", "Pearson")
    l_cuantica = Libro("978-9681804190", "Física Cuántica: Átomos, Moléculas y Sólidos", "Robert Eisberg y Robert Resnick", "Física", "Limusa Wiley")
    l_tiempo = Libro("978-8484326199", "Historia del Tiempo: Del Big Bang a los Agujeros Negros", "Stephen Hawking", "Física", "Crítica")
    l_feynman = Libro("978-8498922844", "Seis Piezas Fáciles: Fundamentos de la Física", "Richard P. Feynman", "Física", "Crítica")

    # --- Ingeniería de Software y Arquitectura ---
    l_cleancode = Libro("978-0132350884", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Ingeniería de Software", "Prentice Hall")
    l_gof = Libro("978-0201633610", "Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides", "Patrones de Diseño", "Addison-Wesley")
    l_cleanarch = Libro("978-0134494166", "Clean Architecture", "Robert C. Martin", "Arquitectura de Software", "Prentice Hall")

    libros = [
        l_dune, l_fundacion, l_neuromante, l_f451, l_3cuerpos, l_androides,
        l_esdla, l_viento, l_tronos, l_hp, l_elantris,
        l_calculo, l_algebra, l_topologia, l_calculaba,
        l_fisica_univ, l_cuantica, l_tiempo, l_feynman,
        l_cleancode, l_gof, l_cleanarch
    ]
    for lib in libros:
        gestor.agregar_libro(lib)

    # =========================================================================
    # 4. EJEMPLARES FÍSICOS DISTRIBUIDOS EN LAS SEDES
    # =========================================================================
    ejemplares = [
        # Dune
        Ejemplar("EJ-01", l_dune, sede_central),
        Ejemplar("EJ-02", l_dune, sede_norte),
        Ejemplar("EJ-03", l_dune, sede_patricios),
        # Fundación
        Ejemplar("EJ-04", l_fundacion, sede_central),
        Ejemplar("EJ-05", l_fundacion, sede_patricios),
        # Neuromante
        Ejemplar("EJ-06", l_neuromante, sede_norte),
        # Fahrenheit 451
        Ejemplar("EJ-07", l_f451, sede_central),
        # El Problema de los Tres Cuerpos
        Ejemplar("EJ-08", l_3cuerpos, sede_central),
        Ejemplar("EJ-09", l_3cuerpos, sede_patricios),
        # Androides
        Ejemplar("EJ-10", l_androides, sede_norte),
        # El Señor de los Anillos
        Ejemplar("EJ-11", l_esdla, sede_central),
        Ejemplar("EJ-12", l_esdla, sede_norte),
        # El Nombre del Viento
        Ejemplar("EJ-13", l_viento, sede_central),
        Ejemplar("EJ-14", l_viento, sede_patricios),
        # Harry Potter
        Ejemplar("EJ-15", l_hp, sede_norte),
        Ejemplar("EJ-16", l_hp, sede_central),
        # Juego de Tronos
        Ejemplar("EJ-17", l_tronos, sede_patricios),
        # Cálculo Stewart
        Ejemplar("EJ-18", l_calculo, sede_central),
        Ejemplar("EJ-19", l_calculo, sede_norte),
        Ejemplar("EJ-20", l_calculo, sede_patricios),
        # Álgebra Lineal Lay
        Ejemplar("EJ-21", l_algebra, sede_central),
        Ejemplar("EJ-22", l_algebra, sede_patricios),
        # El Hombre que Calculaba
        Ejemplar("EJ-23", l_calculaba, sede_norte),
        # Física Universitaria Sears-Zemansky
        Ejemplar("EJ-24", l_fisica_univ, sede_central),
        Ejemplar("EJ-25", l_fisica_univ, sede_norte),
        Ejemplar("EJ-26", l_fisica_univ, sede_patricios),
        # Física Cuántica
        Ejemplar("EJ-27", l_cuantica, sede_norte),
        # Historia del Tiempo
        Ejemplar("EJ-28", l_tiempo, sede_central),
        # Seis Piezas Fáciles
        Ejemplar("EJ-29", l_feynman, sede_patricios),
        # Clean Code
        Ejemplar("EJ-30", l_cleancode, sede_central),
        Ejemplar("EJ-31", l_cleancode, sede_norte),
        # Design Patterns GoF
        Ejemplar("EJ-32", l_gof, sede_central),
        Ejemplar("EJ-33", l_gof, sede_patricios),
    ]

    for ej in ejemplares:
        gestor.agregar_ejemplar(ej)

    # =========================================================================
    # 5. ESCENARIOS OPERATIVOS (Préstamos, Remitos en varios estados y Reservas)
    # =========================================================================
    # A. Préstamo local activo: Martín Palermo toma Clean Code en Sede Central
    gestor.crear_prestamo(
        id_prestamo="PREST-101",
        id_socio="SOC-01",
        id_ejemplar="EJ-30",
        id_sede_origen="SED-01",
        id_sede_destino="SED-01",
        dias_prestamo=14
    )

    # B. Préstamo interbibliotecario en preparación (Remito CREADO):
    # Lucía Gómez solicita Design Patterns GoF de Sede Central para retirar en Sede Norte
    gestor.crear_prestamo(
        id_prestamo="PREST-102",
        id_socio="SOC-02",
        id_ejemplar="EJ-32",
        id_sede_origen="SED-01",
        id_sede_destino="SED-02",
        dias_prestamo=14
    )

    # C. Préstamo interbibliotecario EN TRÁNSITO (Remito DESPACHADO):
    # Valentina Rossi pide Dune de Sede Central para retirar en Sede Parque Patricios.
    # El remito avanza por Creado -> Empaquetado -> Despachado, dejando el ejemplar EN_TRANSITO.
    gestor.crear_prestamo(
        id_prestamo="PREST-103",
        id_socio="SOC-04",
        id_ejemplar="EJ-01",
        id_sede_origen="SED-01",
        id_sede_destino="SED-03",
        dias_prestamo=10
    )
    gestor.empaquetar_remito("REM-PREST-103")
    gestor.despachar_remito("REM-PREST-103")

    # D. Préstamo interbibliotecario EMPAQUETADO:
    # Matías Fernández solicita Física Sears-Zemansky de Sede Norte para retirar en Sede Central.
    gestor.crear_prestamo(
        id_prestamo="PREST-104",
        id_socio="SOC-05",
        id_ejemplar="EJ-25",
        id_sede_origen="SED-02",
        id_sede_destino="SED-01",
        dias_prestamo=14
    )
    gestor.empaquetar_remito("REM-PREST-104")

    # E. Préstamo VENCIDO (para alimentar el Reporte 2 de mora y atraso):
    # Sofía Benítez solicitó Cálculo Stewart en Sede Norte hace 25 días con plazo de 14 días.
    fecha_inicio_vencido = date.today() - timedelta(days=25)
    gestor.crear_prestamo(
        id_prestamo="PREST-105",
        id_socio="SOC-06",
        id_ejemplar="EJ-19",
        id_sede_origen="SED-02",
        id_sede_destino="SED-02",
        dias_prestamo=14,
        fecha_inicio=fecha_inicio_vencido
    )

    # F. Préstamo DEVUELTO históricamente (cumplido en tiempo y forma):
    # Lucas Navarro tomó El Señor de los Anillos y ya lo devolvió en estado EXCELENTE.
    p_devuelto = gestor.crear_prestamo(
        id_prestamo="PREST-106",
        id_socio="SOC-07",
        id_ejemplar="EJ-11",
        id_sede_origen="SED-01",
        id_sede_destino="SED-01",
        dias_prestamo=7,
        fecha_inicio=date.today() - timedelta(days=10)
    )
    gestor.registrar_devolucion("PREST-106", date.today() - timedelta(days=3), Estado.OPTIMO)

    # =========================================================================
    # 6. RESERVAS ACTIVAS
    # =========================================================================
    gestor.crear_reserva(
        id_socio="SOC-08",
        isbn="978-0765382030",  # El Problema de los Tres Cuerpos
        id_sede="SED-01",
        id_reserva="RES-01"
    )
    gestor.crear_reserva(
        id_socio="SOC-01",
        isbn="978-8484326199",  # Historia del Tiempo (Hawking)
        id_sede="SED-03",
        id_reserva="RES-02"
    )
