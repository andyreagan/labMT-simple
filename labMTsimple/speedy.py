# speedy.py
# a mostly futile attempt to speed up the sentiment analysis of text using
# dictionary-based approach

# now runs inside of labMTsimple

# future upgrade: subclass each of the different dictionaries
# then pull in all of the storyLab functions!

# most of these dependencies I don't need, so I've commented them out
# import re
import codecs
# from os import listdir
from os import mkdir
from os.path import isfile,abspath,isdir
import sys
# handle both pythons
if sys.version < '3':
    import codecs
    def u(x):
        """Python 2/3 agnostic unicode function"""
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        """Python 2/3 agnostic unicode function"""
        return x
# import matplotlib.pyplot as plt
from numpy import zeros,array
# from json import loads
# import csv
# import datetime
# memory efficient, but a bit slower
# also, static
import marisa_trie
# faster, still better memory than dict
# both allow prefix search
import datrie
# import string

class sentiDict(object):
    """An abstract class to score them all."""

    # datastructure = ''
    
    def openWithPath(self,filename,mode):
        """Helper function for searching for files."""
        try:
            f = codecs.open(filename,mode,'utf8')
            return f
        except IOError:
            relpath = abspath(__file__).split(u'/')[:-1]
            # relpath.append('data')
            relpath.append(filename)
            filename = '/'.join(relpath)
            f = codecs.open(filename,mode,'utf8')
            return f
        except:
            raise('could not open the needed file')

    def bootstrapify(self):
        """Extend the lists without stems to include stems."""
        if self.corpus in ['LabMT','ANEW']:
            oldcorpus = self.corpus
            # go get the stem sets to extend
            self.corpus = 'LIWC'
            self.data = self.loadDict()
            # make lists from it
            self.makeListsFromDict()
            # create the trie
            LIWCtrie = self.makeMarisaTrie()
            self.corpus = 'MPQA'
            self.data = self.loadDict()
            # make lists from it
            self.makeListsFromDict()
            # create the trie
            MPQAtrie = self.makeMarisaTrie()
            self.corpus = oldcorpus

        if self.corpus not in ['LabMT','ANEW']:
            pass
            # go get the other +/- 1 sets and add
            # only keep the ones that agree
            # check agreement on everything
            # add stems, then add fixed (if not in stems)

    data = dict()
    """Declare this globally."""

    def makeListsFromDict(self):
        """Make lists from a dict, used internally."""
        tmpfixedwords = []
        tmpfixedscores = []
        # add something to store the additional info
        # only captures a third entry, if it exists
        tmpfixedother = []
        
        tmpstemwords = []
        tmpstemscores = []
        tmpstemother = []
        
        for key,score in self.data.items():
            if key[-1] == "*" and not key[-2] == "*":
                tmpstemwords.append(key.replace("*",""))
                tmpstemscores.append(score[0])
                if len(score) > 2:
                    tmpstemother.append(score[2])
            else:
                tmpfixedwords.append(key)
                tmpfixedscores.append(score[0])
                if len(score) > 2:
                    tmpfixedother.append(score[2])
        if self.corpus in ['LabMT','ANEW']:
            # keep the original sort in this case
            stemindexer = []
            fixedindexer = sorted(range(len(tmpfixedwords)), key=lambda k: self.data[tmpfixedwords[k]][1])
        elif self.corpus in ['Warriner']:
            # sort alphabetically
            # (sorting by happiness is ambiguous sometimes)
            stemindexer = []
            fixedindexer = sorted(range(len(tmpfixedscores)), key=lambda k: tmpfixedwords[k])
        else:
            # sort alphabetically
            stemindexer = sorted(range(len(tmpstemscores)), key=lambda k: tmpstemwords[k])
            fixedindexer = sorted(range(len(tmpfixedscores)), key=lambda k: tmpfixedwords[k])
        # sort them
        self.stemwords = [tmpstemwords[i] for i in stemindexer]
        self.stemscores = [tmpstemscores[i] for i in stemindexer]
        if len(tmpstemother) > 0:
            self.stemother = [tmpstemother[i] for i in stemindexer]
        else:
            self.stemother = tmpstemother            
        self.fixedwords = [tmpfixedwords[i] for i in fixedindexer]
        self.fixedscores = [tmpfixedscores[i] for i in fixedindexer]
        if len(tmpfixedother) > 0:
            self.fixedother = [tmpfixedother[i] for i in fixedindexer]
        else: 
            self.fixedother = tmpfixedother
        # now, go reset the dict with these new orders
        for i,word in enumerate(self.fixedwords):
            # will add back in just a third entry, if it had existed
            # entires beyond that are destroyed
            if len(self.fixedother) > 0:
                self.data[word] = (self.data[word][0],i,self.data[word][2])
            else:
                self.data[word] = (self.data[word][0],i)
        for i,word in enumerate(self.stemwords):
            if word in self.data:
                self.data[word] = (self.data[word][0],i)
            else:
                self.data[word+"*"] = (self.data[word+"*"][0],i)

        # build the full vectors
        self.wordlist = self.fixedwords + [word+"*" for word in self.stemwords]
        self.scorelist = array(self.fixedscores + self.stemscores)

    def makeMarisaTrie(self,save_flag=False):
        """Turn a dictionary into a marisa_trie."""
        fmt = "fH"
        fixedtrie = marisa_trie.RecordTrie(fmt,zip(map(u,self.fixedwords),zip(self.fixedscores,range(len(self.fixedscores)))))
        stemtrie = marisa_trie.RecordTrie(fmt,zip(map(u,self.stemwords),zip(self.stemscores,range(len(self.fixedscores),len(self.fixedscores)+len(self.stemscores)))))
        if save_flag:
            fixedtrie.save('{0}/{1:.2f}-fixed.marisa'.format(self.folder,self.stopVal))
            stemtrie.save('{0}/{1:.2f}-stem.marisa'.format(self.folder,self.stopVal))
        return (fixedtrie,stemtrie)

    def matcherTrieBool(self,word):
        """MatcherTrieBool(word) just checks if a word is in the list.
        Returns 0 or 1.

        Works for both trie types.
        Only one needed to make the plots.
        Only use this for coverage, so don't even worry about using with a dict."""
        if word in self.data[0]:
            return 1
        else:
            return len(self.data[1].prefixes(word))

    def matcherDictBool(self,word):
        """MatcherTrieDict(word) just checks if a word is in the dict."""
        return (word in self.data)

    def stopper(self,tmpVec,stopVal=1.0,ignore=[]):
        """Take a frequency vector, and 0 out the stop words.
  
        Will always remove the nig* words.
  
        Return the 0'ed vector."""

        ignoreWords = {u"nigga": 1, u"nigger": 1, u"niggaz": 1, u"niggas": 1}
        for word in ignore:
            ignoreWords[u(word)] = 1

        newVec = tmpVec

        newVec[abs(self.scorelist-self.center) < stopVal] = 0

        ignore_vector = self.wordVecify(ignoreWords)
        newVec[ignore_vector > 0] = 0

        return newVec

    def wordVecifyTrieMarisa(self,wordDict):
        """Make a word vec from word dict using marisa_trie backend.

        INPUTS:\n
        -wordDict is our favorite hash table of word and count."""
        wordVec = zeros(len(self.data[0])+len(self.data[1]))
        for word,count in wordDict.items():
            if word in self.data[0]:
                wordVec[self.data[0].get(word)[0][1]] += count
            # this strictly assumes that the keys in the stem set
            # are non-overlapping!
            # also they'll match anything after the word, not just [a-z']
            elif len(self.data[1].prefixes(word)) > 0:
                wordVec[self.data[1].get(self.data[1].prefixes(word)[0])[0][1]] += count
        return wordVec

    def wordVecifyTrieDict(self,wordDict):
        """Make a word vec from word dict using dict backend.

        INPUTS:\n
        -wordDict is our favorite hash table of word and count."""
        wordVec = zeros(len(self.data))
        for word,count in wordDict.items():
            if word in self.data:
                wordVec[self.data[word][1]] += count
        return wordVec

    def scoreTrieMarisa(self,wordDict):
        """Score a wordDict using the marisa_trie backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.data[0]:
                totalcount += count
                totalscore += count*self.data[0].get(word)[0][0]
            elif (len(self.data[1].prefixes(word)) > 0):
                totalcount += count
                totalscore += count*self.data[1].get(self.data[1].prefixes(word)[0])[0][0]
        return totalscore/totalcount

    def scoreTrieDict(self,wordDict):
        """Score a wordDict using the dict backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.data:
                totalcount += count
                totalscore += count*self.data[word][0]
        if totalcount > 0:
            return totalscore/totalcount
        else:
            return 0.0

    def matcherTrieMarisa(self,word,wordVec,count):
        """Not sure what this one does."""
        if word in self.data[0]:
            wordVec[self.data[0].get(word)[0][1]] += count
        # this strictly assumes that the keys in the stem set
        # are non-overlapping!
        # also they'll match anything after the word, not just [a-z']
        elif len(self.data[1].prefixes(word)) > 0:
            wordVec[self.data[1].get(self.data[1].prefixes(word)[0])[0][1]] += count

    def matcherTrieDict(self,word,wordVec,count):
        """Not sure what this one does."""
        if word in self.data:
            wordVec[self.data[word][1]] += count

    def __init__(self,datastructure='dict',bootstrap=False,stopVal=0.0,bananas=False,loadFromFile=False,saveFile=False):
        """Instantiate the class."""
        self.stopVal = stopVal
        self.datastructure = datastructure
        print("loading {0} {1} with stopVal={2}".format(self.title,datastructure,stopVal))
        if saveFile:
            if not isdir('{0}'.format(self.folder)):
                mkdir('{0}'.format(self.folder))
        if datastructure == 'dict':
            self.data = self.loadDict(bananas)
            if bootstrap:
                self.bootstrapify()
            self.makeListsFromDict()
            self.matcher = self.matcherTrieDict
            self.matcherBool = self.matcherDictBool
            self.score = self.scoreTrieDict
            self.wordVecify = self.wordVecifyTrieDict

        if datastructure == 'marisatrie':
            fmt = "fH"
            if isfile('{0}/{1:.2f}-fixed.marisa'.format(self.folder,stopVal)) and loadFromFile:
                self.data = (marisa_trie.RecordTrie(fmt,[]),marisa_trie.RecordTrie(fmt,[]))
                self.data[0].load('{0}/{1:.2f}-fixed.marisa'.format(self.folder,stopVal))
                self.data[1].load('{0}/{1:.2f}-stem.marisa'.format(self.folder,stopVal))
            else:
                # load up the dict
                self.data = self.loadDict(bananas)
                # make lists from it
                self.makeListsFromDict()
                # create the trie
                self.data = self.makeMarisaTrie()

            self.matcher = self.matcherTrieMarisa
            self.matcherBool = self.matcherDictBool
            self.score = self.scoreTrieMarisa
            self.wordVecify = self.wordVecifyTrieMarisa

