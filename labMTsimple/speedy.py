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
from numpy import zeros,array,min,max,dot
# from json import loads
# import csv
# import datetime
# memory efficient, but a bit slower
# also, static
import marisa_trie
# faster, still better memory than dict
# both allow prefix search
# import datrie
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
    fmt = "Hf"
    my_marisa = (marisa_trie.RecordTrie(fmt,[]),marisa_trie.RecordTrie(fmt,[]))
    """Declare this globally."""

    def makeListsFromDict(self):
        """Make lists from a dict, used internally."""
        tmpfixedwords = []
        tmpfixedscores = []
        
        tmpstemwords = []
        tmpstemscores = []
        
        for key,score in self.data.items():
            if key[-1] == "*" and not key[-2] == "*":
                tmpstemwords.append(key.replace("*",""))
                tmpstemscores.append(score[1])
            else:
                tmpfixedwords.append(key)
                tmpfixedscores.append(score[1])
        if self.corpus in ['LabMT','ANEW']:
            # keep the original sort in this case
            stemindexer = []
            fixedindexer = sorted(range(len(tmpfixedwords)), key=lambda k: self.data[tmpfixedwords[k]][0])
        else:
            # sort alphabetically
            stemindexer = sorted(range(len(tmpstemscores)), key=lambda k: tmpstemwords[k])
            fixedindexer = sorted(range(len(tmpfixedscores)), key=lambda k: tmpfixedwords[k])
        # sort them
        self.stemwords = [tmpstemwords[i] for i in stemindexer]
        self.stemscores = [tmpstemscores[i] for i in stemindexer]
        self.fixedwords = [tmpfixedwords[i] for i in fixedindexer]
        self.fixedscores = [tmpfixedscores[i] for i in fixedindexer]
            
        # now, go reset the dict with these new orders
        for i,word in enumerate(self.fixedwords):
            # will add back in just a third entry, if it had existed
            # entires beyond that are destroyed
            self.data[word] = tuple([i]+list(self.data[word][1:]))
        for i,word in enumerate(self.stemwords):
            if word in self.data:
                self.data[word] = tuple([i]+list(self.data[word][1:]))
            else:
                self.data[word+"*"] = tuple([i]+list(self.data[word+"*"][1:]))
                
        # build the full vectors
        self.wordlist = self.fixedwords + [word+"*" for word in self.stemwords]
        self.scorelist = array(self.fixedscores + self.stemscores)
        # get the range of the scores
        self.full_score_range = [min(self.scorelist),max(self.scorelist)]
        # check the number of unique scores
        my_set = {}
        map(my_set.__setitem__, self.scorelist, [])
        self.unique_scores = len(my_set.keys())

    def makeMarisaTrie(self,save_flag=False):
        """Turn a dictionary into a marisa_trie."""
        fmt = "Hf"
        fixedtrie = marisa_trie.RecordTrie(fmt,zip(map(u,self.fixedwords),zip(range(len(self.fixedscores)),self.fixedscores)))
        stemtrie = marisa_trie.RecordTrie(fmt,zip(map(u,self.stemwords),zip(range(len(self.fixedscores),len(self.fixedscores)+len(self.stemscores)),self.stemscores)))
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
        if word in self.my_marisa[0]:
            return 1
        else:
            return len(self.my_marisa[1].prefixes(word))

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
        wordVec = zeros(len(self.my_marisa[0])+len(self.my_marisa[1]))
        for word,count in wordDict.items():
            if word in self.my_marisa[0]:
                wordVec[self.my_marisa[0].get(word)[0][0]] += count
            # this strictly assumes that the keys in the stem set
            # are non-overlapping!
            # also they'll match anything after the word, not just [a-z']
            elif len(self.my_marisa[1].prefixes(word)) > 0:
                wordVec[self.my_marisa[1].get(self.my_marisa[1].prefixes(word)[0])[0][0]] += count
        return wordVec

    def wordVecifyTrieDict(self,wordDict):
        """Make a word vec from word dict using dict backend.

        INPUTS:\n
        -wordDict is our favorite hash table of word and count."""
        wordVec = zeros(len(self.data))
        for word,count in wordDict.items():
            if word in self.data:
                wordVec[self.data[word][0]] += count
        return wordVec

    def scoreTrieMarisa(self,wordDict):
        """Score a wordDict using the marisa_trie backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.my_marisa[0]:
                totalcount += count
                totalscore += count*self.my_marisa[0].get(word)[0][1]
            elif (len(self.my_marisa[1].prefixes(word)) > 0):
                totalcount += count
                totalscore += count*self.my_marisa[1].get(self.my_marisa[1].prefixes(word)[0])[0][1]
        if totalcount > 0:
            return totalscore/totalcount
        else:
            return self.center

    def scoreTrieDict(self,wordDict):
        """Score a wordDict using the dict backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.data:
                totalcount += count
                totalscore += count*self.data[word][1]
        if totalcount > 0:
            return totalscore/totalcount
        else:
            return 0.0

    def matcherTrieMarisa(self,word,wordVec,count):
        """Not sure what this one does."""
        if word in self.my_marisa[0]:
            wordVec[self.my_marisa[0].get(word)[0][0]] += count
        # this strictly assumes that the keys in the stem set
        # are non-overlapping!
        # also they'll match anything after the word, not just [a-z']
        elif len(self.my_marisa[1].prefixes(word)) > 0:
            wordVec[self.my_marisa[1].get(self.my_marisa[1].prefixes(word)[0])[0][0]] += count

    def matcherTrieDict(self,word,wordVec,count):
        """Not sure what this one does."""
        if word in self.data:
            wordVec[self.data[word][0]] += count

    def __init__(self,datastructure='dict',bootstrap=False,stopVal=0.0,bananas=False,loadFromFile=False,saveFile=False):
        """Instantiate the class."""
        self.stopVal = stopVal
        self.datastructure = datastructure
        if saveFile:
            if not isdir('{0}'.format(self.folder)):
                mkdir('{0}'.format(self.folder))
        if not self.stems and datastructure=="dict":
            self.data = self.loadDict(bananas)
            if bootstrap:
                self.bootstrapify()
            self.makeListsFromDict()
            self.matcher = self.matcherTrieDict
            self.matcherBool = self.matcherDictBool
            self.score = self.scoreTrieDict
            self.wordVecify = self.wordVecifyTrieDict
            self.datastructure = "dict"
        if self.stems or datastructure=="marisatrie":
            if isfile('{0}/{1:.2f}-fixed.marisa'.format(self.folder,stopVal)) and loadFromFile:
                print("loading from cache")
                self.my_marisa[0].load('{0}/{1:.2f}-fixed.marisa'.format(self.folder,stopVal))
                self.my_marisa[1].load('{0}/{1:.2f}-stem.marisa'.format(self.folder,stopVal))
            else:
                # load up the dict
                self.data = self.loadDict(bananas)
                # make lists from it
                self.makeListsFromDict()
                # create the trie
                self.my_marisa = self.makeMarisaTrie()

            self.matcher = self.matcherTrieMarisa
            self.matcherBool = self.matcherDictBool
            self.score = self.scoreTrieMarisa
            self.wordVecify = self.wordVecifyTrieMarisa
            self.datastructure = "marisatrie"
        print("loading {0} with stopVal={1}, for {2} words".format(self.title,stopVal,len(self.data)))

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
        # word    rank    happs   stddev  rank    rank    rank    rank
        i = 0
        for line in f:
            l = line.rstrip().split("\t")
            word,overallrank,happs,stddev,rank1,rank2,rank3,rank4 = l
            LabMT[word] = (i,float(happs),float(stddev))
            i+=1
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
    """ANEW class."""

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
        f = self.openWithPath("data/ANEW/all-2.csv","r")
        # f = self.openWithPath("data/ANEW/all.csv","r")
        # f.readline()
        # Description,Word No.,Valence Mean,Valence SD,Arousal Mean,Arousal SD,Dominance Mean,Dominance SD,Word Frequency
        # ["Description","Word_No","Valence_Mean","Valence_SD","Arousal_Mean","Arousal_SD","Dominance_Mean","Dominance_SD","Word_Frequency",]
        # description,word_no,valence_mean,valence_sd,arousal_mean,arousal_sd,dominance_mean,dominance_sd,word_frequency
        i = 0
        for line in f:
            # description,word_no,valence_mean,valence_sd,arousal_mean,arousal_sd,dominance_mean,dominance_sd,word_frequency = line.rstrip().split(",")
            description,word_no,valence_mean,valence_sd,arousal_mean,arousal_sd,dominance_mean,dominance_sd,word_frequency = line.rstrip().split("\t")
            ANEW[description] = (i,float(valence_mean),float(valence_sd))
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
    """LIWC class."""

    # these are the global lists
    folder = 'LIWC'
    title = 'LIWC'
    center = 0.0
    corpus = 'LIWC'
    stems = True
    score_range = 'integer'
    word_types = dict()
    
    def loadDict(self,bananas):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        word_type_dict = dict()
        f = self.openWithPath("data/LIWC/LIWC2007_English100131_header.dic","r")
        # leave space for index, happs_score
        i = 2
        for line in f:
            key,label = line.rstrip().split("\t")
            word_type_dict[int(key)] = (i,label)
            i+=1
        f.close()
        self.word_types = word_type_dict.copy()
        
        LIWC = dict()
        # mostly just the raw data (just no header)
        f = self.openWithPath("data/LIWC/LIWC2007_English100131_words.dic","r")
        print("loading data/LIWC/LIWC2007_English100131_words.dic")
        i = 0
        for line in f:
            l = line.rstrip().split("\t")
            word = l[0]
            # print(l[1:])
            if l[1] == "(02 134)125/464":
                tags = [2,134,125,464]
            else:
                tags = list(map(int,l[1:]))
            if word not in LIWC:
                LIWC[word] = [0 for j in range(len(word_type_dict)+2)]
                LIWC[word][0] = i
                # affect word
                if 125 in tags:
                    # posititive
                    if 126 in tags:
                        score = 1
                        LIWC[word][1] = score
                    # negative
                    elif 127 in tags:
                        score = -1
                        LIWC[word][1] = score
                for tag in tags:
                    LIWC[word][word_type_dict[tag][0]] = 1
                    
                # SORT THIS MESS OUT LATER
                # ...by adding all word types, the first score of 0
                # is now meaningless (if it had any meaning before...)
                #
                # # get the words that are "function" words (1)
                # # specifically not getting them with emotion
                # # if the bananas is false
                # elif self.stopVal == 0.0 and 1 in l and not bananas:
                #     score = 0
                #     if word in LIWC:
                #         print(word)
                #     LIWC[word][1] = score
                # # but if bananas, put them neutral regardless of affect!
                # elif self.stopVal == 0.0 and 1 in l and bananas:
                #     score = 0
                #     if word in LIWC:
                #         print(word)
                #     LIWC[word] = (i,score)
                
                i+=1
            else:
                # print("already in LIWC: {0}".format(word))
                pass
        f.close()
        stopWords = []
        if self.stopVal > 0.0:
            for word in LIWC:
                if LIWC[word][1] == 0.0:
                    stopWords.append(word)
            for word in stopWords:
                del LIWC[word]
        # print LIWC["like"]
        return LIWC

