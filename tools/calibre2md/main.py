import os
import sys

sys.path.append("c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\calibre_tools")

from calibre2md.Library import Library

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
git_repo_url = ""


def main():
    global git_repo_url
    script_directory = os.path.dirname(os.path.abspath(__file__))

    root_dir = "c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\lib"
    root_dir = "c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\kutya"
    root_dir = "c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\libXX"
    print("Current directory: " + os.getcwd())
    print("Script  directory: " + script_directory)

    lib = Library(root_dir=root_dir)
    lib.gen_md()


if __name__ == '__main__':
    main()

print("End.")
