from pathlib import Path
import re

DIRECTORY_NAMES = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "bower_components",
    "vendor",
    ".npm",
    ".yarn",
    ".pnpm-store",
    ".bundle",
    ".cache",
    "site-packages",
    "__pypackages__",
    ".m2",
    ".ivy2",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".next",
    ".nuxt",
    ".angular",
    "dist",
    "build",
    "coverage",
    "target",
    ".gradle",
    ".terraform",
    "pods",
    ".dart_tool",
    "flutter_build",
    ".ssh",
    ".aws",
    ".azure",
    ".gcloud",
    ".kube",
    ".docker",
    ".vagrant",
    ".pulumi",
    ".vault",
    ".gnupg",
}

SAFE_ENV_FILES = {
    ".env.example",
    ".env.sample",
    ".env.template",
}

SENSITIVE_DIRECTORY_PATHS = {
    ".config/gcloud",
    ".config/gh",
    ".config/containers",
    ".config/1password",
    ".config/bitwarden",
    ".cargo/credentials",
    ".docker/buildx"
}

SENSITIVE_FILE_NAMES = {
    "credentials",
    "credentials.json",
    "credentials.yaml",
    "credentials.yml",
    "secrets",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "service-account.json",
    "serviceaccount.json",
    "google-credentials.json",
    "firebase-adminsdk.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    "id_xmss",
    "known_hosts",
    ".bash_history",
    ".zsh_history",
    ".python_history",
    ".envrc",
    "authorized_keys",
    "authorized_keys2",
    "config.json.enc",
    ".npmrc",
    ".pypirc",
    ".netrc",
    ".git-credentials",
    ".htpasswd",
    "auth.json",
    "token.json",
    "kubeconfig",
    "terraform.tfstate",
    "terraform.tfstate.backup",
    "pulumi.yaml.bak",
    "application_default_credentials.json",
    "client_secret.json",
    "client_secrets.json",
    "id_token.json",
    "refresh_token.json",
    "access_token.json"
}

SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".p7b",
    ".p7c",
    ".jks",
    ".keystore",
    ".ppk",
    ".kdbx",
    ".asc",
    ".gpg",
    ".pgp",
    ".sqlite",
    ".sqlite3",
    ".sqlite-wal",
    ".sqlite-shm",
    ".db-wal",
    ".db-shm",
    ".db",
    ".mdb",
    ".accdb",
    ".bak",
    ".backup",
    ".dump",
    ".dmp",
    ".rdb",
    ".tfstate"
}

SENSITIVE_NAME_PATTERN = re.compile(
    r"(^|[._-])(secret|secrets|credential|credentials|password|passwd|token|tokens|apikey|api_key|private_key|privkey|service[-_]account|id_(rsa|ed25519|ecdsa|dsa|xmss))([._-]|$)"
)

BACKUP_NAME_PATTERN = re.compile(r"(^|[._-])(backup|backups|dump|dumps)([._-]|$)")

SENSITIVE_SUFFIXES = (
    ".tfstate.backup",
    ".tfstate.backup~",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.staging"
)


def get_directory_exclusion_reason(directory_name, relative_path=None):
    normalized = directory_name.lower().replace("\\", "/").strip("/")
    normalized_path = (relative_path or directory_name).lower().replace("\\", "/").strip("/")

    if normalized_path in SENSITIVE_DIRECTORY_PATHS:
        return "Carpeta de configuración privada o credenciales de una herramienta."

    if normalized in DIRECTORY_NAMES:
        return "Carpeta de dependencias, archivos generados, caché o configuración privada."

    if normalized.rsplit("/", 1)[-1] in {"secrets", "secret", "credentials", "credential"}:
        return "Carpeta destinada a credenciales o información sensible."

    return None


def get_file_exclusion_reason(filename):
    name = filename.lower()

    if name in SAFE_ENV_FILES:
        return None

    if name == ".env" or name.startswith(".env."):
        return "Archivo de variables de entorno; puede contener credenciales."

    if name in SENSITIVE_FILE_NAMES:
        return "Nombre asociado a credenciales, claves o configuración privada."

    if SENSITIVE_NAME_PATTERN.search(name):
        return "El nombre del archivo indica que podría contener secretos o credenciales."

    if any(name.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return "Archivo de configuración o estado que puede contener información sensible."

    extension = Path(name).suffix.lower()

    if extension in SENSITIVE_EXTENSIONS:
        return "Archivo de clave, certificado, base de datos o copia de seguridad que puede contener información privada."

    if BACKUP_NAME_PATTERN.search(name) and extension in {".sql", ".gz", ".zip", ".7z", ".tar", ".dmp", ".dump"}:
        return "Posible copia de seguridad o volcado de datos."

    if name.endswith(".log") or ".log." in name:
        return "Archivo de registro que podría contener tokens, rutas o datos privados."

    if name in {".ds_store", "thumbs.db"}:
        return "Archivo auxiliar del sistema operativo."

    return None
