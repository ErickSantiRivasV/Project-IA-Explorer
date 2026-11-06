# Project AI Exporter
# HECHO CON IA!
Aplicación de escritorio en Python y Tkinter para explorar proyectos, seleccionar archivos, analizar su estructura, extraer su contenido y preparar paquetes para compartir con herramientas de IA.

## Ejecutar

Desde esta carpeta:

```bash
python main.py
```

No requiere instalar paquetes externos: utiliza la biblioteca estándar de Python y Tkinter.

## Funciones

1. Escaneo de proyectos.
2. Exclusión preventiva de dependencias, cachés, configuraciones privadas, credenciales, claves, bases de datos locales, copias de seguridad y registros.
3. Clasificación automática.
4. Selección personalizada.
5. Inventario, estructura, lenguajes, frameworks, bases de datos, herramientas, dependencias y archivos importantes.
6. Lectura y extracción de contenido con límites por archivo y sesión.
7. Generación de contexto Markdown, vista previa, copia y guardado.
8. Exportación de paquetes ZIP con el contexto y, opcionalmente, los archivos originales seleccionados.

## Exportar un paquete ZIP

1. Selecciona la carpeta del proyecto.
2. Marca los archivos que quieras compartir.
3. Pulsa **Generar contexto**.
4. En la vista previa, deja marcada la opción **Incluir archivos originales seleccionados** si quieres adjuntar los archivos originales.
5. Pulsa **Exportar ZIP** y elige dónde guardar el paquete.

El ZIP contiene `contexto_proyecto.md`, `LEEME.txt` y, si se eligió, la carpeta `archivos_proyecto/` con los archivos seleccionados en su estructura relativa. Si desmarcas la opción, el ZIP contendrá únicamente el contexto y el archivo LEEME.

La exportación vuelve a validar las rutas y no incluye enlaces simbólicos ni archivos que hayan salido de la carpeta original. Solo se empaquetan archivos seleccionados.

## Proyecto de prueba

La carpeta `test_project` contiene TaskFlow, una aplicación web de gestión de tareas con Python, Flask, SQLite, HTML, CSS, JavaScript, SQL, documentación y pruebas.


## Exclusiones preventivas de seguridad

El escáner omite automáticamente archivos y carpetas con nombres, extensiones o ubicaciones habitualmente asociados a credenciales, claves privadas, configuraciones de proveedores cloud, bases de datos locales, copias de seguridad y registros. Se mantienen permitidos `.env.example`, `.env.sample` y `.env.template`. La detección se basa en rutas y nombres; no inspecciona el contenido para descubrir secretos escritos dentro de archivos normales. Revisa siempre la lista **Ver omitidos** y los archivos seleccionados antes de compartir un paquete.
