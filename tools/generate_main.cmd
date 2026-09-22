@echo off

set target=main
set target=../libs/%target%

for /f "delims=" %%v in ('python --version 2^>^&1') do set "python_version=%%v"

pushd "%~dp0"
pushd "%target%"
echo Check if the Git repository has uncommitted changes
git status | findstr /R "nothing to commit, working tree clean" > nul
if %errorlevel% neq 0 (
    echo Error: Git repository has uncommitted changes:
    echo --------------------------------------
    git status
    echo --------------------------------------
    echo This is not my change, please clean the repo manually and try again.
    popd
    popd
    exit /b 1
)

popd
python.exe -m pip install --upgrade pip

echo Preparing Python environment...
python -m pip install poetry
poetry install --without dev

echo Running app...
poetry.exe run python calibre2web/main.py --library %target%

pushd "%target%"
echo
git status | findstr /R "nothing to commit, working tree clean" > nul
if %errorlevel% neq 0 (
    echo Pushing changes in the Git repository
    git add .
    git commit -am"Automatically generated - %python_version%"
    git push
) else (
    echo No local changes, push skipped.
)
popd
popd
