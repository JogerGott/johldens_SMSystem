import enum
from sqlalchemy import Column, Integer, String, Enum
from src.models.base import Base

class BoxStatus(enum.Enum):
    LIBRE = "LIBRE"
    OCUPADA = "OCUPADA"
    PERDIDA = "PERDIDA"
    INACTIVA = "INACTIVA"

class BoxStateColor(enum.Enum):
    NEGRA = "negra"
    AZUL = "azul"
    ROJA = "roja"
    VERDE = "verde"
    AMARILLA = "amarilla"
    GRIS = "gris"

class Box(Base):
    __tablename__ = "boxes"

    id_box = Column(Integer, primary_key=True, index=True, autoincrement=True)
    color = Column(Enum(BoxStateColor), nullable=False)
    number = Column(Integer, nullable=False)
    status = Column(Enum(BoxStatus), nullable=False, default=BoxStatus.LIBRE)
