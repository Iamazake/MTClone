"""setup.py — Instalação do mtclone."""

from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="mtclone",
    version="0.1.0",
    description="Gerenciador de APK open-source — decode, build, sign, align.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="mtclone contributors",
    license="MIT",
    python_requires=">=3.11",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mtclone=mtclone.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
)
