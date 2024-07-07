from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from app import app
from app.models import Participantes, Participames
from datetime import datetime
from functools import wraps
from werkzeug.security import check_password_hash





def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'parti_id' not in session:
            return redirect(url_for('iniciosession'))
        return f(*args, **kwargs)
    return decorated_function



def verificar_credenciales_parti(userPhone, claveparti):
    parti_db = Participantes.query.filter_by(usuario=userPhone).first()
    if parti_db:
        if check_password_hash(parti_db.clave, claveparti):
            return parti_db
    return None



@app.route('/iniciosessionparticipante', methods=['GET', 'POST'])
def iniciosessionparticipante():
    if request.method == 'POST':
        nombre = request.form['userPhone']
        clave = request.form['userPhone']
        
        parti = verificar_credenciales_parti(nombre, clave)
        if parti:
            session['parti_id'] = parti.id
            return redirect(url_for('participantesmes'))
        else:
            flash('Usuario o clave incorrecto.', 'error')
        
    return render_template('iniciosession.html')

@app.route('/exitparticipante')
def exitparticipante():
    session.pop('parti_id', None)
    return redirect(url_for('iniciosessionparticipante'))


@app.route('/participantesmes', methods=['GET', 'POST'])
@login_required
def participantesmes():
    participantes = Participantes.query.all()
    participames = Participames.query.all()
    calendario = obtener_calendario_mes(participames)# Modificamos para obtener los participantes de Participames
    return render_template('participantesmes.html', participames=participames, 
                           participantes=participantes, calendario=calendario)
      



def obtener_calendario_mes(participames):
    calendario = {'Martes': {'Mañana - Schamann': [], 'Tarde - Schamann': [], 'Tarde - Arenales': []},
                  'Jueves': {'Mañana - Schamann': [], 'Tarde - Schamann': [], 'Tarde - Arenales': []}}

    for participante in participames:
        fecha = datetime.strptime(participante.fecha, "%Y-%m-%d")
        dia_semana = fecha.strftime('%A')

        if dia_semana in calendario:
            disponibilidad = participante.disponibilidad
            if disponibilidad in calendario[dia_semana]:
                calendario[dia_semana][disponibilidad].append({
                    'nombre': participante.nombre,
                    'genero': participante.genero,
                    'disponibilidad': participante.disponibilidad
                })

    return calendario
