#!/usr/bin/env python

from __future__ import division
from collections import defaultdict
import sys
import re
import json
import os, errno
import nltk
import codecs
import pickle
import traceback

__author__ = "Abe Kazemzadeh, Dogan Can, Hao Wang"
__version__ = "$Revision: 1 $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) University of Southern California"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__maintainer__ = "Last modified by Abe Kazemzadeh"
__email__ = "See the authors' website"

import gflags as flags
FLAGS=flags.FLAGS

from htmlentitydefs import name2codepoint
# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39
debug = False # if True, the model won't be loaded, 0 will be assigned to all tweets, .

def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

#def tokenize(line):
#    return line.lower().split()

def features(tweet, n):
    feats = defaultdict(bool)
    words = ['<s>'] + tweet[u'tokens'] + ['</s>']
    for i in range(len(words)):
        for j in range(i + 1, i + n + 1):
            feat = " ".join(words[i:j])
            feats[feat] = True
    return feats

def init(modelfile="model.naivebayes-bool-simple-1"):
    global classifier
    
    # print init message and version number
    match = re.match('\$Revision:\s+(.*?)\s+\$', __version__)
    if match != None:
        ver = match.group(1)
    else:
        ver = __version__
    sys.stderr.write("init sentiment python script version " + ver + '\n')
    
    if debug: return

    # read model from file
    modelpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), modelfile)    
    f = open(modelpath)
    classifier = pickle.load(f)
    f.close()

# input: tweet in json
def getSentiment(tweet_json):
    try:
#        print >> sys.stderr, 'sentiment before decode', type(tweet_json), tweet_json
        tweet = codecs.decode(tweet_json, 'utf-8', "replace")
#        print >> sys.stderr, 'sentiment after decode', type(tweet_json), tweet_json
        t = json.loads(tweet)

        if debug:
            t['valence'] = 0
            t['sentiment_classification'] = 'pos'
            return codecs.encode(json.dumps(t), 'utf-8')
    except Exception, err:
        traceback.print_exc()
        print >> sys.stderr, 'sentiment len =', len(tweet_json), ' text =', tweet_json
        return None
    text = t[u'text']
    # Process input text
    text = unescape(text)#.encode('utf8'))                            # encode unicode chars in utf8, 

    #print text
    labels = sorted(classifier.labels())
    feat = features(t,1) #1 refers to unigram
    hyp = classifier.classify(feat) 
    classprobs = classifier.prob_classify(feat) 
    if hyp == 'negative':
        valence = - classprobs.prob('negative')
    elif hyp == 'positive':
        valence = classprobs.prob('positive')
    else:
        valence = 0

    t['valence'] = valence # "%f" % (valence)
    t['sentiment_classification'] = hyp
    #t['ratings'] = " ".join(["%s[%.2f]" % (s + w, r) for w, s, r in zip(words, word_status, ratings)])
    return codecs.encode(json.dumps(t), 'utf-8')
    
##==================================================================================================
## MAIN
##==================================================================================================

if __name__ == "__main__":
    
    flags.DEFINE_string("model_path", "model.naivebayes-bool-simple-1", "pickled naive bayes model")
    
    argv = FLAGS(sys.argv)
    
    init(FLAGS.model_path)
    for t in sys.stdin:
        t = codecs.decode(t, 'utf-8')
        t = t.strip()
        if not t: continue
        t = getSentiment(t)
        if t != None:
            print codecs.encode(t, 'utf-8')
