from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from models.gestor import GestorBiblioteca
from models.datos_demo import cargar_datos_iniciales
from models.entidades import Sede, Socio, Libro, Ejemplar
from models.enum import Estado
from models.excepciones import BibliotecaExcepcion, TransicionInvalidaError

app = Flask(__name__)
app.secret_key = "dao_biblioteca_secret_key_2026"

# Instanciamos el Gestor (Singleton) y cargamos datos demostrativos
gestor = GestorBiblioteca()
cargar_datos_iniciales(gestor)


# -------------------------------------------------------------------------
# 1. Dashboard Principal
# -------------------------------------------------------------------------
@app.route("/")
def index():
    ultimos_prestamos = sorted(gestor.prestamos, key=lambda p: p.fecha_inicio, reverse=True)[:5]
    remitos_en_proceso = [r for r in gestor.remitos if r.estado_actual.__class__.__name__ != "Recibido"]
    
    total_prestamos_activos = len([p for p in gestor.prestamos if p.fecha_devolucion is None])
    
    return render_template(
        "index.html",
        total_sedes=len(gestor.sedes),
        total_socios=len(gestor.socios),
        total_libros=len(gestor.libros),
        total_ejemplares=len(gestor.ejemplares),
        total_prestamos_activos=total_prestamos_activos,
        total_remitos=len(gestor.remitos),
        ultimos_prestamos=ultimos_prestamos,
        remitos_en_proceso=remitos_en_proceso
    )


# -------------------------------------------------------------------------
# 2. Sedes
# -------------------------------------------------------------------------
@app.route("/sedes", methods=["GET", "POST"])
def sedes():
    if request.method == "POST":
        id_sede = request.form.get("id_sede", "").strip() or None
        nombre = request.form.get("nombre", "").strip()
        direccion = request.form.get("direccion", "").strip()
        contacto = request.form.get("contacto", "").strip()
        horarios = request.form.get("horarios", "").strip()
        activa = True if request.form.get("activa") else False

        try:
            nueva_sede = Sede(
                id_sede=id_sede,
                nombre=nombre,
                direccion=direccion,
                contacto=contacto,
                horarios=horarios,
                activa=activa
            )
            sede_creada = gestor.agregar_sede(nueva_sede)
            flash(f"Sede '{nombre}' ({sede_creada.id_sede}) registrada exitosamente.", "success")
        except BibliotecaExcepcion as e:
            flash(str(e), "danger")
        return redirect(url_for("sedes"))

    return render_template("sedes.html", sedes=list(gestor.sedes.values()))


@app.route("/sedes/<id_sede>/toggle", methods=["POST"])
def toggle_sede(id_sede):
    try:
        sede = gestor.obtener_sede(id_sede)
        nuevo_estado = not sede.activa
        gestor.cambiar_estado_sede(id_sede, nuevo_estado)
        estado_txt = "activada" if nuevo_estado else "dada de baja"
        flash(f"Sede '{sede.nombre}' ha sido {estado_txt}.", "info")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("sedes"))


# -------------------------------------------------------------------------
# 3. Socios
# -------------------------------------------------------------------------
@app.route("/socios", methods=["GET", "POST"])
def socios():
    if request.method == "POST":
        id_socio = request.form.get("id_socio", "").strip() or None
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        dni = request.form.get("dni", "").strip()
        email = request.form.get("email", "").strip()

        try:
            nuevo_socio = Socio(id_socio=id_socio, nombre=nombre, apellido=apellido, dni=dni, email=email)
            socio_creado = gestor.agregar_socio(nuevo_socio)
            flash(f"Socio {nombre} {apellido} ({socio_creado.id_socio}) registrado exitosamente.", "success")
        except BibliotecaExcepcion as e:
            flash(str(e), "danger")
        return redirect(url_for("socios"))

    return render_template("socios.html", socios=list(gestor.socios.values()), hoy=date.today())


