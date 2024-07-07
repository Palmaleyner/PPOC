from app import app, db
from app.models import Participantes, Gestor

# Crear contexto de aplicación
with app.app_context():
    # Crear o actualizar todas las tablas al iniciar la aplicación
    Participantes.crear_tablas()
    Gestor.crear_tablas()


# Configuración para archivos estáticos
app.static_folder = 'static'


if __name__ == '__main__':
    app.run(debug=True)
