import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import argparse
import locale


# Set Hungarian locale for proper sorting (if available)
try:
    locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
except locale.Error:
    print("Warning: Hungarian locale not found. Sorting may be approximate.")

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/"
}

def extract_tags(calibre_root):
    """Extract all tags from Calibre library OPF files."""
    tag_usage = defaultdict(set)  # tag -> set of book folder paths
    books_without_tags = []

    for opf_file in Path(calibre_root).rglob("metadata.opf"):
        try:
            tree = ET.parse(opf_file)
            root = tree.getroot()
            subjects = root.findall(".//dc:subject", NAMESPACES)

            if not subjects:
                title_elem = root.find(".//dc:title", NAMESPACES)
                title = title_elem.text.strip() if title_elem is not None else "(no title)"
                book_path_title = f"{opf_file.parent}/{title}"
                books_without_tags.append(book_path_title)
            else:
                for subject in subjects:
                    tag = subject.text.strip()
                    tag_usage[tag].add(book_path_title)

        except Exception as e:
            print(f"Error parsing {opf_file}: {e}")

    return tag_usage, books_without_tags


def main():
    parser = argparse.ArgumentParser(description="Extract all tags from a Calibre library")
    parser.add_argument("calibre_root", help="Path to the root folder of the Calibre library")
    parser.add_argument("--no-tags-file", default="books_without_tags.txt",
                        help="Output file for books with no tags")
    parser.add_argument("--tags-file", default="all_tags.txt",
                        help="Output file for all tags (alphabetical order)")
    args = parser.parse_args()

    tags, books_without_tags = extract_tags(args.calibre_root)

    # 1️⃣ Save books with no tags (full path + title)
    if books_without_tags:
        with open(args.no_tags_file, "w", encoding="utf-8") as f:
            for book in sorted(books_without_tags, key=str.casefold):
                f.write(book + "\n")
        print(f"Books with no tags saved to '{args.no_tags_file}' ({len(books_without_tags)} books).")

    # 2️⃣ Save all tags sorted
    sorted_tags = sorted(tags.keys(), key=lambda t: locale.strxfrm(t.lower()))
    with open(args.tags_file, "w", encoding="utf-8") as f:
        for tag in sorted_tags:
            f.write(tag + "\n")
    print(f"All tags saved to '{args.tags_file}' ({len(sorted_tags)} tags).")


if __name__ == "__main__":
    main()
