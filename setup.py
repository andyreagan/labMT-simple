from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = 'labMTsimple',
    packages = ['labMTsimple'],
    package_data={'labMTsimple': ['data/labMT/*.txt','data/PANAS-X/*.txt','data/warriner/*.csv','data/ANEW/all.csv','data/MPQA-lexicon/subjectivity_clues_hltemnlp05/*.tff','data/liu-lexicon/*-clean.txt','static/d3.andy.js','static/jquery-1.11.0.min.js','static/urllib.js','static/hedotools.init.js','static/hedotools.shifter.js','static/example-on-load.js','static/example-on-load-self.js','static/hedotools.shift.css']},
    version = '2.3.4.4',
    description = 'Basic usage script for dictionary-based sentiment analysis. Intended use with labMT data',
    long_description = long_description,
    author = 'Andy Reagan',
    author_email = 'andy@andyreagan.com',
    url = 'https://github.com/andyreagan/labMT-simple', 
    download_url = 'https://github.com/andyreagan/labMT-simple/tarball/2.3.1.5',
    keywords = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python'],
    )





