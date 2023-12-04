#!/bin/bash

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPTDIR}" >/dev/null || exit

echo "Preparing Python environment..."
python3 -m pip install poetry >/dev/null

echo "Running app..."
#cd calibre2web || exit
poetry.exe run python calibre2md/main.py
