import os
import pathlib
import sys
import urllib
from typing import Dict

import snakemd

from calibre2md import Opf
from calibre2md.utils import get_repo_url, find_opf_paths_in_dir


class Library:

    def __init__(self, root_dir):
        self.root_dir = pathlib.Path(root_dir).absolute()
        if not self.root_dir.exists():
            print(f"Input directory {self.root_dir} does not exist, aborting.")
            sys.exit(1)
        self.repo_url = get_repo_url(root_dir)
        self.opfs = self.get_opfs()

    @staticmethod
    def sort_books(opfs) -> Dict:
        data_auth_year_series = {}
        for opf in opfs:
            if opf.creator not in data_auth_year_series:
                data_auth_year_series[opf.creator] = {
                    'series': {},
                    'others': {}
                }
            if opf.series:
                if opf.series not in data_auth_year_series[opf.creator][
                    'series']:
                    data_auth_year_series[opf.creator]['series'][
                        opf.series] = {}
                data_auth_year_series[opf.creator]['series'][opf.series][
                    opf.series_index] = opf
            else:
                if opf.dt.year not in data_auth_year_series[opf.creator][
                    'others']:
                    data_auth_year_series[opf.creator]['others'][
                        opf.dt.year] = []
                data_auth_year_series[opf.creator]['others'][
                    opf.dt.year].append(
                    opf)
        return data_auth_year_series

    def get_url(self, file_path: pathlib.Path):
        u = urllib.parse.quote(
            str(file_path.relative_to(self.root_dir)).replace(
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

    def gen_md(self):
        details_content = "### Részletek\n"
        catalog_file_name = 'catalog.md'
        details_file_name = 'catalog_details.md'
        books_auth_year_series = self.sort_books(self.opfs)

        # https://github.com/TheRenegadeCoder/SnakeMD
        # https://therenegadecoder.com/code/the-complete-guide-to-snakemd-a-python-library-for-generating-markdown/
        doc = snakemd.new_doc("Example")
        doc.add_header("Könyvek")
        doc.add_table_of_contents()

        # doc.add_paragraph("par1_text")
        doc.add_header("Szerzők szerint", level=2)

        details_folder = pathlib.Path(os.path.join(self.root_dir, '_details'))
        if not details_folder.exists():
            details_folder.mkdir()

        for creator, books in books_auth_year_series.items():
            doc.add_header(creator, level=3)

            details_file_name = f"{creator}.md"
            details_file_name_quoted = urllib.parse.quote(
                "_details/" + details_file_name)
            details_content = ""

            if (len(books['series']) > 0):
                doc.add_paragraph("Sorozatok:")
                for serie in sorted(books['series']):
                    titles_list = []
                    for index in sorted(books['series'][serie]):
                        o: Opf = books['series'][serie][index]
                        link_download = ""
                        if len(o.books) > 0:
                            book = o.books[0]
                            url = self.get_url(book)
                            filename, file_extension = os.path.splitext(
                                book)
                            link_download = f"[{file_extension.replace('.', '')}]" \
                                            f"({url})"
                            o.link_download=link_download

                        link_details = f"[részletek]({details_file_name_quoted}#id_{o.id})"
                        titles_list.append(
                            f"{index} ({o.dt.year}) - {o.title} "
                            f"{link_details} {link_download}\n")
                        details_content += (o.get_md_details())
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
                    for o in books['others'][year]:
                        link_download = ""
                        if len(o.books) > 0:
                            book = o.books[0]
                            url = self.get_url(book)
                            filename, file_extension = os.path.splitext(
                                book)
                            link_download = f"[{file_extension.replace('.', '')}]" \
                                            f"({url})"
                        link_details = f"[details](" \
                                       f"{details_file_name_quoted}#id_{o.id})"
                        titles_list.append(f"({year}) - {o.title} "
                                           f"{link_details} {link_download}")
                        details_content += (o.get_md_details())
                doc.add_unordered_list(titles_list)
            out_file_details = pathlib.Path(os.path.join(details_folder,
                                                         details_file_name))
            out_file_details.write_text(details_content, encoding='utf-8')

        catalog_content = str(doc)
        out_file = pathlib.Path(os.path.join(self.root_dir, catalog_file_name))
        out_file.write_text(catalog_content, encoding='utf-8')

        # print(md_content)
        return out_file
