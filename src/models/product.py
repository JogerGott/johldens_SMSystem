from sqlalchemy import Column, Integer, String, DECIMAL, Boolean
from src.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id_product = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    # Representamos production time en días (integer)
    production_time = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
