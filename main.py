import sys
from sqlalchemy.exc import OperationalError
from src.database.session import engine, DATABASE_URL
from src.models.base import Base
# Importar todos los modelos asegura que metadata los registrue para create_all()
from src.models import *

from src.ui.main_window import start_app

def init_db():
    try:
        print(f"Buscando base de datos en {DATABASE_URL}...")
        # Genera las tablas en MySQL si no existen (Basado en los modelos de código)
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Todas las tablas han sido verificadas / creadas en MySQL.")
    except OperationalError as e:
        print(f"[ERROR CONEXION] No se pudo conectar a la base de datos.")
        print("Por favor verifica que tu servidor MySQL esté encendido y las credenciales (root/root) sean correctas.")
        print("Detalle del error:", e)
        # Si estas en entorno de desarollo, podrías cambiar el DATABASE_URL en session.py por sqlite:///database.db
        sys.exit(1)

if __name__ == "__main__":
    init_db()
    
    print("[UI] Encendiendo Intefaz Grafica PyQt6...")
    start_app()
