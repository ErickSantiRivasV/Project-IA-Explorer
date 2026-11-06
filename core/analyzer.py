from collections import Counter
from pathlib import PurePosixPath
from pathlib import Path
import json
import re

try:
    import tomllib
except ImportError:
    tomllib = None


TEXT_LIMIT = 1_000_000

IMPORTANT_NAMES = {
    "readme", "readme.md", "readme.txt",
    "license", "license.md", "copying",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml",
    "makefile", "procfile",
    "package.json", "requirements.txt", "pyproject.toml",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts",
    "cargo.toml", "go.mod", "composer.json", "pubspec.yaml",
    "tsconfig.json", "vite.config.js", "vite.config.ts",
    "webpack.config.js", "next.config.js", "next.config.ts",
    "angular.json", "manage.py", "main.py", "app.py",
    "server.js", "index.js", "index.ts", "program.cs",
    "main.java", "main.cpp", "main.c"
}

ENTRY_NAMES = {
    "main.py", "app.py", "manage.py", "wsgi.py", "asgi.py",
    "main.js", "main.ts", "index.js", "index.ts",
    "server.js", "main.java", "program.cs",
    "main.cpp", "main.c", "main.go", "main.rs", "main.dart"
}

MANIFEST_NAMES = {
    "package.json", "requirements.txt", "pyproject.toml",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "cargo.toml", "go.mod", "composer.json", "pubspec.yaml",
    "gemfile"
}

LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".php": "PHP",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".dart": "Dart",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bat": "Batch",
    ".ps1": "PowerShell"
}


def _read_text(root, relative_path):
    path = root / relative_path

    try:
        if path.stat().st_size > TEXT_LIMIT:
            return None

        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None


def _add_dependency(result, name, version="", source=""):
    name = str(name).strip()
    version = str(version).strip()

    if not name:
        return

    key = (name.lower(), source.lower())

    if key not in result:
        result[key] = {
            "name": name,
            "version": version,
            "source": source
        }


def _parse_requirements(content, result):
    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#") or line.startswith("-"):
            continue

        match = re.match(
            r"([A-Za-z0-9_.-]+)\s*(.*)",
            line
        )

        if match:
            _add_dependency(result, match.group(1), match.group(2), "requirements.txt")


def _parse_package_json(content, result):
    data = json.loads(content)

    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        for name, version in data.get(section, {}).items():
            _add_dependency(result, name, version, f"package.json ({section})")


def _parse_pyproject(content, result):
    if tomllib is None:
        return

    data = tomllib.loads(content)
    project = data.get("project", {})

    for dependency in project.get("dependencies", []):
        _parse_requirements(dependency, result)

    optional = project.get("optional-dependencies", {})
    for group, dependencies in optional.items():
        for dependency in dependencies:
            _parse_requirements(dependency, result)


def _parse_pom(content, result):
    import xml.etree.ElementTree as ET

    root = ET.fromstring(content)

    for dependency in root.findall(".//{*}dependency"):
        group = dependency.findtext("{*}groupId", default="")
        artifact = dependency.findtext("{*}artifactId", default="")
        version = dependency.findtext("{*}version", default="")
        name = f"{group}:{artifact}" if group else artifact
        _add_dependency(result, name, version, "pom.xml")


def _parse_gradle(content, result, source):
    pattern = re.compile(
        r"""(?:implementation|api|compileOnly|runtimeOnly|testImplementation|classpath)\s*\(?\s*['"]([^'"]+)['"]"""
    )

    for match in pattern.finditer(content):
        _add_dependency(result, match.group(1), "", source)


def _parse_go_mod(content, result):
    inside_block = False

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("require ("):
            inside_block = True
            continue

        if inside_block and line == ")":
            inside_block = False
            continue

        if line.startswith("require "):
            parts = line.split()
            if len(parts) >= 3:
                _add_dependency(result, parts[1], parts[2], "go.mod")
        elif inside_block:
            parts = line.split()
            if len(parts) >= 2 and not line.startswith("//"):
                _add_dependency(result, parts[0], parts[1], "go.mod")


