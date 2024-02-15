from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Materia(Base):
    __tablename__ = 'materias'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    creditos = Column(Integer)
    requisitos = Column(String)

class Estudiante(Base):
    __tablename__ = 'estudiantes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    estado_civil = Column(String)
    celular = Column(String)
    correo = Column(String)
    fecha = Column(String)
    usuario = Column(String)
    contraseña = Column(String)

class Inscripcion(Base):
    __tablename__ = 'inscripciones'

    id = Column(Integer, primary_key=True, index=True)
    id_materia = Column(Integer, ForeignKey('materias.id'))
    id_estudiante = Column(Integer, ForeignKey('estudiantes.id'))
    nota = Column(Float)
    estado = Column(String)
    fecha = Column(String)

    materia = relationship("Materia", back_populates="inscripciones")
    estudiante = relationship("Estudiante", back_populates="inscripciones")

Materia.inscripciones = relationship("Inscripcion", order_by=Inscripcion.id, back_populates="materia")
Estudiante.inscripciones = relationship("Inscripcion", order_by=Inscripcion.id, back_populates="estudiante")