class MPQA(sentiDict):
    """MPQA class."""
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
            # type=weaksubj len=1 word1=abandoned pos1=adj stemmed1=n priorpolarity=negative
            l = [x.split("=")[1] for x in line.rstrip().split(" ")]
            if len(l) == 6:
                my_type,my_len,word,pos,stemmed,priorpolarity = l
            elif len(l) == 7:
                my_type,my_len,word,pos,stemmed,polarity,priorpolarity = l
                priorpolarity = polarity

            if (stemmed=="y"):
                word += '*'

            if priorpolarity == 'both':
                priorpolarity = "neutral"
                
            # check that no words are different polarity when duplicated
            # and if they are, delete, set to neutral
            if word in MPQA:
                if not MPQA[word][1] == scores[emotions.index(priorpolarity)]:
                    # # print all of this to see the duplicate words
                    # # when loading MPQA dictionary
                    # print("{0} has emotion {1} and {2}".format(word,MPQA[word][1],scores[emotions.index(priorpolarity)]))
                    # print(line.rstrip())
                    # print(MPQA[word][-1])
                    # print(" ")
                    num_duplicates += 1
                    MPQA[word] = (MPQA[word][0],0,line.rstrip())
                else:
                    # print("word duplicate but same score")
                    pass
            else:
                MPQA[word] = (i,scores[emotions.index(priorpolarity)],line.rstrip())
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
                # print(l)
                pass
            else:
                liu[l] = (i,-1)
                i+=1
        f.close()
        f = self.openWithPath("data/liu-lexicon/positive-words.txt","r")
        for line in f:
            l = line.rstrip()
            if l in liu:
                # print(l)
                pass
            else:
                liu[l] = (i,1)
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
        # ,Word,V.Mean.Sum,V.SD.Sum,V.Rat.Sum,A.Mean.Sum,A.SD.Sum,A.Rat.Sum,D.Mean.Sum,D.SD.Sum,D.Rat.Sum,V.Mean.M,V.SD.M,V.Rat.M,V.Mean.F,V.SD.F,V.Rat.F,A.Mean.M,A.SD.M,A.Rat.M,A.Mean.F,A.SD.F,A.Rat.F,D.Mean.M,D.SD.M,D.Rat.M,D.Mean.F,D.SD.F,D.Rat.F,V.Mean.Y,V.SD.Y,V.Rat.Y,V.Mean.O,V.SD.O,V.Rat.O,A.Mean.Y,A.SD.Y,A.Rat.Y,A.Mean.O,A.SD.O,A.Rat.O,D.Mean.Y,D.SD.Y,D.Rat.Y,D.Mean.O,D.SD.O,D.Rat.O,V.Mean.L,V.SD.L,V.Rat.L,V.Mean.H,V.SD.H,V.Rat.H,A.Mean.L,A.SD.L,A.Rat.L,A.Mean.H,A.SD.H,A.Rat.H,D.Mean.L,D.SD.L,D.Rat.L,D.Mean.H,D.SD.H,D.Rat.H
        # i,word,v_mean_sum,v_sd_sum,v_rat_sum,a_mean_sum,a_sd_sum,a_rat_sum,d_mean_sum,d_sd_sum,d_rat_sum,v_mean_m,v_sd_m,v_rat_m,v_mean_f,v_sd_f,v_rat_f,a_mean_m,a_sd_m,a_rat_m,a_mean_f,a_sd_f,a_rat_f,d_mean_m,d_sd_m,d_rat_m,d_mean_f,d_sd_f,d_rat_f,v_mean_y,v_sd_y,v_rat_y,v_mean_o,v_sd_o,v_rat_o,a_mean_y,a_sd_y,a_rat_y,a_mean_o,a_sd_o,a_rat_o,d_mean_y,d_sd_y,d_rat_y,d_mean_o,d_sd_o,d_rat_o,v_mean_l,v_sd_l,v_rat_l,v_mean_h,v_sd_h,v_rat_h,a_mean_l,a_sd_l,a_rat_l,a_mean_h,a_sd_h,a_rat_h,d_mean_l,d_sd_l,d_rat_l,d_mean_h,d_sd_h,d_rat_h
        for line in f:
            l = line.rstrip().split(',')
            i,word,v_mean_sum,v_sd_sum,v_rat_sum,a_mean_sum,a_sd_sum,a_rat_sum,d_mean_sum,d_sd_sum,d_rat_sum,v_mean_m,v_sd_m,v_rat_m,v_mean_f,v_sd_f,v_rat_f,a_mean_m,a_sd_m,a_rat_m,a_mean_f,a_sd_f,a_rat_f,d_mean_m,d_sd_m,d_rat_m,d_mean_f,d_sd_f,d_rat_f,v_mean_y,v_sd_y,v_rat_y,v_mean_o,v_sd_o,v_rat_o,a_mean_y,a_sd_y,a_rat_y,a_mean_o,a_sd_o,a_rat_o,d_mean_y,d_sd_y,d_rat_y,d_mean_o,d_sd_o,d_rat_o,v_mean_l,v_sd_l,v_rat_l,v_mean_h,v_sd_h,v_rat_h,a_mean_l,a_sd_l,a_rat_l,a_mean_h,a_sd_h,a_rat_h,d_mean_l,d_sd_l,d_rat_l,d_mean_h,d_sd_h,d_rat_h = l
            Warriner[word] = (int(i),float(v_mean_sum),float(v_sd_sum))
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
            word,score = l
            PANAS[word] = (i,int(score))
            i+=1
        f.close()
        return PANAS

