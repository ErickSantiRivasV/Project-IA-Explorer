from pathlib import PurePosixPath

LANGUAGE_BY_EXTENSION = {
    ".py": "python", ".js": "javascript", ".jsx": "jsx", ".ts": "typescript",
    ".tsx": "tsx", ".html": "html", ".css": "css", ".scss": "scss",
    ".sql": "sql", ".java": "java", ".cpp": "cpp", ".cc": "cpp",
    ".c": "c", ".h": "c", ".hpp": "cpp", ".cs": "csharp",
    ".php": "php", ".rb": "ruby", ".go": "go", ".rs": "rust",
    ".json": "json", ".xml": "xml", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".ini": "ini", ".md": "markdown", ".sh": "bash",
    ".ps1": "powershell", ".bat": "bat", ".txt": "text", ".env.example": "dotenv"
}


def _format_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024


def _code_fence(content):
    longest = max((len(part) for part in content.split("```")), default=0)
    longest_run = 0
    current = 0
    for character in content:
        if character == "`":
            current += 1
            longest_run = max(longest_run, current)
        else:
            current = 0
    return "`" * max(3, longest_run + 1)


def build_project_context(project_data, analysis, content_result):
    project_name = project_data.get("project_name", "Proyecto sin nombre")
    selected_documents = content_result.get("documents", [])
    lines = [
        f"# Contexto del proyecto: {project_name}",
        "",
        "> Documento generado por Project AI Exporter. Contiene únicamente los archivos seleccionados y cuyo contenido pudo leerse dentro de los límites establecidos.",
        "",
        "## 1. Resumen del proyecto",
        "",
        f"- **Nombre:** {project_name}",
        f"- **Archivos seleccionados:** {analysis['total_files']}",
        f"- **Carpetas representadas:** {analysis['total_directories']}",
        f"- **Tamaño de los archivos seleccionados:** {_format_size(analysis['total_size'])}",
        f"- **Archivos leídos:** {content_result['read_files']}",
        f"- **Archivos omitidos:** {content_result['omitted_files']}",
        f"- **Archivos limitados:** {content_result['limited_files']}",
        f"- **Errores de lectura:** {content_result['error_files']}",
        "",
        "## 2. Estructura seleccionada",
        "",
        "```text",
        analysis["structure"],
        "```",
        "",
        "## 3. Tecnologías detectadas",
        ""
    ]

    group_labels = {
        "languages": "Lenguajes",
        "frameworks": "Frameworks",
        "databases": "Bases de datos",
        "tools": "Herramientas"
    }

    for key, label in group_labels.items():
        values = analysis["technology_groups"].get(key, [])
        lines.append(f"### {label}")
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- No se detectaron elementos.")
        lines.append("")

    lines.extend(["## 4. Dependencias", ""])
    if analysis["dependencies"]:
        for dependency in analysis["dependencies"]:
            version = dependency["version"] or "Versión no especificada"
            lines.append(f"- **{dependency['name']}** — {version} — {dependency['source']}")
    else:
        lines.append("No se encontraron dependencias reconocibles en los manifiestos seleccionados.")

    lines.extend(["", "### Manifiestos detectados", ""])
    if analysis["manifests"]:
        lines.extend(f"- `{name}`" for name in analysis["manifests"])
    else:
        lines.append("No se detectaron manifiestos seleccionados.")

    lines.extend(["", "## 5. Archivos importantes", "", "### Posibles puntos de entrada", ""])
    lines.extend(f"- `{path}`" for path in analysis["entry_points"])
    if not analysis["entry_points"]:
        lines.append("No se detectaron puntos de entrada conocidos.")

    lines.extend(["", "### Otros archivos importantes", ""])
    entry_point_set = set(analysis["entry_points"])
    other_important_files = [path for path in analysis["important_files"] if path not in entry_point_set]
    lines.extend(f"- `{path}`" for path in other_important_files)
    if not other_important_files:
        lines.append("No se detectaron otros archivos importantes conocidos.")

    lines.extend(["", "## 6. Contenido de los archivos", ""])
    for document in selected_documents:
        path = document["path"]
        lines.extend([f"### `{path}`", ""])
        if document["status"] == "ok":
            extension = PurePosixPath(path).suffix.lower()
            language = LANGUAGE_BY_EXTENSION.get(extension, "")
            if path.lower().endswith(".env.example"):
                language = "dotenv"
            fence = _code_fence(document["content"])
            lines.extend([
                f"Codificación: {document['encoding']} | Líneas: {document['lines']} | Caracteres: {document['characters']}",
                "",
                f"{fence}{language}",
                document["content"].rstrip("\n"),
                fence,
                ""
            ])
        else:
            lines.extend([
                f"**Contenido no incluido:** {document['message']}",
                ""
            ])

    lines.extend([
        "## 7. Observaciones para la IA",
        "",
        "- La estructura y el contenido corresponden a los archivos seleccionados al generar este documento.",
        "- Los archivos omitidos, limitados o con errores no tienen su contenido incluido.",
        "- Las tecnologías y los puntos de entrada son detecciones automáticas y pueden requerir confirmación.",
        "- No asumas que los archivos no incluidos no existen en el proyecto original.",
        ""
    ])

    return "\n".join(lines)
