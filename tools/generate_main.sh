#!/bin/bash
set -e

target=main

target="../libs/${target}"

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pushd "${SCRIPTDIR}" >/dev/null || exit
pushd "$target" >/dev/null || exit
echo
echo "Working on '$(basename $target)'..."

echo "Check Git repository for changes..."
if [[ $(git status --porcelain | wc -l) -gt 0 ]]; then
    echo "Error: Git repository has uncommitted changes:"
    echo "--------------------------------------"
    git status
    echo "--------------------------------------"
    echo "This is not my change, please clean the repo manually and try again."
    popd
    popd
    exit 1
fi

popd

echo "Preparing Python environment..."
python3 -m pip install poetry || sudo apt install python3-poetry
poetry install --without dev

echo "Running app..."
poetry run python calibre2web/main.py --library "$target"

pushd "$target"
echo
if [[ $(git status --porcelain | wc -l) -gt 0 ]]; then
    echo "Pushing changes in the Git repository"
    git add .
    git commit -am "Automatically generated - $(python3 --version)"
    git push
else
    echo "No local changes, push skipped."
fi
popd

popd