class pattern(sentiDict):
    folder = "pattern"
    title = "Pattern"
    corpus = "Pattern"
    center = 0.0
    stems = False
    score_range = "integer"

    def loadDict(self,bananas):
        import xml.etree.ElementTree as etree
        tree = etree.parse('data/{0}/en-sentiment.xml'.format(self.folder))
        root = tree.getroot()
        # look at some stuff:
        # print(root)
        # for child in root:
        #     print(child)
        #     print(child.tag)
        #     print(child.form)
        #     print(child.attrib['form'])
            
        # print(len(my_dict))
        # print(root[0].attrib)
        for i,child in enumerate(root):
            my_dict[child.attrib['form']] = (i,float(child.attrib['polarity']))

        # look at the words
        # print(len(my_dict))
        # my_dict['13th']
        # pos_words = [word for word in my_dict if my_dict[word][1] > 0]
        # print(len(pos_words))
        # neg_words = [word for word in my_dict if my_dict[word][1] < 0]
        # print(len(neg_words))
        return my_dict

class sentiWordNet(sentiDict):
    folder = "sentiWordNet"
    title = "SentiWordNet"
    corpus = "SentiWordNet"
    center = 0.0
    stems = False
    score_range = "full"

    def loadDict(self,bananas):
        f = open("data/{0}/SentiWordNet_3.0.0_20130122.txt".format(folder),"r")
        f.readline()
        my_dict = dict()
        for line in f:
            splitline = line.rstrip().split("\t")
            words = map(lambda x: x[:-2],splitline[4].split(" "))
            # print(words)
            for word in words:
                if word not in my_dict:
                    my_dict[word] = splitline[2:4]
                else:
                    my_dict[word] = my_dict[word]+splitline[2:4]

        i = 0
        for word in my_dict:
            pos_scores = map(float,my_dict[word][0::2])
            neg_scores = map(float,my_dict[word][1::2])
            my_dict[word] = (i,sum(pos_scores)/len(pos_scores),sum(neg_scores)/len(neg_scores))
            i+=1
            
        # my_dict['deflagrate']
        # len(my_dict)
        # pos_words = [word for word in my_dict if my_dict[word][0] > my_dict[word][1]]
        # len(pos_words)
        # neg_words = [word for word in my_dict if my_dict[word][0] < my_dict[word][1]]
        # len(neg_words)
        # neutral_words = [word for word in my_dict if my_dict[word][0] == my_dict[word][1]]
        # len(neutral_words)

        return my_dict

