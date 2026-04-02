from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Credenciales root con clave vacía por ser instalación MySQL XAMPP/Local típica
DATABASE_URL = "mysql+pymysql://root:Jogerivan2002.@localhost:3306/joldens_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_session():
    return SessionLocal()
