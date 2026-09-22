import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib
from collections import defaultdict
from typing import Dict, List
from urllib.parse import urlparse, unquote, quote

import snakemd
from bs4 import BeautifulSoup

from . import Opf
from .utils import get_repo_url, find_opf_paths_in_dir


class Library:

    def __init__(self, root_dir: pathlib.Path):
        self.url = None
        root_dir = pathlib.Path(os.path.normpath(root_dir.absolute()))
        self.root_dir = root_dir
        if not self.root_dir.exists():
            print(f"Input directory {self.root_dir} does not exist, aborting.")
            sys.exit(1)
        self.repo_url: str = get_repo_url(root_dir.parent)
        self.catalog_url: str = self.repo_url + "/" + root_dir.name
        self.opfs: List[Opf] = self.get_opfs

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

    def get_url(self, file_path: pathlib.Path) -> str:
        u = urllib.parse.quote(
            str(file_path.relative_to(self.root_dir.parent)).replace(
                '\\', '/'))
        url = f"{self.repo_url}/raw/main/{u}"
        self.url = url
        return url

    @property
    def get_opfs(self):
        opfs = []
        print(f"Reading files under {self.root_dir}...")
        for opf_path in find_opf_paths_in_dir(self.root_dir):
            opfs.append(Opf.Opf(path=str(opf_path.absolute()),
                                repo_url=self.repo_url,
                                library=self))

        print(f"{len(opfs)} books have been read.")
        return opfs

    def gen_catalog_by_tags(self, output_format='markdown'):
        extension = self.get_extension(output_format)
        tag_list_file_name = f"catalog_tags.{extension}"
        tag_list_file = self.root_dir / tag_list_file_name

        books_tags = self.sort_books_tag(self.opfs)

        details_folder = self.root_dir / '_tags'
        if not details_folder.exists():
            details_folder.mkdir()

        # https://github.com/TheRenegadeCoder/SnakeMD
        # https://therenegadecoder.com/code/the-complete-guide-to-snakemd-a-python-library-for-generating-markdown/
        md_TagList = snakemd.new_doc()
        md_TagList.add_heading("Tagek")
        tags = ""
        for tag in sorted(books_tags.keys()):
            tag_file = self.root_dir / "_tags" / f"{self.get_tag_corrected(tag)}.md"

            # generate content for tag X
            md_Tag = snakemd.new_doc()
            md_Tag.add_heading(tag)
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
            tags += self.get_tag_link(tag) + " | "

        md_TagList.add_paragraph(tags)

        md_content = str(md_TagList)
        if output_format == 'markdown':
            file_content = md_content
        elif output_format == 'markdeep':
            file_content = md_content
            file_content += "\n\n"
            file_content += "\n\n"

        tag_list_file.write_text(file_content, encoding='utf-8')

        return tag_list_file

    def convert_markdown_to(self, markdown_content: str, output_format: str):
        output_content = markdown_content
        if output_format == 'markdown':
            output_content = markdown_content
        elif output_format == 'markdeep':
            pass

    def get_extension(self, output_format) -> str:
        if output_format == 'markdown':
            extension = 'md'
        elif output_format == 'markdeep':
            extension = 'md.html'
        elif output_format == 'html':
            extension = 'html'
        else:
            print(f'Unsupported format: {output_format}')
            sys.exit(2)

        return extension

    def gen_catalog_by_authors(self, output_format='markdown'):
        details_content = "### Részletek\n"
        catalog_file_name = 'catalog_authors.md'
        if output_format == 'markdown':
            extension = 'md'
        elif output_format == 'markdeep':
            extension = 'md.html'

        books_auth_year_series = self.sort_books_auth_year(self.opfs)
        books_tags = self.sort_books_tag(self.opfs)

        details_folder = self.root_dir / '_details'
        if not details_folder.exists():
            details_folder.mkdir()

        # https://github.com/TheRenegadeCoder/SnakeMD
        # https://therenegadecoder.com/code/the-complete-guide-to-snakemd-a-python-library-for-generating-markdown/
        doc = snakemd.new_doc()
        doc.add_heading("Könyvek szerzők szerint")
        doc.add_table_of_contents()

        for creator, books in books_auth_year_series.items():
            doc.add_horizontal_rule()
            doc.add_heading(creator, level=2)

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

    def get_tag_corrected(self, subj) -> str:
        return subj.replace("(", " ").replace(")", " ").replace(
            "\\", "_").replace(
            "/", "_").replace("  ", " ").rstrip().lstrip().lower()

    def get_tag_link(self, subj, mode='github') -> str:
        if mode == 'github':
            tag_file_link = self.catalog_url.replace('/calibre_lib/',
                                                     '/calibre_lib/blob/main/') \
                            + "/_tags/" + \
                            urllib.parse.quote(
                                f"{self.get_tag_corrected(subj)}.md")
        return f"[{subj}]({tag_file_link})"

    def md2html(self, delete_markdown=False):

        def md_to_html(input_md: pathlib.Path, mode='markdeep'):

            if not input_md.exists():
                print(f"{input_md} does not exist.")
                sys.exit(2)

            html_file_name = str(input_md.absolute()).replace('.tmp.md',
                                                              '').replace(
                '.md', '.html')

            try:
                if mode == 'pandoc':
                    print(f' Converting MD to HTML with Pandoc')
                    output_html = pathlib.Path(html_file_name)
                    subprocess.run(['pandoc', input_md, '--metadata', 'title=',
                                    '-s',
                                    '-o', output_html], check=True,
                                   capture_output=True,
                                   text=True)
                    # pypandoc.convert_file(source_file=input_md, to='html',
                    #                       outputfile=output_html,
                    #                       extra_args=('--self-contained'))
                elif mode == 'markdeep':
                    output_html = pathlib.Path(html_file_name)
                    markdeep_footer = '<!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="markdeep.min.js" charset="utf-8"></script><script src="https://morgan3d.github.io/markdeep/latest/markdeep.min.js?" charset="utf-8"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>'
                    markdeep_footer += '<script>window.markdeepOptions = {' \
                                       'tocDepth: 1};</script>'

                    content = '<meta charset="utf-8">' + '\n'
                    content += input_md.read_text(encoding='utf-8') + '\n'

                    content += '\n'
                    content += markdeep_footer
                    output_html.write_text(content, encoding='utf-8')
                else:
                    print(f'Unknown mode: {mode}')
                    sys.exit(1)

            except FileNotFoundError as e:
                print("pandoc can't be found on the path. Install it & "
                      f"retry. (winget install pandoc)\n {e}")
                sys.exit(1)
            except Exception as e:
                print(f'Error during conversion: {e}')
                sys.exit(1)

            return html_file_name

        def replace_in_file(file: pathlib.Path, replacements):
            if not file.exists():
                print(f'File not found: {file.absolute()}')
                return
            if not file.is_file():
                print(f'{file.absolute()} is not a file.')
                return

            content: str = file.read_text(encoding='utf-8')
            print(f' Replacements in content:')
            for old_str, new_str in replacements:
                print(f'  "{old_str}" -> "{new_str}"')
                # content = content.replace(old_str, new_str)
                pattern = re.compile(re.escape(old_str), re.IGNORECASE)
                content = pattern.sub(new_str, content)
            file.write_text(content, encoding='utf-8')

        def make_links_relative(lib, html_file):
            print(f' Absolute links -> relative links')
            html = pathlib.Path(html_file)
            try:
                soup = BeautifulSoup(html.read_text(encoding='utf-8'),
                                     'html.parser')
                # Find all <a>, <link>, and <img> tags with href or src attributes
                tags = soup.find_all(['a', 'link', 'img'], href=True)
                # print(f"Processing {len(tags)} tags...")
                for tag in tags:
                    attribute = 'href' if 'href' in tag.attrs else 'src'
                    original_url = tag[attribute]

                    # Parse the original URL
                    parsed_url = urlparse(original_url)

                    # Check if the URL is absolute
                    if parsed_url.scheme or parsed_url.netloc:
                        # Make the URL relative to the HTML file's directory
                        if '/blob/main/' in original_url or '/raw/main/' in original_url:
                            p = original_url
                            p = p.replace('/blob/main/', '/')
                            p = p.replace('/raw/main/', '/')
                            p = p.replace(lib.catalog_url + '/', '')
                            p = p.replace(lib.catalog_url.lower() + '/', '')
                            p = unquote(p)
                            p = p.replace('/', '\\')

                            p2 = pathlib.Path.joinpath(lib.root_dir, p)
                            f_html: pathlib.Path = pathlib.Path(html_file)
                            f_link: pathlib.Path = pathlib.Path(p2)

                            relative_url = '.\\{0}\\{1}'.format(
                                str(os.path.relpath(f_link.parent,
                                                    f_html.parent)),
                                # str(f_link.parent.relative_to(f_html.parent)),
                                f_link.name)
                            relative_url = relative_url.replace('\\', '/')
                            relative_url = quote(relative_url)
                            # print(
                            #     f"\n{html_file}:\n {original_url} -> "
                            #     f"\n{relative_url}\n")
                            tag[attribute] = relative_url
                        else:
                            print(
                                f"Help me: Unable to make link {original_url} relative.")
                            # sys.exit(1)

                # Write the modified content back to the HTML file
                with open(html_file, 'w', encoding='utf-8') as file:
                    file.write(str(soup))
            except FileNotFoundError:
                print(f'File not found: {html_file}')

        md_files = self.root_dir.rglob('*.md')
        for md_file in md_files:
            if not md_file.is_file(): continue
            f = str(md_file.relative_to(self.root_dir)).replace("\b", "/")
            print(f'\nProcessing {f}:')
            tmp_name = str(md_file.absolute()) + ".tmp.md"
            md_file_tmp = pathlib.Path(tmp_name)
            shutil.copy2(md_file.absolute(), md_file_tmp)

            # prepare file: .md -> .html

            # if '/_tags/' in str(md_file_tmp.absolute()):

            mode = 'markdeep'
            mode = 'pandoc'
            replacements = [
                ('.md', '.html'),
            ]
            replace_in_file(md_file_tmp, replacements=replacements)
            html = md_to_html(md_file_tmp.absolute(), mode=mode)
            make_links_relative(self, html)
            md_file_tmp.unlink()

            # pandoc: md -> html
            if delete_markdown:
                md_file.unlink()