class AFINN(sentiDict):
    folder = "AFINN"
    title = "AFINN"
    corpus = "AFINN"
    center = 0.0
    stems = False
    score_range = "full"

    def loadDict(self,bananas):
        afinn = dict([ (line.rstrip().split(t)[0],int(line.rstrip().split(t)[1])) for line in open("data/AFINN/AFINN-111.txt") ])
        # pos_words = [word for word in afinn if afinn[word] > 0]
        # neg_words = [word for word in afinn if afinn[word] < 0]
        # neu_words = [word for word in afinn if afinn[word] == 0]

        return afinn
    
class GI(sentiDict):
    folder = "GI"
    title = "General Inquirer"
    corpus = "General Inquirer"
    center = 0.0
    stems = False
    score_range = "integer"

    def loadDict(self,bananas):
        # coding: utf-8
        f = open("inqtabs.txt","r")
        header = f.readline().rstrip()
        for line in f:
            splitline = line.rstrip().split("\t")
            word = splitline[0]
            pos = splitline[2]
            neg = splitline[3]
            if len(pos) > 0:
                my_dict[word] = 1
            if len(neg) > 0:
                my_dict[word] = -1
                
        my_dict = dict()
        i = 0
        for line in f:
            splitline = line.rstrip().split("\t")
            word = splitline[0]
            pos = splitline[2]
            neg = splitline[3]
            if len(pos) > 0:
                my_dict[word] = (i,1)
                i+=1
            elif len(neg) > 0:
                # print("oops, {0} is both pos and negative".format(word))
                my_dict[word] = (i,-1)
                i+=1
            
        # len(my_dict)
        # pos_words = [word for word in my_dict if my_dict[word] > 0]
        # neg_words = [word for word in my_dict if my_dict[word] < 0]
        # len(pos_words)
        # len(neg_words)

        return my_dict

