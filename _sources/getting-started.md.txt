Getting Started
============

TL;DR
a simple labMT usage script

Usage
-----

This script uses the language assessment by Mechanical Turk (labMT) word list to score the happiness of a corpus. The labMT word list was created by combining the 5000 words most frequently appearing in four sources: Twitter, the New York Times, Google Books, and music lyrics, and then scoring the words for sentiment on Amazon's Mechanical Turk. The list is described in detail in the publication Dodds' et al. 2011, PLOS ONE, "Temporal Patterns of Happiness and Information in a Global-Scale Social Network: Hedonometrics and Twitter."

Given two corpora, the script "storylab.py" creates a word-shift graph illustrating the words most responsible for the difference in happiness between the two corpora. The corpora should be large (e.g. at least 10,000 words) in order for the difference to be meaningful, as this is a bag-of-words approach. As an example, a random collection of English tweets from both Saturday January 18 2014 and Tuesday January 21 2014 are included in the "example" directory. They can be compared by moving to the test directory, using the command

```python
python example.py example-shift.html
```

and opening the file `example-shift.html` in a web browser. For an explanation of the resulting plot, please visit

[http://www.hedonometer.org/shifts.html](http://www.hedonometer.org/shifts.html)


Installation
------------

Cloning the github directly is recommended, and then installing locally:

```bash
git clone https://github.com/andyreagan/labMT-simple.git
cd labMT-simple
python setup.py install
```

This repository can also be installed using pip

```bash
pip install labMTsimple
```

in which case you can download the tests from github and run them, if desired.


Running tests
-------------

Tests are based on nose2, `pip install nose2`, and can be run inside the by executing

```bash
nose2
```

in the root directory of this repository.

This will compare the two days in test/data and print test.html which shifts them, allowing for a changable lens.

Developing with labMT-simple locally
------------------------------------

I find it really useful to reload the library when testing it interactively:

```python
try:
    reload
except NameError:
    # Python 3
    from importlib import reload
```

Building these docs
-------------------

Go into the docs directory (activate local `virtualenv` first), and do the following:
```
\rm -rf _build/*
make html
make latexpdf
git add -f *
git commit -am "new docs, probably should just add a pre-commit hook"
```

Note that these docs will build locally in python 2 because the dependencies exist.
With python 3 available, these dependencies will be mocked (and this is set for the online readthedocs site).

(`sphinx-apidoc -o . ../labMTsimple` was run once.)
