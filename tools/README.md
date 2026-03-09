[Catalog](https://github.com/BercziSandor/calibre_lib/blob/main/catalog.md)



https://stackoverflow.com/questions/45237819/python-parsing-xml-opf-file
	from xml.etree import ElementTree as ET

	tree = ET.parse('content.opf')
	title = tree.find(".//{http://purl.org/dc/elements/1.1/}title")
	print(title.text)


https://gitlab.com/LazyLibrarian/LazyLibrarian
https://github.com/BercziSandor/calibre/blob/master/src/calibre/ebooks/metadata/opf3.py