class WDAL(sentiDict):
    folder = "WDAL"
    title = "Whissel's Dictionary of Affective Language"
    corpus = "Whissel's Dictionary of Affective Language"
    center = 1.5
    stems = False
    score_range = "full"

    def loadDict(self,bananas):
        f = open("words.txt","r")
        my_dict = dict()
        f.readline()
        i = 0
        for line in f:
            a = line.rstrip().split(" ")
            word = a[0]
            pleasantness,activation,imagery = a[-3:]
            my_dict[word] = (i,float(pleasantness))
            i+=1
            
        # len(my_dict)
        # pos_words = [word for word in my_dict if my_dict[word] > 1.5]
        # print(len(pos_words))
        # neg_words = [word for word in my_dict if my_dict[word] < 1.5]
        # print(len(neg_words))
        # neg_words = [word for word in my_dict if my_dict[word] <= 1.5]
        # print(len(neg_words))
        # neg_words = [word for word in my_dict if my_dict[word] < 1.5]
        # neu_words = [word for word in my_dict if my_dict[word] == 1.5]
        # print(len(neu_words))
        # len(my_dict)

        return my_dict



class NRC(sentiDict):
    folder = "NRC"
    title = "NRC"
    corpus = "NRC"
    center = 0.0
    stems = False
    score_range = "full"

    def loadDict(self,bananas):
        i = 0
        # coding: utf-8
        f = open("Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
        unigrams = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in unigrams:
                unigrams[word] = (i,score)
                i+=1
            # else:
            #     print("complaining")
        f.close()
        
        # print("read in {0} unigrams".format(len(unigrams)))
        
        f = open("Sentiment140-Lexicon-v0.1/bigrams-pmilexicon.txt","r")
        bigrams = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in bigrams:
                bigrams[word] = (i,score)
                i+=1
            # else:
            #     print("complaining")
        f.close()

        # print("read in {0} bigrams".format(len(bigrams)))        
        
        f = open("Sentiment140-Lexicon-v0.1/pairs-pmilexicon.txt","r")
        pairs = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in pairs:
                pairs[word] = score
                i+=1
            # else:
            #     print("complaining")            
        f.close()

        # print("read in {0} pairs".format(len(pairs)))

        # print("length of all of them: {0}".format(len(pairs)+len(bigrams)+len(unigrams)))
        
        all = unigrams.copy()
        all.update(bigrams)
        all.update(pairs)
        
        # pos_words = [word for word in all if all[word] > 0]
        # neg_words = [word for word in all if all[word] < 0]
        # neu_words = [word for word in all if all[word] == 0]
        # len(pos_words)
        # len(neg_words)
        # all['happy']
        # pos_words = [word for word in all if float(all[word]) > 0]
        # len(neg_words)
        # len(pos_words)
        # neg_words = [word for word in all if float(all[word]) < 0]
        # neu_words = [word for word in all if float(all[word]) == 0]
        # len(neg_words)
        # len(neu_words)

        return all

# class Sentence(object):
#     words = []
    
#     def __init__():
#         pass
    