class LabMT(sentiDict):
    """LabMT class."""

    folder = 'labMT'
    title = 'LabMT'
    center = 5.0
    corpus = 'LabMT'
    stems = False
    score_range = 'full'

    def loadDict(self,bananas):
        # don't cheat
        LabMT = dict()
        f = self.openWithPath("data/labMT/labMT2english.txt","r")
        f.readline()
        i = 0
        for line in f:
            l = line.rstrip().split("\t")
            LabMT[l[0]] = (float(l[2]),i,float(l[3]))
            i=i+1
        f.close()
        stopWords = []
        for word in LabMT:
            if abs(LabMT[word][0]-self.center) < self.stopVal:
                stopWords.append(word)
        for word in stopWords:
            del LabMT[word]
        # print(LabMT["happy"])
        return LabMT

class ANEW(sentiDict):
    """An abstract class to score them all."""

    # these are the global lists
    folder = 'ANEW'
    title = 'ANEW'
    center = 5.0
    corpus = 'ANEW'
    stems = False
    score_range = 'full'

    def loadDict(self,bananas):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        ANEW = dict()
        f = self.openWithPath("data/ANEW/all.csv","r")
        f.readline()
        i = 0
        for line in f:
            l = line.rstrip().split(",")
            ANEW[l[0]] = (float(l[2]),i,float(l[3]))
            i+=1
        f.close()
        # stop the thing too
        stopWords = []
        for word in ANEW:
            if abs(ANEW[word][0]-self.center) < self.stopVal:
                stopWords.append(word)
        for word in stopWords:
            del ANEW[word]
        return ANEW

