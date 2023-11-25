import argparse
import os
import pathlib
from pathlib import Path

from Library import Library

# sys.path.append("c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\calibre_tools")

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
git_repo_url = ""


def get_script_directory() -> pathlib.Path:
    return Path(__file__).parent.resolve()


def get_available_libraries():
    libraries_directory = get_script_directory().parent.parent / 'libs'
    return [libraries_directory.joinpath(name) for name in
            os.listdir(libraries_directory) if
            os.path.isdir(os.path.join(libraries_directory, name))]


def prompt_for_library() -> pathlib.Path:
    available_libraries = get_available_libraries()

    print('Choose a library:')
    for idx, library in enumerate(available_libraries, start=1):
        print(f"{idx}. {library.name}")

    while True:
        try:
            choice = int(input('Enter the number of the library: '))
            if 1 <= choice <= len(available_libraries):
                selected_library = available_libraries[choice - 1]
                break
            else:
                print('Invalid choice. Please enter a valid number.')
        except ValueError:
            print('Invalid input. Please enter a number.')

    return selected_library


def main():
    global git_repo_url

    parser = argparse.ArgumentParser(description='Process a library.')
    parser.add_argument('--library', help='Name of the library')
    args = parser.parse_args()
    library: pathlib.Path

    if args.library is None:
        # If the library name is not provided, prompt the user to choose one
        library = prompt_for_library()
    else:
        library = get_script_directory().parent.parent / 'libs' / args.library

    lib = Library(root_dir=library)
    lib.gen_md()


if __name__ == '__main__':
    main()

print("End.")