def _parse_simple_manifest(filename, content, result):
    if filename == "composer.json":
        data = json.loads(content)
        for section in ("require", "require-dev"):
            for name, version in data.get(section, {}).items():
                if name != "php":
                    _add_dependency(result, name, version, f"composer.json ({section})")

    elif filename == "cargo.toml" and tomllib is not None:
        data = tomllib.loads(content)
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            for name, value in data.get(section, {}).items():
                version = value.get("version", "") if isinstance(value, dict) else value
                _add_dependency(result, name, version, f"Cargo.toml ({section})")

    elif filename == "pubspec.yaml":
        section = ""
        for line in content.splitlines():
            if line and not line.startswith(" "):
                section = line.strip().rstrip(":")
            elif section in {"dependencies", "dev_dependencies"}:
                match = re.match(r"\s{2}([A-Za-z0-9_]+)\s*:\s*(.*)", line)
                if match and match.group(1) not in {"flutter", "sdk"}:
                    _add_dependency(result, match.group(1), match.group(2), "pubspec.yaml")

    elif filename == "gemfile":
        for match in re.finditer(r"""gem\s+['"]([^'"]+)['"](?:\s*,\s*['"]([^'"]+)['"])?""", content):
            _add_dependency(result, match.group(1), match.group(2) or "", "Gemfile")


def _detect_technologies(files, manifest_contents, dependencies, source_contents):
    languages = set()
    frameworks = set()
    databases = set()
    tools = set()
    extensions = {item["extension"] for item in files}
    names = {PurePosixPath(item["path"]).name.lower() for item in files}

    for extension in extensions:
        language = LANGUAGE_BY_EXTENSION.get(extension)
        if language:
            languages.add(language)

    dependency_names = {item["name"].lower().replace("_", "-") for item in dependencies.values()}
    source = "\n".join(source_contents)
    source_lower = source.lower()

    js_frameworks = {
        "react": "React", "next": "Next.js", "vue": "Vue.js",
        "nuxt": "Nuxt", "angular": "Angular", "@angular/core": "Angular",
        "express": "Express", "svelte": "Svelte", "fastify": "Fastify",
        "koa": "Koa", "nestjs": "NestJS", "@nestjs/core": "NestJS"
    }
    python_frameworks = {
        "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
        "starlette": "Starlette", "tornado": "Tornado", "streamlit": "Streamlit",
        "dash": "Dash"
    }

    for dependency, label in {**js_frameworks, **python_frameworks}.items():
        if dependency in dependency_names:
            frameworks.add(label)

    import_patterns = {
        "Flask": r"(?:from\s+flask\s+import|import\s+flask)",
        "Django": r"(?:from\s+django\b|import\s+django\b)",
        "FastAPI": r"(?:from\s+fastapi\s+import|import\s+fastapi)",
        "React": r"(?:from\s+['\"]react['\"]|require\(['\"]react['\"]\))",
        "Vue.js": r"(?:from\s+['\"]vue['\"]|require\(['\"]vue['\"]\))",
        "Express": r"(?:from\s+['\"]express['\"]|require\(['\"]express['\"]\))"
    }
    for label, pattern in import_patterns.items():
        if re.search(pattern, source, re.IGNORECASE):
            frameworks.add(label)

    database_dependencies = {
        "sqlalchemy": "SQLAlchemy", "psycopg": "PostgreSQL",
        "psycopg2": "PostgreSQL", "psycopg2-binary": "PostgreSQL",
        "asyncpg": "PostgreSQL", "mysql-connector-python": "MySQL",
        "pymysql": "MySQL", "mysql2": "MySQL", "pg": "PostgreSQL",
        "pymongo": "MongoDB", "motor": "MongoDB", "mongoose": "MongoDB",
        "better-sqlite3": "SQLite", "sqlite3": "SQLite"
    }
    for dependency, label in database_dependencies.items():
        if dependency in dependency_names:
            databases.add(label)

    database_patterns = {
        "SQLite": r"(?:import\s+sqlite3|from\s+sqlite3\s+import|better-sqlite3)",
        "PostgreSQL": r"(?:import\s+psycopg2?\b|from\s+psycopg\b|import\s+asyncpg\b|from\s+asyncpg\b|\bpostgresql://)",
        "MySQL": r"(?:import\s+pymysql\b|from\s+pymysql\b|mysql\.connector|\bmysql://)",
        "MongoDB": r"(?:import\s+pymongo\b|from\s+pymongo\b|mongoose|mongodb://)"
    }
    for label, pattern in database_patterns.items():
        if re.search(pattern, source, re.IGNORECASE):
            databases.add(label)

    tool_dependencies = {
        "pytest": "pytest", "ruff": "Ruff", "black": "Black",
        "mypy": "Mypy", "vite": "Vite", "webpack": "Webpack",
        "typescript": "TypeScript", "eslint": "ESLint", "prettier": "Prettier",
        "jest": "Jest", "vitest": "Vitest", "playwright": "Playwright",
        "cypress": "Cypress", "nodemon": "Nodemon"
    }
    for dependency, label in tool_dependencies.items():
        if dependency in dependency_names:
            tools.add(label)

    if "dockerfile" in names or any(name in names for name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}):
        tools.add("Docker")
    if any(name.startswith("vite.config.") for name in names):
        tools.add("Vite")
    if any(name.startswith("next.config.") for name in names):
        frameworks.add("Next.js")
    if "angular.json" in names:
        frameworks.add("Angular")
    if "manage.py" in names:
        frameworks.add("Django")
    if any("pytest" in PurePosixPath(item["path"]).parts for item in files) or any(part.lower() == "tests" for item in files for part in PurePosixPath(item["path"]).parts):
        tools.add("Pruebas automatizadas")

    return {
        "languages": sorted(languages, key=str.lower),
        "frameworks": sorted(frameworks, key=str.lower),
        "databases": sorted(databases, key=str.lower),
        "tools": sorted(tools, key=str.lower)
    }


