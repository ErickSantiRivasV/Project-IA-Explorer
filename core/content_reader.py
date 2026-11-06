from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".java", ".cpp", ".cc", ".c", ".h", ".hpp", ".cs",
    ".js", ".jsx", ".ts", ".tsx", ".php", ".rb", ".go", ".rs",
    ".swift", ".kt", ".dart", ".html", ".css", ".scss", ".sql",
    ".sh", ".bat", ".ps1", ".json", ".xml", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".properties", ".gradle",
    ".lock", ".md", ".txt", ".rst", ".adoc", ".csv", ".env.example",
    ".gitignore", ".gitattributes", ".editorconfig", ".dockerignore"
}

SPECIAL_TEXT_NAMES = {
    "dockerfile", "makefile", "procfile", "gemfile", "license",
    "readme", "changelog", "gitignore", "gitattributes", "editorconfig",
    ".gitignore", ".gitattributes", ".editorconfig"
}

MAX_FILE_SIZE = 1_000_000
MAX_TOTAL_SIZE = 10_000_000


def _is_text_file(path):
    name = path.name.lower()
    return path.suffix.lower() in TEXT_EXTENSIONS or name in SPECIAL_TEXT_NAMES or name.endswith(".env.example")


def _decode_content(raw):
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeError:
            continue
    return None, None


def read_selected_content(project_data, selected_paths, max_file_size=MAX_FILE_SIZE, max_total_size=MAX_TOTAL_SIZE):
    root = Path(project_data["project_path"]).resolve()
    selected = set(selected_paths)
    documents = []
    total_bytes = 0

    for file_data in project_data["files"]:
        relative_path = file_data["path"]
        if relative_path not in selected:
            continue

        original_path = root / relative_path
        item = {
            "path": relative_path,
            "status": "ok",
            "content": "",
            "size": file_data["size"],
            "lines": 0,
            "characters": 0,
            "encoding": "",
            "message": ""
        }

        try:
            if original_path.is_symlink():
                raise ValueError("No se leen enlaces simbólicos.")
            path = original_path.resolve()
            if root not in path.parents:
                raise ValueError("La ruta está fuera de la carpeta del proyecto.")
            if not path.is_file():
                raise ValueError("El elemento ya no es un archivo válido.")
            if not _is_text_file(path):
                item["status"] = "omitted"
                item["message"] = "Formato no textual; no se extrajo su contenido."
            elif path.stat().st_size > max_file_size:
                item["status"] = "limited"
                item["message"] = f"Supera el límite de {max_file_size // 1_000_000} MB por archivo."
            elif total_bytes + path.stat().st_size > max_total_size:
                item["status"] = "limited"
                item["message"] = "Se alcanzó el límite total de lectura de esta sesión."
            else:
                raw = path.read_bytes()
                if b"\x00" in raw:
                    item["status"] = "omitted"
                    item["message"] = "Se detectaron bytes nulos; se considera un archivo binario."
                else:
                    content, encoding = _decode_content(raw)
                    if content is None:
                        item["status"] = "error"
                        item["message"] = "No se pudo interpretar la codificación del archivo."
                    else:
                        item["content"] = content
                        item["encoding"] = encoding
                        item["lines"] = len(content.splitlines())
                        item["characters"] = len(content)
                        total_bytes += len(raw)
        except (OSError, ValueError) as error:
            item["status"] = "error"
            item["message"] = str(error)

        documents.append(item)

    return {
        "documents": documents,
        "total_files": len(documents),
        "read_files": sum(item["status"] == "ok" for item in documents),
        "omitted_files": sum(item["status"] == "omitted" for item in documents),
        "limited_files": sum(item["status"] == "limited" for item in documents),
        "error_files": sum(item["status"] == "error" for item in documents),
        "total_characters": sum(item["characters"] for item in documents),
        "total_lines": sum(item["lines"] for item in documents)
    }
