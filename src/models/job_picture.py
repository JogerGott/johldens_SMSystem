from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class JobPicture(Base):
    __tablename__ = "job_pictures"

    id_job_picture = Column(Integer, primary_key=True, index=True)
    id_job = Column(Integer, ForeignKey("jobs.id_job"), nullable=False)
    
    # Path local/en red donde la imagen esta guardada para no sobrecargar la bd
    file_path = Column(String(255), nullable=False) 
    
    job = relationship("Job", back_populates="pictures")
