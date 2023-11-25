import logging
import os
import pathlib
import sys
from datetime import datetime
from xml.etree import ElementTree as ET

import Library

NAMESPACES = {
    'None': "http://www.idpf.org/2007/opf",
    'dc': "http://purl.org/dc/elements/1.1/",
    'opf': "http://www.idpf.org/2007/opf",
}
BOOK_EXTENSIONS = ['.epub', '.pdf', '.djvu', '.prc', '.rtf', '.azw3']


class Opf:

    def __init__(self, path: str, repo_url: str,
                 library: Library,
                 basedir=os.getcwd()):
        self.orig = path
        self._basedir = basedir
        self.repo_url = repo_url,
        self.library = library,
        if not os.path.isabs(path):
            self.path = pathlib.Path(os.path.abspath(os.path.join(basedir,
                                                                  path)))
        else:
            self.path = pathlib.Path(os.path.join(basedir,
                                                  path))
        if not os.path.exists(self.path):
            sys.exit(1)
        self.load_info()
        self.load_download_links()

    def __str__(self):
        return f"{self.creator}: " \
               f"{self.title} " \
               f"{'(' + self.series + ' ' if self.series else ''}" \
               f"{str(self.series_index) + ') ' if self.series_index else ''}" \
               f"{'(' + str(self.dt.year) + ')' if self.dt.year > 101 else ''}"

    def get_tag_link(self, subj):
        tag_file_link = self.library[0].catalog_url + f"/_details/_tags/{subj}"
        return f"[{subj}]({tag_file_link})"

    def get_md_details(self):
        md_details = ""
        md_details += f"# <a name=\"id_{self.id}\">{self}</a>\n"
        if len(self.covers) > 0:
            cover_url = self.library[0].get_url(self.covers[0])
            cover_link = f"![cover]({cover_url})"
            cover_link = f'<img src="{cover_url}" alt="cover" width="300"/>'
            md_details += f"{cover_link}\n\n"

        if len(self.download_links) > 0:
            md_details += "### Letöltés\n"
            md_details += " \n ".join(self.download_links)
            md_details += "\n\n"

        if len(self.subjects) > 0:
            md_details += "### Tagek\n"
            t = ', '.join(self.get_tag_link(subj) for subj in
                          self.subjects)
            md_details += t.lower()
            md_details += "\n\n"

        if self.description:
            md_details += f"### Összefoglalás\n"
            md_details += f"{self.description}\n"
            md_details += "\n\n"

        return md_details

    def load_info(self):
        tree = ET.parse(self.path)

        # <dc:identifier opf:scheme="calibre" id="calibre_id">962</dc:identifier>
        self.id = int(tree.find(".//{" + NAMESPACES['dc'] + "}identifier").text)

        self.title = tree.find(".//{" + NAMESPACES['dc'] + "}title").text
        self.creator = tree.find(".//{" + NAMESPACES['dc'] + "}creator").text

        description = tree.find(".//{" + NAMESPACES['dc'] + "}description")
        if description != None:
            self.description = description.text
        else:
            self.description = ""

        language = tree.find(".//{" + NAMESPACES['dc'] + "}language")
        if language: self.language = language.text

        dt = tree.find(".//{" + NAMESPACES['dc'] + "}date")
        if dt is not None:
            dt_str = dt.text
            if "." in dt_str:
                # 2015-06-04T14:29:48.577000+00:00
                DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
            else:
                # 2015-05-24T22:00:00+00:00
                DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
            self.dt = datetime.strptime(dt_str, DATE_FORMAT)

        subjects = tree.findall(".//{" + NAMESPACES['dc'] + "}subject")
        self.subjects = [x.text for x in subjects]

        # Covers
        covers = tree.findall(".//{" + NAMESPACES['None'] + "}reference["
                                                            "@type='cover']")
        self.covers = []
        if covers:
            for cover in covers:
                coverFile = pathlib.Path(os.path.abspath(os.path.join(
                    self.path.parent, cover.attrib['href'])))
                if not coverFile.exists():
                    logging.warning(f"Cover file '{coverFile}' "
                                    f"does not exist.")
                    continue
                self.covers.append(coverFile)
            # self.covers = [x.attrib['href'] for x in covers]

        # <meta name="calibre:series" content="Millennium"/>
        self.series = None
        series = tree.find(".//{" + NAMESPACES['None']
                           + "}meta[@name='calibre:series']")
        if series is not None:
            self.series = series.attrib['content']

        # <meta name="calibre:series_index" content="4"/>
        self.series_index = None
        series_index = tree.find(".//{" + NAMESPACES['None']
                                 + "}meta[@name='calibre:series_index']")
        if series_index is not None:
            d = series_index.attrib['content']
            if '.' in d:
                d = float(d)
            else:
                d = int(d)
            self.series_index = d

        # books
        self.books = []
        files = os.listdir(self.path.parent)
        for file in files:
            file_ext = pathlib.Path(file).suffix.lower()
            if file_ext not in BOOK_EXTENSIONS: continue
            path = pathlib.Path(os.path.abspath(os.path.join(
                self.path.parent, file)))
            self.books.append(path)

    def get_download_link(self, book):
        url = self.library[0].get_url(book)
        filename, file_extension = os.path.splitext(
            book)
        link_download = f"[{file_extension.replace('.', '')}]" \
                        f"({url})"
        return link_download

    def load_download_links(self):
        self.download_links = [self.get_download_link(
            book) for book in self.books]
