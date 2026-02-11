"""
__main__.py — CLI do mtclone.

Uso:
    mtclone decode app.apk           → descompila para ./app/
    mtclone build  ./app/            → gera app_mod.apk (assinado e alinhado)
    mtclone sign   app.apk           → assina APK existente
    mtclone align  app.apk           → alinha APK existente

Flags globais:
    -v / --verbose                   → ativa logs detalhados
    --version                        → mostra versão
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from mtclone import __version__
from mtclone.core.apktool import decode as apktool_decode, build as apktool_build
from mtclone.core.signer import sign as signer_sign
from mtclone.core.align import align as aligner_align


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(name)s: %(message)s",
    )


def _cmd_decode(args: argparse.Namespace) -> None:
    apk = Path(args.apk)
    if not apk.exists():
        print(f"Erro: arquivo não encontrado — {apk}", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output) if args.output else Path(apk.stem)
    print(f"Descompilando {apk} → {output}/")
    apktool_decode(apk, output)
    print(f"Pronto! Pasta gerada: {output}/")


def _cmd_build(args: argparse.Namespace) -> None:
    source = Path(args.source)
    if not source.is_dir():
        print(f"Erro: diretório não encontrado — {source}", file=sys.stderr)
        sys.exit(1)

    output_name = args.output if args.output else f"{source.name}_mod.apk"
    output_apk = Path(output_name)

    print(f"Recompilando {source}/ → {output_apk}")
    apktool_build(source, output_apk)

    # Alinhar
    print("Alinhando APK...")
    aligned = aligner_align(output_apk)

    # Assinar
    print("Assinando APK...")
    signed = signer_sign(aligned)

    # Limpar arquivos intermediários
    if aligned != output_apk and aligned.exists():
        aligned.unlink(missing_ok=True)

    # Renomear para o nome final
    final_name = output_apk.with_stem(output_apk.stem).name
    final_path = signed.parent / final_name
    if signed != final_path:
        signed.rename(final_path)
        signed = final_path

    print(f"Pronto! APK gerado: {signed}")


def _cmd_sign(args: argparse.Namespace) -> None:
    apk = Path(args.apk)
    if not apk.exists():
        print(f"Erro: arquivo não encontrado — {apk}", file=sys.stderr)
        sys.exit(1)

    print(f"Assinando {apk}...")
    signed = signer_sign(apk)
    print(f"Pronto! APK assinado: {signed}")


def _cmd_align(args: argparse.Namespace) -> None:
    apk = Path(args.apk)
    if not apk.exists():
        print(f"Erro: arquivo não encontrado — {apk}", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output) if args.output else None
    print(f"Alinhando {apk}...")
    aligned = aligner_align(apk, output)
    print(f"Pronto! APK alinhado: {aligned}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mtclone",
        description="mtclone — Gerenciador de APK open-source",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Ativa logs detalhados"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # decode
    p_decode = sub.add_parser("decode", help="Descompila um APK")
    p_decode.add_argument("apk", help="Caminho do arquivo .apk")
    p_decode.add_argument("-o", "--output", help="Pasta de saída (padrão: nome do APK)")

    # build
    p_build = sub.add_parser("build", help="Recompila pasta em APK assinado")
    p_build.add_argument("source", help="Pasta descompilada")
    p_build.add_argument("-o", "--output", help="Nome do APK de saída")

    # sign
    p_sign = sub.add_parser("sign", help="Assina um APK")
    p_sign.add_argument("apk", help="Caminho do arquivo .apk")

    # align
    p_align = sub.add_parser("align", help="Alinha um APK com zipalign")
    p_align.add_argument("apk", help="Caminho do arquivo .apk")
    p_align.add_argument("-o", "--output", help="Caminho do APK alinhado")

    args = parser.parse_args(argv)
    _setup_logging(args.verbose)

    dispatch = {
        "decode": _cmd_decode,
        "build": _cmd_build,
        "sign": _cmd_sign,
        "align": _cmd_align,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
