"""
downloader.py — Baixa binários (apktool, uber-apk-signer, zipalign)
via GitHub Releases quando ausentes no sistema.

Nenhuma telemetria; apenas requisições HTTPS para GitHub Releases.
"""

from __future__ import annotations

import logging
import os
import platform
import stat
import urllib.request
import zipfile
from pathlib import Path

log = logging.getLogger("mtclone.downloader")

# Diretório padrão onde os binários ficam armazenados
_TOOLS_DIR = Path.home() / ".mtclone" / "tools"

# URLs de releases (GitHub) — ajuste as versões conforme necessário
_APKTOOL_URL = (
    "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/"
    "apktool_2.9.3.jar"
)
_UBER_SIGNER_URL = (
    "https://github.com/nicedayzhu/uber-apk-signer/releases/download/v1.3.0/"
    "uber-apk-signer-1.3.0.jar"
)
# zipalign vem do Android Build Tools — usamos um mirror community
_ZIPALIGN_URLS: dict[str, str] = {
    "Windows": (
        "https://github.com/nicedayzhu/build-tools/releases/download/"
        "34.0.0/build-tools-34.0.0-windows.zip"
    ),
    "Linux": (
        "https://github.com/nicedayzhu/build-tools/releases/download/"
        "34.0.0/build-tools-34.0.0-linux.zip"
    ),
    "Darwin": (
        "https://github.com/nicedayzhu/build-tools/releases/download/"
        "34.0.0/build-tools-34.0.0-macos.zip"
    ),
}


def _ensure_dir() -> Path:
    """Cria o diretório de ferramentas se não existir."""
    _TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    return _TOOLS_DIR


def _download(url: str, dest: Path) -> None:
    """Baixa um arquivo de *url* para *dest* (sem telemetria)."""
    log.info("Baixando %s → %s", url, dest)
    urllib.request.urlretrieve(url, str(dest))  # noqa: S310
    log.info("Download concluído: %s", dest.name)


def _make_executable(path: Path) -> None:
    """Torna um arquivo executável em Unix."""
    if platform.system() != "Windows":
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def get_apktool_jar() -> Path:
    """Retorna o caminho para o JAR do apktool, baixando se necessário."""
    tools = _ensure_dir()
    jar = tools / "apktool.jar"
    if not jar.exists():
        _download(_APKTOOL_URL, jar)
    return jar


def get_uber_signer_jar() -> Path:
    """Retorna o caminho para o JAR do uber-apk-signer, baixando se necessário."""
    tools = _ensure_dir()
    jar = tools / "uber-apk-signer.jar"
    if not jar.exists():
        _download(_UBER_SIGNER_URL, jar)
    return jar


def get_zipalign() -> Path:
    """Retorna o caminho para o binário zipalign, baixando se necessário."""
    tools = _ensure_dir()
    sys_name = platform.system()
    exe_name = "zipalign.exe" if sys_name == "Windows" else "zipalign"
    exe_path = tools / exe_name

    if exe_path.exists():
        return exe_path

    url = _ZIPALIGN_URLS.get(sys_name)
    if url is None:
        raise RuntimeError(f"Sistema não suportado para zipalign: {sys_name}")

    zip_path = tools / "build-tools.zip"
    _download(url, zip_path)

    # Extrair apenas o zipalign do zip
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            basename = os.path.basename(member)
            if basename in ("zipalign", "zipalign.exe"):
                data = zf.read(member)
                exe_path.write_bytes(data)
                break
        else:
            raise FileNotFoundError("zipalign não encontrado no arquivo baixado.")

    zip_path.unlink(missing_ok=True)
    _make_executable(exe_path)
    return exe_path
