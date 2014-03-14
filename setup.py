from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = 'labMTsimple',
    packages = ['labMTsimple'],
    package_data={'labMTsimple': ['labMT1.txt']},
    data_files=[('test', ['test/shiftPlot.html','test/18.01.14.txt','test/21.01.14.txt'])],
    version = '0.3.1',
    description = 'Basic usage script for LabMT1.0 dataset',
    long_description = long_description,
    author = 'Andy Reagan',
    author_email = 'andy@andyreagan.com',
    url = 'https://github.com/andyreagan/labMT-simple', 
    download_url = 'https://github.com/andyreagan/labMT-simple/tarball/0.3',
    keywords = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python'],
    )

