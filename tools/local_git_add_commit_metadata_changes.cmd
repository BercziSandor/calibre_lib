@echo off
cd %~dp0
cd lib

git add *.opf -v
git add *.json -v
git add metadata.db -v
git commit -am"Auto metadata commit"


TIMEOUT /T 5
