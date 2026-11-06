# TaskFlow Demo

TaskFlow es una pequeña aplicación web para crear, consultar, completar y eliminar tareas. Está construida con Python, Flask, SQLite, HTML, CSS y JavaScript.

## Requisitos

- Python 3.10 o superior.
- pip.

## Instalación

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\activate
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Abre `http://127.0.0.1:5000` en el navegador.

## Ejecutar pruebas

```bash
python -m unittest discover -s tests -v
```

La base de datos SQLite se crea automáticamente. Para cambiar su ubicación, define `DATABASE_PATH` en el entorno.
