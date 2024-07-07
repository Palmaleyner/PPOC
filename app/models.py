from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta
import string




class BaseModel:
    @staticmethod
    def crear_tablas():
        db.create_all()

class Participantes(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(500), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50))
    genero = db.Column(db.String(50))
    disponibilidad = db.Column(db.String(50), nullable=False)
    yaasignado = db.Column(db.Boolean, default=False)
    
    def set_clave(self, clave):
        self.clave = generate_password_hash(clave)

    def verificar_clave(self, clave):
        return check_password_hash(self.clave, clave)
    
    @staticmethod
    def formar_grupos():
        grupos = []
        turnos = ['Martes', 'Jueves']
        disponibilidades = {
            'Martes': ['Mañana - Schamann', 'Tarde - Arenales'],
            'Jueves': ['Mañana - Schamann', 'Tarde - Schamann']
        }
        
        hoy = datetime.today()
        mes_siguiente = hoy.replace(day=1) + timedelta(days=31)
        mes_siguiente = mes_siguiente.replace(day=1)
        fin_mes_siguiente = (mes_siguiente + timedelta(days=31)).replace(day=1)
        
        fechas_turno = {
            'Martes': [],
            'Jueves': []
        }
        
        # Generar todas las fechas de martes y jueves para el mes siguiente
        fecha = mes_siguiente
        while fecha < fin_mes_siguiente:
            if fecha.weekday() == 1:  # Martes
                fechas_turno['Martes'].append(fecha.strftime("%Y-%m-%d"))
            elif fecha.weekday() == 3:  # Jueves
                fechas_turno['Jueves'].append(fecha.strftime("%Y-%m-%d"))
            fecha += timedelta(days=1)
        
        
         # Lista de letras disponibles
        letras_disponibles = list(string.ascii_uppercase)
        
        
        # Formar grupos para cada fecha de Martes y Jueves
        for turno in turnos:
            for fecha_actual in fechas_turno[turno]:
                grupos_por_fecha = []
                for disponibilidad in disponibilidades[turno]:
                    participantes = Participantes.query.filter_by(turno=turno, disponibilidad=disponibilidad, yaasignado=0).all()
                    random.shuffle(participantes)
                    
                    grupo = []
                    masculinos_asignados = set()
                    femeninos_asignados = set()
                    
                    while len(grupo) < 3 and len(participantes) > 0:
                        participante = participantes.pop(0)
                        
                        if participante.genero == 'Masculino' and len(participante.nombre) <= 15 and len(masculinos_asignados) < 1:
                            grupo.append((participante.nombre, participante.genero, turno, disponibilidad, fecha_actual))
                            masculinos_asignados.add(participante.nombre)
                        elif participante.genero == 'Femenino' and len(femeninos_asignados) < 2:
                            grupo.append((participante.nombre, participante.genero, turno, disponibilidad, fecha_actual))
                            femeninos_asignados.add(participante.nombre)
                    
                    if len(grupo) == 3:
                        # Asignar una letra única al grupo
                        letra_asignada = letras_disponibles.pop(0)
                        grupos_por_fecha.append({
                            'grupo': grupo,
                            'disponibilidad': disponibilidad,
                            'letra': letra_asignada
                        })
                
                # Asegurar que hay exactamente un grupo de mañana y un grupo de tarde por fecha
                if len(grupos_por_fecha) == 2:
                    grupos.append({
                        'grupo': grupos_por_fecha[0]['grupo'],
                        'fecha': fecha_actual,
                        'disponibilidad': grupos_por_fecha[0]['disponibilidad'],
                        'letra': grupos_por_fecha[0]['letra']
                    })
                    grupos.append({
                        'grupo': grupos_por_fecha[1]['grupo'],
                        'fecha': fecha_actual,
                        'disponibilidad': grupos_por_fecha[1]['disponibilidad'],
                        'letra': grupos_por_fecha[1]['letra']
                    })

        # Ordenar los grupos por fecha y disponibilidad (Mañana antes que Tarde)
        grupos.sort(key=lambda x: (x['fecha'], x['disponibilidad']))

        return grupos
    
    
    

class Gestor(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    clave = db.Column('clave', db.String(500), nullable=False)  # Cambiado a _clave para evitar colisión con el método set_clave


   # def __repr__(self):
       # return f"<Gestor {self.nombre}>"
       
       
class Participames(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    turno = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    disponibilidad = db.Column(db.String(50), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    grupos = db.Column(db.String(50), nullable=False)
