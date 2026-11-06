
from pathlib import Path


FILE_CATEGORIES = {
    "Código fuente": {
        ".py", ".java", ".cpp", ".c", ".h", ".hpp",
        ".cs", ".js", ".jsx", ".ts", ".tsx", ".php",
        ".rb", ".go", ".rs", ".swift", ".kt", ".dart",
        ".html", ".css", ".sql", ".sh", ".bat", ".ps1"
    },

    "Configuración": {
        ".json", ".xml", ".yaml", ".yml", ".toml",
        ".ini", ".cfg", ".conf", ".properties",
        ".env", ".gradle", ".lock"
    },

    "Documentación": {
        ".md", ".txt", ".pdf", ".doc", ".docx",
        ".rst", ".adoc"
    },

    "Imágenes": {
        ".png", ".jpg", ".jpeg", ".gif", ".svg",
        ".webp", ".bmp", ".ico", ".tiff"
    },

    "Multimedia": {
        ".mp3", ".wav", ".ogg", ".mp4", ".avi",
        ".mov", ".mkv", ".webm"
    },

    "Datos": {
        ".csv", ".xlsx", ".xls", ".db", ".sqlite",
        ".parquet"
    },

    "Archivos comprimidos": {
        ".zip", ".rar", ".7z", ".tar", ".gz"
    }
}


SPECIAL_FILENAMES = {
    "dockerfile": "Configuración",
    "makefile": "Configuración",
    "procfile": "Configuración",
    "license": "Documentación",
    "readme": "Documentación",
    "changelog": "Documentación",
    "gitignore": "Configuración",
    "gitattributes": "Configuración",
    "editorconfig": "Configuración"
}


def classify_file(filename):
    name = filename.lower()
    special_name = name.lstrip(".")
    extension = Path(name).suffix.lower()

    if name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[name]

    if special_name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[special_name]

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Otros"