# -------------------------------------------------------------------------
# 4. Catálogo, Ejemplares y Disponibilidad
# -------------------------------------------------------------------------
@app.route("/catalogo", methods=["GET"])
def catalogo():
    isbn_filtro = request.args.get("isbn", "").strip()
    id_sede_filtro = request.args.get("id_sede", "").strip()

    consulta_realizada = False
    resultados_disponibilidad = []

    if isbn_filtro:
        consulta_realizada = True
        resultados_disponibilidad = gestor.consultar_disponibilidad(
            isbn=isbn_filtro,
            id_sede=id_sede_filtro if id_sede_filtro else None
        )

    return render_template(
        "catalogo.html",
        libros=list(gestor.libros.values()),
        ejemplares=list(gestor.ejemplares.values()),
        sedes=list(gestor.sedes.values()),
        consulta_realizada=consulta_realizada,
        resultados_disponibilidad=resultados_disponibilidad,
        isbn_seleccionado=isbn_filtro,
        sede_seleccionada=id_sede_filtro
    )


@app.route("/catalogo/libro", methods=["POST"])
def nuevo_libro():
    isbn = request.form.get("isbn", "").strip() or None
    titulo = request.form.get("titulo", "").strip()
    autor = request.form.get("autor", "").strip()
    categoria = request.form.get("categoria", "").strip()
    editorial = request.form.get("editorial", "").strip()

    try:
        libro = Libro(isbn=isbn, titulo=titulo, autor=autor, categoria=categoria, editorial=editorial)
        libro_creado = gestor.agregar_libro(libro)
        flash(f"Libro '{titulo}' (ISBN: {libro_creado.isbn}) agregado al catálogo.", "success")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("catalogo"))


@app.route("/catalogo/ejemplar", methods=["POST"])
def nuevo_ejemplar():
    id_ejemplar = request.form.get("id_ejemplar", "").strip() or None
    isbn = request.form.get("isbn", "").strip()
    id_sede = request.form.get("id_sede", "").strip()

    try:
        libro = gestor.libros.get(isbn)
        if not libro:
            raise BibliotecaExcepcion("Libro no encontrado.")
        sede = gestor.obtener_sede(id_sede)
        ejemplar = Ejemplar(id_ejemplar=id_ejemplar, libro=libro, sede=sede)
        ejemplar_creado = gestor.agregar_ejemplar(ejemplar)
        flash(f"Ejemplar '{ejemplar_creado.id_ejemplar}' ({libro.titulo}) asignado a '{sede.nombre}'.", "success")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("catalogo"))


# -------------------------------------------------------------------------
# 5. Préstamos y Reservas
# -------------------------------------------------------------------------
@app.route("/prestamos", methods=["GET", "POST"])
def prestamos():
    if request.method == "POST":
        id_prestamo = request.form.get("id_prestamo", "").strip() or None
        id_socio = request.form.get("id_socio", "").strip()
        id_ejemplar = request.form.get("id_ejemplar", "").strip()
        id_sede_origen = request.form.get("id_sede_origen", "").strip()
        id_sede_destino = request.form.get("id_sede_destino", "").strip()
        dias_prestamo = int(request.form.get("dias_prestamo", 14))

        try:
            p = gestor.crear_prestamo(
                id_prestamo=id_prestamo,
                id_socio=id_socio,
                id_ejemplar=id_ejemplar,
                id_sede_origen=id_sede_origen,
                id_sede_destino=id_sede_destino if id_sede_destino else None,
                dias_prestamo=dias_prestamo
            )
            msg = f"Préstamo '{p.id_prestamo}' registrado con éxito."
            if p.es_interbibliotecario:
                msg += f" (Se generó remito interbibliotecario REM-{p.id_prestamo})"
            flash(msg, "success")
        except BibliotecaExcepcion as e:
            flash(f"Error al registrar préstamo: {e}", "danger")
        return redirect(url_for("prestamos"))

    return render_template(
        "prestamos.html",
        prestamos=gestor.prestamos,
        reservas=gestor.reservas,
        socios=list(gestor.socios.values()),
        ejemplares=list(gestor.ejemplares.values()),
        sedes=list(gestor.sedes.values()),
        libros=list(gestor.libros.values()),
        estados_fisicos=list(Estado),
        hoy=date.today()
    )