class LIWC(sentiDict):
    """An abstract class to score them all."""

    # these are the global lists
    folder = 'LIWC'
    title = 'LIWC'
    center = 0.0
    corpus = 'LIWC'
    stems = True
    score_range = 'integer'
    
    def loadDict(self,bananas):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        # many (most) of these words are stems
        # so we'll need to deal with this in applying it
        LIWC = dict()
        # all the 125's pulled out
        # f = self.openWithPath("data/LIWC/LIWC2007_English100131_words.dic","r")
        # mostly just the raw data
        f = self.openWithPath("data/LIWC/LIWC2007_English100131_words.dic","r")
        i = 0
        for line in f:
            l = line.rstrip().split("\t")
            word = l[0]
            if word not in LIWC:
                # affect word
                if '125' in l:
                    # posititive
                    if '126' in l:
                        score = 1
                        if word in LIWC:
                            print(word)
                        LIWC[word] = (score,i)
                        i+=1
                    # negative
                    elif '127' in l:
                        score = -1
                        LIWC[word] = (score,i)
                        i+=1
                # get the words that are "function" words (1)
                # specifically not getting them with emotion
                # if the bananas is false
                elif self.stopVal == 0.0 and '1' in l and not bananas:
                    score = 0
                    if word in LIWC:
                        print(word)
                    LIWC[word] = (score,i)
                    i+=1
                # but if bananas, put them neutral regardless of affect!
                elif self.stopVal == 0.0 and '1' in l and bananas:
                    score = 0
                    if word in LIWC:
                        print(word)
                    LIWC[word] = (score,i)
                    i+=1
            else:
                print("already in LIWC: {0}".format(word))
        f.close()
        return LIWC

