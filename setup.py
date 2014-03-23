from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = 'labMTsimple',
    packages = ['labMTsimple'],
    package_data={'labMTsimple': ['data/labMT1.txt','static/d3.v3.min.js','static/drawLens.js','static/plotShift.js','static/shift.js']},
    data_files=[('test', ['test/shiftPlot.html','test/data/18.01.14.txt','test/data/21.01.14.txt','test/shift.js','test/drawLens.js','test/plotShift.js'])],
    version = '1.2',
    description = 'Basic usage script for LabMT1.0 dataset',
    long_description = long_description,
    author = 'Andy Reagan',
    author_email = 'andy@andyreagan.com',
    url = 'https://github.com/andyreagan/labMT-simple', 
    download_url = 'https://github.com/andyreagan/labMT-simple/tarball/1.2',
    keywords = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python'],
    )


