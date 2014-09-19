from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = 'labMTsimple',
    packages = ['labMTsimple'],
    package_data={'labMTsimple': ['data/labMT1.txt','data/labMT1raw.txt','data/labMT2arabic.txt','data/labMT2english.txt','data/labMT2chinese.txt','data/labMT2french.txt','data/labMT2german.txt','data/labMT2hindi.txt','data/labMT2indonesian.txt','data/labMT2korean.txt','data/labMT2pashto.txt','data/labMT2portuguese.txt','data/labMT2russian.txt','data/labMT2spanish.txt','data/labMT2urdu.txt']},
    data_files=[('test', ['test/shiftPlot.html','test/data/18.01.14.txt','test/data/21.01.14.txt'])],
    version = '2.0',
    description = 'Basic usage script for LabMT1.0 dataset',
    long_description = long_description,
    author = 'Andy Reagan',
    author_email = 'andy@andyreagan.com',
    url = 'https://github.com/andyreagan/labMT-simple', 
    download_url = 'https://github.com/andyreagan/labMT-simple/tarball/2.0',
    keywords = [],
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python'],
    )


