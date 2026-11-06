
from pathlib import Path
import os
from core.exclusions import (
    get_directory_exclusion_reason,
    get_file_exclusion_reason
)
from core.classifier import classify_file


def scan_project(project_path):
    root = Path(project_path)

    if not root.exists() or not root.is_dir():
        raise ValueError("La ruta seleccionada no es una carpeta válida.")

    files = []
    directories = []
    excluded = []
    errors = []

    def handle_error(error):
        errors.append({
            "path": str(error.filename or root),
            "message": str(error)
        })

    for current_path, dirnames, filenames in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=handle_error
    ):
        current = Path(current_path)

        retained_directories = []

        for name in dirnames:
            directory_path = current / name

            if directory_path.is_symlink():
                continue

            relative_directory = directory_path.relative_to(root).as_posix()
            reason = get_directory_exclusion_reason(name, relative_directory)

            if reason:
                excluded.append({
                    "path": directory_path.relative_to(root).as_posix(),
                    "type": "Carpeta",
                    "reason": reason
                })
            else:
                retained_directories.append(name)

        dirnames[:] = retained_directories

        if current != root:
            directories.append(
                current.relative_to(root).as_posix()
            )

        for filename in filenames:
            file_path = current / filename

            if file_path.is_symlink():
                continue

            reason = get_file_exclusion_reason(filename)

            if reason:
                excluded.append({
                    "path": file_path.relative_to(root).as_posix(),
                    "type": "Archivo",
                    "reason": reason
                })
                continue

            try:
                relative_path = file_path.relative_to(root).as_posix()
                size = file_path.stat().st_size

                files.append({
                    "name": filename,
                    "path": relative_path,
                    "extension": file_path.suffix.lower(),
                    "category": classify_file(filename),
                    "size": size
                })

            except OSError as error:
                errors.append({
                    "path": str(file_path),
                    "message": str(error)
                })

    files.sort(key=lambda item: item["path"].lower())
    directories.sort(key=str.lower)
    excluded.sort(key=lambda item: item["path"].lower())

    categories = {}

    for file in files:
        category = file["category"]
        categories[category] = categories.get(category, 0) + 1

    return {
        "project_name": root.name,
        "project_path": str(root.resolve()),
        "files": files,
        "directories": directories,
        "excluded": excluded,
        "errors": errors,
        "categories": categories,
        "total_files": len(files),
        "total_directories": len(directories),
        "total_excluded": len(excluded),
        "total_size": sum(file["size"] for file in files)
    }