def _build_structure(files):
    tree = {}

    for file in files:
        parts = PurePosixPath(file["path"]).parts
        current = tree

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current.setdefault("__files__", []).append(parts[-1])

    lines = []

    def walk(node, prefix=""):
        entries = []

        for name, child in node.items():
            if name == "__files__":
                continue
            entries.append((name, child, True))

        for filename in node.get("__files__", []):
            entries.append((filename, None, False))

        entries.sort(key=lambda item: (not item[2], item[0].lower()))

        for index, (name, child, is_directory) in enumerate(entries):
            last = index == len(entries) - 1
            connector = "└── " if last else "├── "
            suffix = "/" if is_directory else ""
            lines.append(prefix + connector + name + suffix)

            if is_directory:
                walk(child, prefix + ("    " if last else "│   "))

    walk(tree)
    return "\n".join(lines) if lines else "(No hay archivos seleccionados)"


def analyze_project(project_data, selected_paths):
    root = Path(project_data["project_path"])
    selected_set = set(selected_paths)
    files = [
        file for file in project_data["files"]
        if file["path"] in selected_set
    ]

    extension_counts = Counter(
        file["extension"] or "Sin extensión"
        for file in files
    )
    category_counts = Counter(file["category"] for file in files)
    total_size = sum(file["size"] for file in files)

    manifest_contents = {}
    dependencies = {}
    source_contents = []

    for file in files:
        filename = PurePosixPath(file["path"]).name.lower()

        if filename not in MANIFEST_NAMES:
            continue

        content = _read_text(root, file["path"])

        if content is None:
            continue

        manifest_contents[filename] = content

        try:
            if filename == "package.json":
                _parse_package_json(content, dependencies)
            elif filename == "requirements.txt":
                _parse_requirements(content, dependencies)
            elif filename == "pyproject.toml":
                _parse_pyproject(content, dependencies)
            elif filename == "pom.xml":
                _parse_pom(content, dependencies)
            elif filename in {"build.gradle", "build.gradle.kts"}:
                _parse_gradle(content, dependencies, filename)
            elif filename == "go.mod":
                _parse_go_mod(content, dependencies)
            else:
                _parse_simple_manifest(filename, content, dependencies)
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        except Exception:
            continue

    for file in files:
        if file["extension"] in LANGUAGE_BY_EXTENSION:
            content = _read_text(root, file["path"])
            if content is not None:
                source_contents.append(content)

    technology_groups = _detect_technologies(
        files, manifest_contents, dependencies, source_contents
    )
    technologies = sorted(
        {item for group in technology_groups.values() for item in group},
        key=str.lower
    )

    important_files = []
    entry_points = []

    for file in files:
        name = PurePosixPath(file["path"]).name.lower()

        if name in IMPORTANT_NAMES or name.startswith("readme.") or name.startswith("license."):
            important_files.append(file["path"])

        if name in ENTRY_NAMES:
            entry_points.append(file["path"])

    return {
        "total_files": len(files),
        "total_directories": len({
            str(PurePosixPath(file["path"]).parent)
            for file in files
            if str(PurePosixPath(file["path"]).parent) != "."
        }),
        "total_size": total_size,
        "extensions": sorted(extension_counts.items(), key=lambda item: (-item[1], item[0].lower())),
        "categories": sorted(category_counts.items(), key=lambda item: (-item[1], item[0].lower())),
        "structure": _build_structure(files),
        "technologies": technologies,
        "technology_groups": technology_groups,
        "dependencies": sorted(
            dependencies.values(),
            key=lambda item: (item["name"].lower(), item["source"].lower())
        ),
        "manifests": sorted(manifest_contents),
        "important_files": sorted(set(important_files), key=str.lower),
        "entry_points": sorted(set(entry_points), key=str.lower)
    }
