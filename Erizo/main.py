from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db import models
from app.db import schemas
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.auth.auth import verify_token
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Access environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to authenticate student
def authenticate_student(db: Session, username: str, password: str):
    student = db.query(models.Estudiante).filter(models.Estudiante.usuario == username).first()
    if not student or not verify_password(password, student.contraseña):
        return False
    return student

# Dependency to create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Authentication route for students
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.LoginForm, db: Session = Depends(get_db)):
    student = authenticate_student(db, form_data.username, form_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.usuario}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#FastAPI routes and CRUD operations

#CRUD operations for Materia entity
# Create Materia
@app.post("/materias/", response_model=schemas.Materia)
def create_materia(materia: schemas.MateriaCreate, db: Session = Depends(get_db)):
    db_materia = models.Materia(**materia.dict())
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

# Read Materia by ID
@app.get("/materias/{materia_id}", response_model=schemas.Materia)
def read_materia(materia_id: int, db: Session = Depends(get_db)):
    db_materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    return db_materia

# Update Materia by ID
@app.put("/materias/{materia_id}", response_model=schemas.Materia)
def update_materia(materia_id: int, materia: schemas.MateriaCreate, db: Session = Depends(get_db)):
    db_materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    for key, value in materia.dict().items():
        setattr(db_materia, key, value)
    db.commit()
    db.refresh(db_materia)
    return db_materia