@app.route("/prestamos/<id_prestamo>/devolver", methods=["POST"])
def devolucion(id_prestamo):
    fecha_devolucion_str = request.form.get("fecha_devolucion")
    estado_fisico_str = request.form.get("estado_fisico")

    try:
        fecha_devolucion = date.fromisoformat(fecha_devolucion_str)
        estado_fisico = Estado[estado_fisico_str]
        gestor.registrar_devolucion(id_prestamo, fecha_devolucion, estado_fisico)
        flash(f"Devolución del préstamo '{id_prestamo}' registrada con éxito.", "success")
    except (BibliotecaExcepcion, ValueError, KeyError) as e:
        flash(f"Error al registrar devolución: {e}", "danger")
    return redirect(url_for("prestamos"))


@app.route("/reservas", methods=["POST"])
def crear_reserva():
    id_reserva = request.form.get("id_reserva", "").strip() or None
    id_socio = request.form.get("id_socio", "").strip()
    isbn = request.form.get("isbn", "").strip()
    id_sede = request.form.get("id_sede", "").strip()

    try:
        reserva = gestor.crear_reserva(id_socio=id_socio, isbn=isbn, id_sede=id_sede, id_reserva=id_reserva)
        flash(f"Reserva '{reserva.id_reserva}' registrada exitosamente para {reserva.socio.nombre} {reserva.socio.apellido}.", "success")
    except BibliotecaExcepcion as e:
        flash(f"Error al registrar reserva: {e}", "danger")
    return redirect(url_for("prestamos"))


@app.route("/reservas/<id_reserva>/cancelar", methods=["POST"])
def cancelar_reserva(id_reserva):
    reserva = next((r for r in gestor.reservas if r.id_reserva == id_reserva), None)
    if reserva:
        reserva.cancelar()
        flash(f"Reserva '{id_reserva}' cancelada.", "info")
    else:
        flash("Reserva no encontrada.", "danger")
    return redirect(url_for("prestamos"))


# -------------------------------------------------------------------------
# 6. Remitos y Logística (Patrón State)
# -------------------------------------------------------------------------
@app.route("/remitos")
def remitos():
    return render_template("remitos.html", remitos=gestor.remitos)


@app.route("/remitos/<id_remito>/empaquetar", methods=["POST"])
def empaquetar(id_remito):
    try:
        gestor.empaquetar_remito(id_remito)
        flash(f"Remito '{id_remito}' empaquetado. Ejemplar en preparación.", "success")
    except TransicionInvalidaError as e:
        flash(f"Error de transición State: {e}", "danger")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("remitos"))


@app.route("/remitos/<id_remito>/despachar", methods=["POST"])
def despachar(id_remito):
    try:
        gestor.despachar_remito(id_remito)
        flash(f"Remito '{id_remito}' despachado. Ejemplar en tránsito.", "info")
    except TransicionInvalidaError as e:
        flash(f"Error de transición State: {e}", "danger")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("remitos"))


@app.route("/remitos/<id_remito>/recibir", methods=["POST"])
def recibir(id_remito):
    try:
        gestor.recibir_remito(id_remito)
        flash(f"Remito '{id_remito}' recibido en sede destino. Ejemplar listo.", "success")
    except TransicionInvalidaError as e:
        flash(f"Error de transición State: {e}", "danger")
    except BibliotecaExcepcion as e:
        flash(str(e), "danger")
    return redirect(url_for("remitos"))


# -------------------------------------------------------------------------
# 7. Reportes Obligatorios No Triviales
# -------------------------------------------------------------------------
@app.route("/reportes")
def reportes():
    rep1 = gestor.reporte_prestamos_activos_y_transito()
    rep2 = gestor.reporte_prestamos_vencidos(date.today())
    rep3 = gestor.reporte_disponibilidad_por_sede()
    rep4 = gestor.reporte_libros_mas_solicitados_intersedes()

    return render_template(
        "reportes.html",
        rep1=rep1,
        rep2=rep2,
        rep3=rep3,
        rep4=rep4,
        hoy=date.today()
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