class MPQA(sentiDict):
    # these are the global lists
    folder = 'MPQA-lexicon'
    title = 'MPQA'
    center = 0.0
    corpus = 'MPQA'
    stems = True
    score_range = 'integer'
    
    def loadDict(self,bananas):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        MPQA = dict()
        scores = [-1,0,1]
        emotions = ["negative","neutral","positive"]
        f = self.openWithPath("data/MPQA-lexicon/subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.tff","r")
        i = 0
        num_duplicates = 0
        for line in f:
            l = [x.split("=")[1] for x in line.rstrip().split(" ")]

            if (l[4]=="y"):
                l[2] += '*'

            if l[5] == 'both':
                l[5] = "neutral"
            # check that no words are different polarity when duplicated
            # and if they are, delete, set to neutral
            if l[2] in MPQA:
                if not MPQA[l[2]][0] == scores[emotions.index(l[5])]:
                    # print("{0} has emotion {1} and {2}".format(l[2],MPQA[l[2]][0],scores[emotions.index(l[5])]))
                    num_duplicates += 1
                    MPQA[l[2]] = (0,MPQA[l[2]][1])
            else:
                MPQA[l[2]] = (scores[emotions.index(l[5])],i)
                i+=1
        f.close()
        stopWords = []
        if self.stopVal > 0.0:
            for word in MPQA:
                if MPQA[word] == 0.0:
                    stopWords.append(word)
            for word in stopWords:
                del MPQA[word]
        # print("MPQA duplicates: {0}".format(num_duplicates))
        return MPQA

class Liu(sentiDict):
    folder = 'liu-lexicon'
    title = 'Liu'
    center = 0.0
    corpus = 'Liu'
    stems = False
    score_range = 'integer'
    
    def loadDict(self,bananas):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        liu = dict()
        f = self.openWithPath("data/liu-lexicon/negative-words.txt","r")
        i=0
        for line in f:
            l = line.rstrip()
            if l in liu:
                print(l)
            else:
                liu[l] = (-1,i)
                i+=1
        f.close()
        f = self.openWithPath("data/liu-lexicon/positive-words.txt","r")
        for line in f:
            l = line.rstrip()
            if l in liu:
                print(l)
            else:
                liu[l] = (1,i)
                i+=1
        f.close()
        return liu

class WK(sentiDict):
    folder = 'warriner'
    title = 'WK'
    center = 5.0
    corpus = 'WK'
    stems = False
    score_range = 'full'
    
    def loadDict(self,bananas):
        Warriner = dict()
        f = self.openWithPath("data/warriner/BRM-emot-submit.csv","r")
        f.readline()
        for line in f:
            l = line.rstrip().split(',')
            Warriner[l[1]] = (float(l[2]),int(l[0]),float(l[3]))
        f.close()
        stopWords = []
        for word in Warriner:
            if abs(Warriner[word][0]-self.center) < self.stopVal:
                stopWords.append(word)
        for word in stopWords:
            del Warriner[word]
        return Warriner

class PANASX(sentiDict):
    folder = 'PANAS-X'
    title = 'PANAS-X'
    center = 0.0
    corpus = 'PANAS-X'
    stems = False
    score_range = 'integer'
    
    def loadDict(self,bananas):
        PANAS = dict()
        f = self.openWithPath("data/PANAS-X/affect.txt","r")
        i=0
        for line in f:
            l = line.rstrip().split(',')
            PANAS[l[0]] = (int(l[1]),i)
            i+=1
        f.close()
        return PANAS