# Delete Materia by ID
@app.delete("/materias/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_materia(materia_id: int, db: Session = Depends(get_db)):
    db_materia = db.query(models.Materia).filter(models.Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    db.delete(db_materia)
    db.commit()
    
# CRUD operations for Estudiante entity
# Create Estudiante
@app.post("/estudiantes/", response_model=schemas.Estudiante)
def create_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    
    # Check if a student with the same ID already exists
    if db.query(models.Estudiante).filter(models.Estudiante.id == estudiante.id).first():
        raise HTTPException(status_code=400, detail="Estudiante already exists")

    
    estudiante.contraseña = pwd_context.hash(estudiante.contraseña)
    db_estudiante = models.Estudiante(**estudiante.dict())
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

# Read Estudiante by ID
@app.get("/estudiantes/{estudiante_id}", response_model=schemas.Estudiante)
def read_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    db_estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return db_estudiante

# Update Estudiante by ID
@app.put("/estudiantes/{estudiante_id}", response_model=schemas.Estudiante)
def update_estudiante(estudiante_id: int, estudiante: schemas.EstudianteUpdate, db: Session = Depends(get_db)):
    db_estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    setattr(db_estudiante, "id", estudiante_id)
    for key, value in estudiante.dict(exclude_unset=True).items():
        print(db_estudiante)
        setattr(db_estudiante, key, value)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

# Delete Estudiante by ID
@app.delete("/estudiantes/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    db_estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if db_estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    db.delete(db_estudiante)
    db.commit()
    
# CRUD operations for Inscripcion entity
# Create Inscripcion
@app.post("/inscripciones/", response_model=schemas.Inscripcion)
def create_inscripcion(inscripcion: schemas.InscripcionCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # Check if the matter exists
    materia = db.query(models.Materia).filter(models.Materia.id == inscripcion.id_materia).first()
    if not materia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The subject does not exist")

    # Check if the student exists
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == inscripcion.id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante does not exist")

    # Check if the student meets the requirements of the subject
    if materia.requisitos:
        requisitos = materia.requisitos.split(',')
        for req in requisitos:
            req_materia = db.query(models.Materia).filter(models.Materia.nombre == req).first()
            if not req_materia:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Required materia  '{req}' does not exist")
            inscripcion_previa = db.query(models.Inscripcion).filter(
                models.Inscripcion.id_estudiante == inscripcion.id_estudiante,
                models.Inscripcion.id_materia == req_materia.id,
                models.Inscripcion.estado == "APROBADO"
            ).first()
            if not inscripcion_previa:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estudiante does not meet the requirement'{req}'")

    db_inscripcion = models.Inscripcion(**inscripcion.dict())
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion

# Read Inscripcion by ID
@app.get("/inscripciones/{inscripcion_id}", response_model=schemas.Inscripcion)
def read_inscripcion(inscripcion_id: int,db: Session = Depends(get_db),token: str = Depends(verify_token)):
    inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripcion not found")
    return inscripcion

# Update Inscripcion by ID
@app.put("/inscripciones/{inscripcion_id}", response_model=schemas.Inscripcion)
def update_inscripcion(inscripcion_id: int, inscripcion: schemas.InscripcionUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not db_inscripcion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripcion not found")
    for key, value in inscripcion.dict(exclude_unset=True).items():
        setattr(db_inscripcion, key, value)
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion

# Delete Inscripcion by ID
@app.delete("/inscripciones/{inscripcion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inscripcion(inscripcion_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not db_inscripcion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripcion not found")
    db.delete(db_inscripcion)
    db.commit()
    return {"detail": "Inscripcion deleted successfully"}

# List Inscripcion Materias
def inscribir_estudiante_en_materias(estudiante_id: int, materias: list[schemas.InscripcionCreate], db: Session):
    inscripciones_creadas = []
    for materia in materias:
        inscripcion_data = materia.dict()
        inscripcion_data["id_estudiante"] = estudiante_id
        inscripcion = schemas.InscripcionCreate(**inscripcion_data)
        inscripcion_creada = create_inscripcion(inscripcion, db=db)
        inscripciones_creadas.append(inscripcion_creada)
    return inscripciones_creadas

# Route to enroll student in multiple subjects
@app.post("/inscripciones/estudiante/{estudiante_id}")
async def enroll_student_in_subjects(estudiante_id: int, materias: list[schemas.InscripcionCreate], db: Session = Depends(get_db), token: str = Depends(verify_token)):
    inscripciones = inscribir_estudiante_en_materias(estudiante_id, materias, db)
    return inscripciones

# Route to get subjects enrolled by student
@app.get("/inscripciones/estudiante/{estudiante_id}/materias", response_model=list[schemas.Materia])
async def get_enrolled_subjects_by_student(estudiante_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # Check if the student exists
    student = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get the enrolled subjects by student
    inscripciones = db.query(models.Inscripcion).filter(models.Inscripcion.id_estudiante == estudiante_id).all()
    if not inscripciones:
        raise HTTPException(status_code=404, detail="Student is not enrolled in any subjects")

    # Get the subjects details for the enrolled subjects
    materias = []
    for inscripcion in inscripciones:
        materia = db.query(models.Materia).join(models.Inscripcion).filter(models.Materia.id == inscripcion.id_materia, models.Inscripcion.estado == "INSCRITO").first()
        if materia:
            materias.append(materia)
    return materias

# Route to add grade to enrollment and automatically set state
@app.put("/inscripciones/{inscripcion_id}/nota", response_model=schemas.Inscripcion)
async def add_grade_to_enrollment(inscripcion_id: int, inscripcion: schemas.InscripcionUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    db_inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not db_inscripcion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripcion not found")
    for key, value in inscripcion.dict(exclude_unset=True).items():
        setattr(db_inscripcion, key, value)
        
    if db_inscripcion.nota < 0.0 or db_inscripcion.nota > 5.0:
        raise HTTPException(status_code=400, detail="Grade must be between 0.0 and 5.0")
    
    # Update state based on grade
    if db_inscripcion.nota >= 3.0:
        db_inscripcion.estado = "APROBADO"
    else:
        db_inscripcion.estado = "REPROBADO"
    
    db.commit()
    db.refresh(db_inscripcion)
    return db_inscripcion


# Route to get list of approved subjects and overall average score
@app.get("/estudiantes/{estudiante_id}/materias_aprobadas")
async def get_student_approved_subjects_and_average(estudiante_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    # Check if the student exists
    student = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get the enrolled subjects by student
    inscripciones = db.query(models.Inscripcion).filter(models.Inscripcion.id_estudiante == estudiante_id).all()
    if not inscripciones:
        raise HTTPException(status_code=404, detail="Student is not enrolled in any subjects")

    # Calculate overall average score for the student
    materias = []
    total_score = 0
    total_subjects = 0
    for inscripcion in inscripciones:
        materia = db.query(models.Materia).join(models.Inscripcion).filter(models.Materia.id == inscripcion.id_materia, models.Inscripcion.estado == "APROBADO").first()
        if materia:
            materias.append(materia)
            total_score += inscripcion.nota
            total_subjects += 1

    overall_average_score = total_score / total_subjects if total_subjects > 0 else 0

    return {
        "materias_aprobadas": total_subjects,
        "promedio_puntaje_general": overall_average_score
    }

# Route to get list of failed subjects for a specific student
@app.get("/estudiantes/{estudiante_id}/materias-reprobadas")
async def get_failed_subjects(estudiante_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):

    # Get list of failed subjects for the student
    failed_subjects = db.query(models.Materia).join(models.Inscripcion).filter(
        models.Inscripcion.id_estudiante == estudiante_id,
        models.Inscripcion.estado == "REPROBADO"
    ).all()

    return failed_subjects