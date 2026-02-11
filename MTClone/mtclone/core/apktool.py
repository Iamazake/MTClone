"""
apktool.py — Wrapper para o apktool via subprocess.

Funcionalidades:
  - decode: descompila APK em pasta de recursos + smali
  - build: recompila pasta em APK
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from mtclone.utils.downloader import get_apktool_jar

log = logging.getLogger("mtclone.apktool")


def _find_java() -> str:
    """Localiza o executável java no PATH."""
    java = shutil.which("java")
    if java is None:
        raise FileNotFoundError(
            "Java não encontrado no PATH. Instale o JDK 11+ antes de usar o mtclone."
        )
    return java


def decode(apk_path: Path, output_dir: Path, *, force: bool = True) -> Path:
    """
    Descompila *apk_path* para *output_dir* usando apktool d.

    Parâmetros
    ----------
    apk_path : Path
        Caminho do arquivo .apk.
    output_dir : Path
        Pasta de destino.
    force : bool
        Se True, sobrescreve a pasta de destino caso já exista.

    Retorna
    -------
    Path
        Caminho da pasta de saída.
    """
    jar = get_apktool_jar()
    java = _find_java()

    cmd: list[str] = [
        java, "-jar", str(jar),
        "d", str(apk_path),
        "-o", str(output_dir),
    ]
    if force:
        cmd.append("-f")

    log.info("Executando: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error("apktool decode falhou:\n%s", result.stderr)
        raise RuntimeError(f"apktool decode falhou (código {result.returncode}):\n{result.stderr}")

    log.info("Decode concluído: %s → %s", apk_path, output_dir)
    return output_dir


def build(source_dir: Path, output_apk: Path) -> Path:
    """
    Recompila *source_dir* em *output_apk* usando apktool b.

    Parâmetros
    ----------
    source_dir : Path
        Pasta descompilada anteriormente.
    output_apk : Path
        Caminho do APK de saída.

    Retorna
    -------
    Path
        Caminho do APK gerado.
    """
    jar = get_apktool_jar()
    java = _find_java()

    cmd: list[str] = [
        java, "-jar", str(jar),
        "b", str(source_dir),
        "-o", str(output_apk),
    ]

    log.info("Executando: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error("apktool build falhou:\n%s", result.stderr)
        raise RuntimeError(f"apktool build falhou (código {result.returncode}):\n{result.stderr}")

    log.info("Build concluído: %s → %s", source_dir, output_apk)
    return output_apk
