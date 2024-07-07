from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, make_response, jsonify
from app import app, db
from app.models import Participantes, Gestor, Participames
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import  datetime, timezone
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import json
import pdfkit








# Lista de letras con números 1 y 2
letras = [f'{letra}{numero}' for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for numero in range(1, 3)]

# Diccionario para controlar las selecciones por letra
selecciones = {letra: 0 for letra in letras}

# Diccionario para controlar las selecciones totales por letra en toda la tabla
selecciones_totales = {letra: 0 for letra in letras}



@app.route('/seleccionar_letra', methods=['POST'])
def seleccionar_letra():
    letra_seleccionada = request.form['letra']
    letra_original = request.form.get('original')

    if selecciones_totales.get(letra_seleccionada, 0) < 3:
        if letra_original and letra_original in selecciones_totales:
            selecciones_totales[letra_original] -= 1

        selecciones_totales[letra_seleccionada] = selecciones_totales.get(letra_seleccionada, 0) + 1
        selecciones[letra_seleccionada] = selecciones.get(letra_seleccionada, 0) + 1
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Ya se a seleccionado esta letra tres veces en total.'})


@app.route('/actualizar_contador', methods=['POST'])
def actualizar_contador():
    letra = request.form.get('letra')
    cambio = int(request.form.get('cambio', 0))

    if letra:
        if letra in selecciones_totales:
            selecciones_totales[letra] += cambio
        else:
            selecciones_totales[letra] = cambio
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Error: letra no especificada.'})





def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('iniciosession'))
        return f(*args, **kwargs)
    return decorated_function




def verificar_credenciales(nombre, clave):
    usuario_db = Gestor.query.filter_by(nombre=nombre).first()
    if usuario_db:
        if check_password_hash(usuario_db.clave, clave):
            return usuario_db
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
       
    return render_template('iniciosession.html')




@app.route('/iniciosession', methods=['GET', 'POST'])
def iniciosession():
    if request.method == 'POST':
        nombre = request.form['nombreadmin']
        clave = request.form['claveadmin']
        
        user = verificar_credenciales(nombre, clave)
        if user:
            session['user_id'] = user.id
            return redirect(url_for('visualgestor'))
        else:
            flash('Invalid username or password.')
        
    return render_template('iniciosession.html')

@app.route('/exit')
def exit():
    session.pop('user_id', None)
    return redirect(url_for('iniciosession'))


@app.before_request
def before_request():
    if 'user_id' in session:
        last_active = session.get('last_active')
        if last_active and datetime.now(timezone.utc) > last_active + app.config['PERMANENT_SESSION_LIFETIME']:
            # Si ha pasado el tiempo de vida de la sesión, eliminar la sesión y redirigir al inicio de sesión
            session.pop('user_id')
            flash('Tu sesión ha expirado debido a inactividad.', 'info')
            return redirect(url_for('iniciosession'))
    # Actualizar el tiempo de última actividad en cada solicitud
    session['last_active'] = datetime.now(timezone.utc)


@app.route('/visualgestor', methods=['GET', 'POST'])
@login_required
def visualgestor():
    if request.method == 'POST':
        termino_busqueda = request.form.get('busqueda', '')
        if termino_busqueda:
            participantes = Participantes.query.filter(
                (Participantes.usuario.like(f'%{termino_busqueda}%')) | 
                (Participantes.nombre.like(f'%{termino_busqueda}%'))
            ).all()
        else:
            participantes = Participantes.query.all()
        return render_template('visualgestor.html', participantes=participantes)
    gestores = Gestor.query.all()
    participantes = Participantes.query.all()
    return render_template('visualgestor.html', participantes=participantes, gestores=gestores)



@app.route('/listaparticipantes', methods=['GET', 'POST'])
@login_required
def listaparticipantes():
    if request.method == 'POST':
        # Reiniciar los contadores de selecciones y selecciones totales
        global selecciones, selecciones_totales
        selecciones = {letra: 0 for letra in letras}
        selecciones_totales = {letra: 0 for letra in letras}
        
        grupos = Participantes.formar_grupos()
        return render_template('listaparticipantes.html', grupos=grupos, letras=letras, selecciones=selecciones, selecciones_totales=selecciones_totales)
    
    return render_template('listaparticipantes.html',letras=letras, selecciones=selecciones, selecciones_totales=selecciones_totales)




@app.route('/delete_gestor/<int:id>', methods=['POST'])
@login_required
def delete_gestor(id):
    #print(id)
    gestor = Gestor.query.get_or_404(id)
    
    db.session.delete(gestor)
    db.session.commit()
    return redirect(url_for('visualgestor'))


