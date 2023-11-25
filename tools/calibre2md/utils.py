import os
import pathlib
import re
import subprocess
from typing import List


def get_repo_url(rootDir) -> str:
    repo_url: str = ''
    dir_orig = os.getcwd()

    if not os.path.exists(os.path.join(rootDir, '.git')):
        return '???'

    os.chdir(rootDir)
    console_output = subprocess.check_output(['git', 'config', '--get',
                                              'remote.origin.url']).decode(
        "utf-8")
    os.chdir(dir_orig)

    result = re.search(r"^git@github\.com:(.*)\/(.*)\.git", console_output)
    if result:
        repo_url = f"https://github.com/{result.group(1)}/{result.group(2)}"
    return repo_url


def find_opf_paths_in_dir(root=os.getcwd(), file_ending='.opf') -> List[pathlib.Path]:
    found_opf_paths: List[str] = []
    for p, d, files in os.walk(root):
        for file in files:
            if file.lower().endswith(file_ending):
                found_opf_paths.append(pathlib.Path(os.path.abspath(
                    os.path.join(p,
                                 file))))
    return found_opf_paths
