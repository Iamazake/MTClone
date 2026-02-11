"""
signer.py — Assina APKs usando uber-apk-signer.

Usa uma debug-keystore embutida por padrão (gerada automaticamente pelo uber-apk-signer).
"""

from __future__ import annotations

import logging
import subprocess
import shutil
from pathlib import Path

from mtclone.utils.downloader import get_uber_signer_jar

log = logging.getLogger("mtclone.signer")


def _find_java() -> str:
    java = shutil.which("java")
    if java is None:
        raise FileNotFoundError(
            "Java não encontrado no PATH. Instale o JDK 11+ antes de usar o mtclone."
        )
    return java


def sign(apk_path: Path, output_dir: Path | None = None) -> Path:
    """
    Assina *apk_path* com uber-apk-signer (debug keystore).

    Parâmetros
    ----------
    apk_path : Path
        APK a ser assinado.
    output_dir : Path | None
        Pasta de saída. Se None, usa o mesmo diretório do APK.

    Retorna
    -------
    Path
        Caminho do APK assinado (sufixo *-aligned-debugSigned.apk*).
    """
    jar = get_uber_signer_jar()
    java = _find_java()

    cmd: list[str] = [
        java, "-jar", str(jar),
        "--apks", str(apk_path),
    ]

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--out", str(output_dir)])

    log.info("Assinando: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error("uber-apk-signer falhou:\n%s", result.stderr)
        raise RuntimeError(
            f"uber-apk-signer falhou (código {result.returncode}):\n{result.stderr}"
        )

    # uber-apk-signer gera arquivo com sufixo no mesmo diretório
    out_dir = output_dir or apk_path.parent
    signed_candidates = list(out_dir.glob("*-aligned-debugSigned.apk"))
    if not signed_candidates:
        # fallback: procurar qualquer apk assinado
        signed_candidates = list(out_dir.glob("*-debugSigned.apk"))

    if not signed_candidates:
        raise FileNotFoundError(
            "APK assinado não encontrado após execução do uber-apk-signer."
        )

    signed = signed_candidates[0]
    log.info("APK assinado gerado: %s", signed)
    return signed
