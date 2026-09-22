import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
from collections import defaultdict
import sys
import csv
import traceback

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf"
}
ET.register_namespace("dc", NAMESPACES["dc"])
ET.register_namespace("opf", NAMESPACES["opf"])

DRY_RUN = True  # True = csak listáz, False = ténylegesen írja a fájlokat
DRY_RUN = False  # True = csak listáz, False = ténylegesen írja a fájlokat

def process_opf(opf_path, replace_map, tag_map):
    tree = ET.parse(opf_path)
    root = tree.getroot()

    metadata = root.find("opf:metadata", NAMESPACES)
    if metadata is None:
        print(f"Nincs <metadata> elem: {opf_path}")
        return False

    subjects = metadata.findall("dc:subject", NAMESPACES)
    existing_tags = {s.text.strip() for s in subjects}

    # 1️ Replace
    replaced_tags = {}
    for subject in subjects:
        tag = subject.text.strip()
        if tag in replace_map:
            new_tag = replace_map[tag]
            if new_tag != tag:
                replaced_tags[tag] = new_tag
                existing_tags.discard(tag)
                existing_tags.add(new_tag)

    # 2️ Kiegészítés mapping alapján
    added_tags = set()
    for tag in existing_tags:
        mapped_set = tag_map.get(tag)
        if mapped_set:
            for mapped_tag in mapped_set:
                if mapped_tag not in existing_tags:
                    added_tags.add(mapped_tag)

    if replaced_tags or added_tags:
        print(f"\nKönyv: {opf_path.parent.name}")
        if replaced_tags:
            for old, new in replaced_tags.items():
                print(f"  Replace: '{old}' → '{new}'")
        if added_tags:
            print(f"  Hozzáadott tagek: {', '.join(sorted(added_tags))}")

        if not DRY_RUN:
            for tag in added_tags:
                el = ET.SubElement(metadata, f"{{{NAMESPACES['dc']}}}subject")
                el.text = tag
            ET.indent(tree, space="    ", level=0)
            tree.write(opf_path, encoding="utf-8", xml_declaration=True)
        return True

    return False

def process_library(calibre_root, replace_map_file, tag_map_file):
    replace_map = {}
    with open(replace_map_file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for orig, neww in reader:
            replace_map[orig] = neww

    tag_map = defaultdict(set)
    with open(tag_map_file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for magy, angol in reader:
            tag_map[magy].add(angol)
            tag_map[angol].add(magy)

    changed = 0
    all_tags = set()  # ⚡ összes megtalált tag a könyvtárban
    books_without_tags = []
    for opf in Path(calibre_root).rglob("metadata.opf"):
        try:
            tree = ET.parse(opf)
            root = tree.getroot()
            metadata = root.find("opf:metadata", NAMESPACES)
            if metadata is None:
                continue

            subjects = metadata.findall("dc:subject", NAMESPACES)
            existing_tags = {s.text.strip() for s in subjects if s.text}
            if not existing_tags:
                title_elem = root.find(".//dc:title", NAMESPACES)
                title = title_elem.text.strip() if title_elem is not None else "(no title)"
                book_path_title = f"{opf.parent}/{title}"
                books_without_tags.append(book_path_title)
                continue   # ⚡ nem próbáljuk feldolgozni

            all_tags.update(existing_tags)

            if process_opf(opf, replace_map, tag_map):
                changed += 1

        except Exception as e:
            print(f"Hiba {opf}: {e}")
            traceback.print_exc()
            sys.exit(1)

    print(f"\nÖsszesen {changed} könyv módosítandó.")

    if books_without_tags:
        print("\n📕 Könyvek tag nélkül:")
        for i, book in enumerate(books_without_tags, start=1):
            print(f"  {i}. {book}")

    # ⚡ Nem fordított tag-ek
    unmapped_tags = sorted(t for t in all_tags if t not in tag_map)
    if unmapped_tags:
        print("\nTag-ek, amik még nincsenek a tag-translations file-ban:")
        for t in unmapped_tags:
            print(f"  {t}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract all tags from a Calibre library")
    parser.add_argument("calibre_root", help="Path to the root folder of the Calibre library")
    parser.add_argument("--tag-replacements-file", default="1_tag_replacements.csv",
                        help="File containing tag replacements")
    parser.add_argument("--tag-translations-file", default="2_tag_translations.csv",
                        help="File containing tag translations")
    args = parser.parse_args()


    process_library(
        args.calibre_root,
        args.tag_replacements_file,
        args.tag_translations_file
    )