@app.route('/agregar_gestor', methods=['POST'])
@login_required
def agregar_gestor():
    nombre = request.form['nombreadmin']
    clave = request.form['claveadmin']
    clave_hasheada = generate_password_hash(clave)
    print(clave_hasheada)
    nuevo_usuario = Gestor(nombre=nombre, clave=clave_hasheada)
    db.session.add(nuevo_usuario)
    db.session.commit()
    flash(f'Usuario creado correctamente', 'success')
    return redirect(url_for('visualgestor'))


@app.route('/agregar_participante', methods=['POST'])
@login_required
def agregar_participante():
    usuario = request.form['usuario']
    clave = usuario
    nombre = request.form['nombre']
    turno = request.form['turno']
    genero = request.form['genero']
    disponibilidad = request.form['disponibilidad']
    yaasignado = bool(request.form.get('yaasignado'))

    nuevo_participante = Participantes(usuario=usuario, nombre=nombre, turno=turno, genero=genero,
                                        disponibilidad=disponibilidad, yaasignado=yaasignado)
    nuevo_participante.set_clave(clave)
    db.session.add(nuevo_participante)
    db.session.commit()
    return redirect(url_for('visualgestor'))

@app.route('/editar_participante/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_participante(id):
    participante = Participantes.query.get_or_404(id)
    if request.method == 'POST':
        participante.usuario = request.form['usuario']
        participante.nombre = request.form['nombre']
        participante.turno = request.form['turno']
        participante.genero = request.form['genero']
        participante.disponibilidad = request.form['disponibilidad']
        participante.yaasignado = bool(request.form.get('yaasignado'))
        
        nueva_clave = request.form['nombre']
        if nueva_clave:
            participante.set_clave(nueva_clave)
        
        db.session.commit()
        return redirect(url_for('visualgestor'))
    return render_template('editar_participante.html', participante=participante)

@app.route('/eliminar_participante/<int:id>', methods=['POST'])
@login_required
def eliminar_participante(id):
    participante = Participantes.query.get_or_404(id)
    db.session.delete(participante)
    db.session.commit()
    return redirect(url_for('visualgestor'))



@app.route('/descargarPDFGene', methods=['GET', 'POST'])
@login_required
def descargarPDFGene():
    participantes = Participantes.query.all()

    # Crear la lista de datos para la tabla
    data = [["usuario","nombre", "turno", "disponibilidad","yaasignado"]]  # Encabezados
    for participante in participantes:
        data.append([participante.usuario, participante.nombre, participante.turno, participante.disponibilidad, participante.yaasignado])

    # Crear el PDF
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    table = Table(data)

    # Estilos de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    elements = [table]

    # Construir el PDF
    pdf.build(elements)

    # Descargar el PDF
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf', headers={
        'Content-Disposition': 'attachment;filename=participantes.pdf'
    })
    

@app.route('/descargarPDFlista', methods=['GET', 'POST'])
@login_required
def descargarPDFlista():
    data = json.loads(request.data)

    # Crear el PDF
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    table_data = [["Turno", "Fecha", "Nombre", "Genero", "Disponibilidad"]]  # Encabezados
    table_data.extend(data)
    table = Table(table_data)

    # Estilos de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    elements = [table]

    # Construir el PDF
    pdf.build(elements)

    # Descargar el PDF
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=participantes.pdf'
        
    return response



@app.route('/guardar_registro', methods=['POST'])
@login_required
def guardar_registro():
    if request.method == 'POST':
        participantemes_data = request.form
        
        turnos = participantemes_data.getlist('turno[]')
        fechas = participantemes_data.getlist('fecha[]')
        nombres = participantemes_data.getlist('nombre[]')
        generos = participantemes_data.getlist('genero[]')
        disponibilidades = participantemes_data.getlist('disponibilidad[]')
        grupos = participantemes_data.getlist('grupo[]')

        for turno, fecha, nombre, genero, disponibilidad, grupos in zip(turnos, fechas, nombres, generos, disponibilidades, grupos):
            participames = Participames(turno=turno, fecha=fecha, nombre=nombre, genero=genero, disponibilidad=disponibilidad, grupos=grupos)
            db.session.add(participames)
        
        db.session.commit()
        flash('Datos guardados exitosamente.', 'success')
    
    return redirect(url_for('listaparticipantes'))
        


@app.route('/eliminar_todo_participames', methods=['POST'])
@login_required
def eliminar_todo_participames():
    try:
        num_rows_deleted = db.session.query(Participames).delete()
        db.session.commit()
        flash(f'Se han eliminado {num_rows_deleted} registros de la tabla Participames.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar los registros: {str(e)}', 'danger')
    return redirect(url_for('listaparticipantes'))
        



# Ruta para cambiar el tema
@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    if app.config['THEME'] == 'light':
        app.config['THEME'] = 'dark'
    else:
        app.config['THEME'] = 'light'
    
    return '', 204  # Respuesta sin contenido

# Context processor para pasar el tema a las plantillas
@app.context_processor
def inject_theme():
    return {'theme': app.config['THEME']}
