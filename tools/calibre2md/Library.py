import os
import pathlib
import sys
import urllib
from collections import defaultdict
from typing import Dict

import snakemd

import Opf
from utils import get_repo_url, find_opf_paths_in_dir


class Library:

    def __init__(self, root_dir: pathlib.Path):
        self.root_dir = root_dir
        if not self.root_dir.exists():
            print(f"Input directory {self.root_dir} does not exist, aborting.")
            sys.exit(1)
        self.repo_url = get_repo_url(root_dir.parent.parent)
        self.catalog_url = self.repo_url + "/" + root_dir.parent.name + "/" + \
                           root_dir.parent.parent.name
        self.opfs = self.get_opfs()

    @staticmethod
    def sort_books_tag(opfs) -> Dict:
        data_tags = {}

        for opf in opfs:
            subjects = opf.subjects
            if not opf.subjects:
                subjects = ['_notTagged']

            for tag in opf.subjects:
                if tag not in data_tags:
                    data_tags[tag] = []
                data_tags[tag].append(opf)

        return dict(data_tags)

    @staticmethod
    def sort_books_auth_year(opfs) -> Dict:
        data_auth_year_series = defaultdict(
            lambda: {'series': defaultdict(dict), 'others': defaultdict(list)})

        for opf in opfs:
            if opf.series:
                data_auth_year_series[opf.creator]['series'][opf.series][
                    opf.series_index] = opf
            else:
                data_auth_year_series[opf.creator]['others'][
                    opf.dt.year].append(opf)

        return dict(data_auth_year_series)

    def get_url(self, file_path: pathlib.Path):
        u = urllib.parse.quote(
            str(file_path.relative_to(self.root_dir.parent.parent)).replace(
                '\\', '/'))
        url = f"{self.repo_url}/raw/main/{u}"
        self.url = url
        return url

    def get_opfs(self):
        opfs = []
        for opf_path in find_opf_paths_in_dir(self.root_dir):
            opfs.append(Opf.Opf(path=opf_path, repo_url=self.repo_url,
                                library=self))
        return opfs

    def get_md_for_auth(self, creator, books):
        doc = snakemd.new_doc("Example")

    def gen_md_by_tags(self):
        tagList_file_name = 'catalog_tags.md'
        tag_file_name = 'catalog_tags_details.md'
        books_tags = self.sort_books_tag(self.opfs)

        details_folder = self.root_dir / '_tags'
        if not details_folder.exists():
            details_folder.mkdir()

        # https://github.com/TheRenegadeCoder/SnakeMD
        # https://therenegadecoder.com/code/the-complete-guide-to-snakemd-a-python-library-for-generating-markdown/
        md_TagList = snakemd.new_doc("Example")
        md_TagList.add_header("Tagek")
        tags = ""
        for tag in sorted(books_tags.keys()):
            tag_file = self.root_dir / "_tags" / f"{self.get_tag_corrected(tag)}.md"

            # generate content for tag X
            md_Tag = snakemd.new_doc(tag)
            md_Tag.add_header(tag)
            opfs = books_tags.get(tag)
            books = []
            for opf in opfs:
                if len(opf.books) > 0:
                    details_file_name_quoted = urllib.parse.quote(
                        "../_details/" + opf.creator + ".md")
                    link_details = f"[részletek]({details_file_name_quoted}#id_{opf.id})"
                    books.append(f"{opf.creator}: {opf.title} {link_details}")
            md_Tag.add_unordered_list(books)

            tag_file.write_text(str(md_Tag), encoding='utf-8')

            tag_file_name_quoted = self.catalog_url + "/blob/main/_tags/" + urllib.parse.quote(
                    f"{self.get_tag_corrected(tag)}.md")
            tags += f"[{tag}]({tag_file_name_quoted}) "

        md_TagList.add_paragraph(tags)

        tagList_file = self.root_dir / tagList_file_name
        tagList_file.write_text(str(md_TagList), encoding='utf-8')

        return tagList_file


    def gen_md_by_authors(self):
        details_content = "### Részletek\n"
        catalog_file_name = 'catalog.md'
        details_file_name = 'catalog_details.md'
        books_auth_year_series = self.sort_books_auth_year(self.opfs)
        books_tags = self.sort_books_tag(self.opfs)

        details_folder = self.root_dir / '_details'
        if not details_folder.exists():
            details_folder.mkdir()

        # https://github.com/TheRenegadeCoder/SnakeMD
        # https://therenegadecoder.com/code/the-complete-guide-to-snakemd-a-python-library-for-generating-markdown/
        doc = snakemd.new_doc("Example")
        doc.add_header("Könyvek szerzők szerint")
        doc.add_table_of_contents()

        for creator, books in books_auth_year_series.items():
            doc.add_header(creator, level=2)

            details_file_name = f"{creator}.md"
            details_file_name_quoted = urllib.parse.quote(
                "_details/" + details_file_name)
            details_content = ""

            if (len(books['series']) > 0):
                doc.add_paragraph("Sorozatok:")
                for serie in sorted(books['series']):
                    titles_list = []
                    for index in sorted(books['series'][serie]):
                        opf: Opf = books['series'][serie][index]
                        link_download = ""
                        if len(opf.books) > 0:
                            book = opf.books[0]
                            url = self.get_url(book)
                            filename, file_extension = os.path.splitext(
                                book)
                            link_download = f"[{file_extension.replace('.', '')}]" \
                                            f"({url})"
                            opf.link_download = link_download

                        link_details = f"[részletek]({details_file_name_quoted}#id_{opf.id})"
                        titles_list.append(
                            f"{index} ({opf.dt.year}) - {opf.title} "
                            f"{link_details} {link_download}\n")
                        details_content += (opf.get_md_details())
                    doc.add_paragraph(f"{serie}:")
                    doc.add_unordered_list(titles_list)
                    # doc.add_paragraph(f"{serie}:\n").add(
                    #     MDList([InlineText(item+ '\n')  for item in titles_list]))
                    # doc.add_element()

            if (len(books['others']) > 0):
                if (len(books['series']) > 0): doc.add_paragraph(
                    "Egyéb könyvek:")
                titles_list = []
                for year in sorted(books['others']):
                    for opf in books['others'][year]:
                        link_download = ""
                        if len(opf.books) > 0:
                            book = opf.books[0]
                            url = self.get_url(book)
                            filename, file_extension = os.path.splitext(
                                book)
                            link_download = f"[{file_extension.replace('.', '')}]" \
                                            f"({url})"
                        link_details = f"[details](" \
                                       f"{details_file_name_quoted}#id_{opf.id})"
                        titles_list.append(f"({year}) - {opf.title} "
                                           f"{link_details} {link_download}")
                        details_content += (opf.get_md_details())
                doc.add_unordered_list(titles_list)
            out_file_details = details_folder / details_file_name
            out_file_details.write_text(details_content, encoding='utf-8')

        catalog_content = str(doc)
        out_file = pathlib.Path(os.path.join(self.root_dir, catalog_file_name))
        out_file.write_text(catalog_content, encoding='utf-8')

        # print(md_content)
        return out_file


    def get_tag_corrected(self, subj):
        return subj.replace("(", " ").replace(")", " ").replace(
            "\\", "_").replace(
            "/", "_").replace("  ", " ").rstrip().lstrip()


    def get_tag_link(self, subj):
        tag_file_link = f"{self.catalog_url}/blob/main/_tags/" + \
                        urllib.parse.quote(f"{self.get_tag_corrected(subj)}.md")
        return f"[{subj}]({tag_file_link})"
