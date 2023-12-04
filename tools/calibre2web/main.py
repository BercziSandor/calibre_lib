import argparse
import os
import pathlib
import sys
from pathlib import Path

from Library import Library

# sys.path.append("c:\\Users\\VWW3224\\Documents\\Calibre\\libs\\calibre_tools")

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
git_repo_url = ""


def get_script_directory() -> pathlib.Path:
    return Path(__file__).parent.resolve()


def get_available_libraries(libraries_root: Path = get_script_directory().parent.parent / 'libs'):
    return [libraries_root.joinpath(name) for name in
            os.listdir(libraries_root) if
            os.path.isdir(os.path.join(libraries_root, name))]


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

    parser = argparse.ArgumentParser(description='Generating static Calibre catalog for publishing on the internet.')
    parser.add_argument('--library', help='The path of the library to be processed. It can be absolute or relative '
                                          'to the directory of this script.')
    args = parser.parse_args()
    library: pathlib.Path

    if args.library is None:
        print("\nError: The library name is not provided, aborting.\n")
        print(parser.format_help())
        sys.exit(1)
        # library = prompt_for_library()
    else:
        print(f"Finding '{args.library}'...")
        library = pathlib.Path(args.library)
        print(f"Trying as {library}.", end='')
        if library.exists():
            print(" - found.")
        else:
            print(" - not found.")
            library = get_script_directory() / args.library
            print(f"Trying as {library}.", end='')
            if library.exists():
                print(" - found.")
            else:
                print(" - not found.")
                library = get_script_directory().parent.parent / 'libs' / args.library
                print(f"Trying as {library}.", end='')
                if library.exists():
                    print(" - found.")
                else:
                    print(" - not found.")
                    print("\nError: The provided library does not exist, aborting.\n")
                    print(parser.format_help())
                    sys.exit(1)

    lib = Library(root_dir=library)
    lib.gen_catalog_by_authors()
    lib.gen_catalog_by_tags()


if __name__ == '__main__':
    main()

print("End.")
