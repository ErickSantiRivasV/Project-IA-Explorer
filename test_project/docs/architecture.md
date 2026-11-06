# Arquitectura

- `app.py`: rutas HTTP y configuración de Flask.
- `taskflow/database.py`: persistencia SQLite y operaciones de tareas.
- `taskflow/templates/index.html`: estructura de la interfaz.
- `taskflow/static/css/styles.css`: estilos responsivos.
- `taskflow/static/js/app.js`: interacción con la API.
- `tests/test_database.py`: pruebas automatizadas de persistencia.

## Flujo principal

El navegador solicita la lista mediante `GET /api/tasks`. El servidor consulta SQLite y devuelve JSON. Las operaciones de creación, finalización y eliminación usan `POST`, `PATCH` y `DELETE` respectivamente.
