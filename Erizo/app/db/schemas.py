from pydantic import BaseModel
from typing import List, Optional

# Schema for Token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for login form
class LoginForm(BaseModel):
    username: str
    password: str

# Schema for Materia
class MateriaBase(BaseModel):
    nombre: str
    creditos: int
    requisitos: Optional[str] = None

class MateriaCreate(MateriaBase):
    pass

class Materia(MateriaBase):
    id: int

    class Config:
        orm_mode = True

# Schema for Estudiante
class EstudianteBase(BaseModel):
    id: int
    nombre: str
    apellido: str
    estado_civil: str
    celular: str
    correo: str
    fecha: str
    usuario: str
    contraseña: str

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteUpdate(BaseModel):
    id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    estado_civil: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    fecha: Optional[str] = None
    usuario: Optional[str] = None
    contraseña: Optional[str] = None

class Estudiante(EstudianteBase):
    id: int

    class Config:
        orm_mode = True

# Schema for Inscripcion
class InscripcionBase(BaseModel):
    id_materia: int
    id_estudiante: int
    nota: Optional[float] = None
    estado: Optional[str] = None
    fecha: Optional[str] = None

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionUpdate(BaseModel):
    id_materia: Optional[int] = None
    id_estudiante: Optional[int] = None
    nota: Optional[float] = None
    estado: Optional[str] = None
    fecha: Optional[str] = None

class Inscripcion(InscripcionBase):
    id: int

    class Config:
        orm_mode = True