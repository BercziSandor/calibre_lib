import os
import pathlib
import re
import subprocess
from typing import List


def get_repo_url(rootDir) -> str:
    def get_git_url_from_config(config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                for line in file:
                    if line.strip().startswith('url'):
                        _, url = line.split(' = ')
                        return url.strip()
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    repo_url: str = ''
    git_config_file=os.path.join(rootDir, '.git', 'config')
    if not os.path.exists(git_config_file):
        return '???'
    git_url = get_git_url_from_config(git_config_file)

    result = re.search(r"^git@github\.com:(.*)\/(.*)\.git", git_url)
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
