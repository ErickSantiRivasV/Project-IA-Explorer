from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile


def create_export_package(project_data, selected_paths, context_text, destination, include_originals=True):
    root = Path(project_data["project_path"]).resolve()
    selected = set(selected_paths)
    known_files = {
        item["path"]: item
        for item in project_data["files"]
        if item["path"] in selected
    }

    if not selected:
        raise ValueError("No hay archivos seleccionados para exportar.")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    included = []

    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("contexto_proyecto.md", context_text)

        if include_originals:
            for relative_path in sorted(known_files, key=str.lower):
                safe_path = PurePosixPath(relative_path)
                if safe_path.is_absolute() or ".." in safe_path.parts:
                    raise ValueError(f"Ruta no válida dentro del proyecto: {relative_path}")

                source = root.joinpath(*safe_path.parts)
                if source.is_symlink():
                    continue
                resolved = source.resolve()
                if root not in resolved.parents or not resolved.is_file():
                    continue

                archive.write(resolved, f"archivos_proyecto/{safe_path.as_posix()}")
                included.append(relative_path)

        summary = [
            "Paquete generado por Project AI Exporter.",
            "",
            f"Proyecto: {project_data.get('project_name', 'Sin nombre')}",
            f"Archivos seleccionados: {len(selected)}",
            f"Archivos originales incluidos: {len(included)}",
            "",
            "Contenido del paquete:",
            "- contexto_proyecto.md",
            "- archivos_proyecto/: archivos originales seleccionados (si se habilitó su inclusión)",
            "",
            "El documento de contexto describe los archivos y sus contenidos legibles.",
            "Los archivos originales se conservan en su estructura relativa dentro de archivos_proyecto/."
        ]
        archive.writestr("LEEME.txt", "\n".join(summary))

    return {
        "destination": str(destination),
        "included_files": included,
        "selected_files": len(selected),
        "context_included": True
    }
