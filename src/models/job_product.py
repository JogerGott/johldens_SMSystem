from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class JobProduct(Base):
    __tablename__ = "job_products"

    id_job_product = Column(Integer, primary_key=True, index=True)
    id_job = Column(Integer, ForeignKey("jobs.id_job"), nullable=False)
    id_product = Column(Integer, ForeignKey("products.id_product"), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    # Guardamos el precio del producto al momento exacto de crear el JOB. 
    # Asi si en el futuro se edita el producto, las facturas viejas no se arruinan!
    historic_price = Column(Integer, nullable=False)

    # Relaciones Back
    job = relationship("Job", back_populates="products")
    product = relationship("Product")
