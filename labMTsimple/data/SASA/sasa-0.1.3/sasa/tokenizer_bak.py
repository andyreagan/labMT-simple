#!/usr/bin/env python

""" This class wraps Christopher Potts' twitter aware-tokenizer, which he
graciously provided under apache licence to meet the license of this project"""

__author__ = "Dogan Can, Abe Kazemzadeh, Hao Wang"
__copyright__ = "Copyright 2013, University of Southern California"
__credits__ = []
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"
__maintainer__ = "Last modified by Abe Kazemzadeh"
__email__ = "See the authors' website"

import sys
import codecs
import json
from happyfuntokenizing import Tokenizer

def tokenize(tweet):
    global tokenizer

    try:
        text = codecs.decode(tweet, "utf-8").strip()
        if not text: return None # blank line
        print text
        text = tokenizer.tokenize(text)
        return codecs.encode(u" ".join(text), "utf-8")
    except Exception, err:
        print >> sys.stderr, err
        print >> sys.stderr, tweet
        return None

def init(preserve_case=True):
    global tokenizer
    tokenizer = Tokenizer(preserve_case=preserve_case)

if __name__ == "__main__":
    init()
    for tweet in sys.stdin:
        text = tokenize(tweet)
        if text is None:
            text = "NONE"
        print text
