# Sistema de Calificación de Notas para una Universidad

Este sistema es una API desarrollada en Python utilizando FastAPI para la gestión de calificaciones de estudiantes en una universidad. Proporciona funcionalidades para la gestión de materias, estudiantes e inscripciones.

## Estructura de la Base de Datos

El sistema utiliza una base de datos relacional para almacenar la información. La estructura de la base de datos incluye las siguientes entidades:

### Materia:
- **id:** Identificador único de la materia.
- **nombre:** Nombre de la materia.
- **creditos:** Número de créditos asociados a la materia.
- **requisitos:** Lista de materias que son requisitos para inscribirse en esta materia.

### Estudiante:
- **id:** Identificador único del estudiante.
- **nombre:** Nombre del estudiante.
- **apellido:** Apellido del estudiante.
- **estado_civil:** Estado civil del estudiante.
- **celular:** Número de teléfono celular del estudiante.
- **correo:** Correo electrónico del estudiante.
- **fecha:** Fecha de registro del estudiante.
- **usuario:** Nombre de usuario del estudiante.
- **contraseña:** Contraseña del estudiante (se recomienda su almacenamiento seguro y encriptado).

### Inscripción:
- **id:** Identificador único de la inscripción.
- **id_materia:** Clave foránea que hace referencia al identificador de la materia inscrita.
- **id_estudiante:** Clave foránea que hace referencia al identificador del estudiante inscrito.
- **nota:** Nota obtenida por el estudiante en la materia (los valores deben estar entre 0.0 y 5.0).
- **estado:** Estado de la inscripción (INSCRITO, REPROBADO, APROBADO, CANCELADO).
- **fecha:** Fecha de registro de la inscripción.

## Funcionalidades Principales

El sistema proporciona las siguientes funcionalidades principales:

- Registro y gestión de materias, estudiantes e inscripciones.
- Autenticación de estudiantes y generación de tokens de acceso.
- CRUD (Crear, Leer, Actualizar, Eliminar) para materias, estudiantes e inscrpciones.
- Ingreso de notas y actualización de estado de inscripción.
- Obtención de listas de inscripciones según diversos criterios

## Requisitos de Instalación

- Python 3.x
- Instalar dependencias del proyecto con `pip install -r requirements.txt`

## Uso

1. Ejecutar la aplicación con `uvicorn main:app --reload`.
2. Acceder a la documentación interactiva en `http://localhost:8000/docs` para probar las API endpoints.
3. Para autorizar las solicitudes, debe proporcionar un token de acceso válido en el encabezado de autorización (`Authorization: Bearer {token}`).

## Autor

[KEVIN HERRERA]

