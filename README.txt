labMT-simple
============

TL;DR a simple labMT usage script

This script uses the language assessment by Mechanical Turk (labMT) word
list to score the happiness of a corpus. The labMT word list was created
by combining the 5000 words most frequently appearing in four sources:
Twitter, the New York Times, Google Books, and music lyrics, and then
scoring the words for sentiment on Amazon's Mechanical Turk. The list is
described in detail in the publication Dodds' et al. 2011, PLOS ONE,
"Temporal Patterns of Happiness and Information in a Global-Scale Social
Network: Hedonometrics and Twitter."

Given two corpora, the script "storylab.py" creates a word-shift graph
illustrating the words most responsible for the difference in happiness
between the two corpora. The corpora should be large (e.g. at least
10,000 words) in order for the difference to be meaningful, as this is a
bag-of-words approach. As an example, a random collection of English
tweets from both Saturday January 18 2014 and Tuesday January 21 2014
are included in the "example" directory. They can be compared by moving
to the test directory, using the command

.. code:: python

    python example.py example-shift.html

and opening the file ``example-shift.html`` in a web browser. For an
explanation of the resulting plot, please visit

http://www.hedonometer.org/shifts.html

Installation
------------

Cloning the github directly is recommended, i.e.

.. code:: bash

    git clone https://github.com/andyreagan/labMT-simple.git

and then installing locally using

.. code:: bash

    sudo python setup.py install

Tests can be run by navigating to the test directory, and running

.. code:: bash

    python test.py

which will compare the two days in test/data and print test.html which
shifts them, allowing for a changable lens.

This repository can also be installed using pip

.. code:: bash

    pip install labMTsimple

in which case you can download the tests from github and run them, if
desired.
