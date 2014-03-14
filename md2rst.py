import pandoc
import os

pandoc.core.PANDOC_PATH = 'pandoc'

doc = pandoc.Document()
doc.markdown = open('README.md').read()
print doc.markdown
print doc.rst
f = open('README.txt','w')
f.write(doc.rst)
f.close()
