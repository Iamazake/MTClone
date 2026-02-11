"""
align.py — Alinhamento de APKs com zipalign.

O zipalign melhora a performance de leitura do APK no dispositivo Android.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from mtclone.utils.downloader import get_zipalign

log = logging.getLogger("mtclone.align")


def align(apk_in: Path, apk_out: Path | None = None, *, alignment: int = 4) -> Path:
    """
    Alinha *apk_in* usando zipalign.

    Parâmetros
    ----------
    apk_in : Path
        APK de entrada (não alinhado).
    apk_out : Path | None
        APK de saída. Se None, gera ``<nome>_aligned.apk`` no mesmo diretório.
    alignment : int
        Tamanho do alinhamento em bytes (padrão: 4).

    Retorna
    -------
    Path
        Caminho do APK alinhado.
    """
    zipalign_bin = get_zipalign()

    if apk_out is None:
        apk_out = apk_in.with_stem(apk_in.stem + "_aligned")

    cmd: list[str] = [
        str(zipalign_bin),
        "-f",                   # forçar sobrescrita
        "-p",                   # alinhamento de página (recomendado)
        str(alignment),
        str(apk_in),
        str(apk_out),
    ]

    log.info("Alinhando: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error("zipalign falhou:\n%s", result.stderr)
        raise RuntimeError(
            f"zipalign falhou (código {result.returncode}):\n{result.stderr}"
        )

    log.info("APK alinhado: %s → %s", apk_in, apk_out)
    return apk_out
