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
        if self.title in ['labMT','ANEW']:
            oldcorpus = self.title
            # go get the stem sets to extend
            self.title = 'LIWC'
            self.data = self.loadDict()
            # make lists from it
            self.makeListsFromDict()
            # create the trie
            LIWCtrie = self.makeMarisaTrie()
            self.title = 'MPQA'
            self.data = self.loadDict()
            # make lists from it
            self.makeListsFromDict()
            # create the trie
            MPQAtrie = self.makeMarisaTrie()
            self.title = oldcorpus

        if self.title not in ['labMT','ANEW']:
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
            if key[-1] == "*" and len(key) > 1:
                if not key[-2] == "*":
                    # tmpstemwords.append(key.replace("*",""))
                    tmpstemwords.append(key[:-1])
                    tmpstemscores.append(score[1])
                else:
                    tmpfixedwords.append(key)
                    tmpfixedscores.append(score[1])
            else:
                tmpfixedwords.append(key)
                tmpfixedscores.append(score[1])
        if self.title in ['labMT','ANEW']:
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

    def scoreTrieMarisa(self,wordDict,idx=1):
        """Score a wordDict using the marisa_trie backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.my_marisa[0]:
                totalcount += count
                totalscore += count*self.my_marisa[0].get(word)[0][idx]
            elif (len(self.my_marisa[1].prefixes(word)) > 0):
                totalcount += count
                totalscore += count*self.my_marisa[1].get(self.my_marisa[1].prefixes(word)[0])[0][idx]
        if totalcount > 0:
            return totalscore/totalcount
        else:
            return self.center

    def scoreTrieDict(self,wordDict,idx=1):
        """Score a wordDict using the dict backend.

        INPUTS:\n
        -wordDict is a favorite hash table of word and count."""
        totalcount = 0
        totalscore = 0.0
        for word,count in wordDict.items():
            if word in self.data:
                totalcount += count
                totalscore += count*self.data[word][idx]
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

    def stopData(self):
        stopWords = []
        for word in self.data:
            if abs(self.data[word][1]-self.center) < self.stopVal:
                stopWords.append(word)
        for word in stopWords:
            del self.data[word]

    def __init__(self,datastructure='dict',bootstrap=False,stopVal=0.0,bananas=False,loadFromFile=False,saveFile=False,lang='english'):
        """Instantiate the class."""
        self.stopVal = stopVal
        self.datastructure = datastructure
        if saveFile:
            if not isdir('{0}'.format(self.folder)):
                mkdir('{0}'.format(self.folder))
        if not self.stems and datastructure=="dict":
            self.data = self.loadDict(bananas,lang)
            self.stopData()
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
                self.data = self.loadDict(bananas,lang)
                self.stopData()
                # make lists from it
                self.makeListsFromDict()
                # create the trie
                self.my_marisa = self.makeMarisaTrie()

            self.matcher = self.matcherTrieMarisa
            self.matcherBool = self.matcherDictBool
            self.score = self.scoreTrieMarisa
            self.wordVecify = self.wordVecifyTrieMarisa
            self.datastructure = "marisatrie"
        # print("loading {0} with stopVal={1}, for {2} words".format(self.title,stopVal,len(self.data)))

class LabMT(sentiDict):
    """LabMT class.
    
    Now takes the full name of the language."""

    # the folder, of course
    # same as the class, force upper case on first letter
    folder = 'LabMT'
    # short title
    title = 'labMT'
    # long title
    title_long = 'language assessment by Mechanical Turk'
    construction_note = "Survey: MT, 50 ratings"
    license = "CC"
    citation = """@article{dodds2015a,
	Author = {Dodds, P. S. and Clark, E. M. and Desu, S. and Frank, M. R. and Reagan, A. J. and Williams, J. R. and Mitchell, L. and Harris, K. D. and Kloumann, I. M. and Bagrow, J. P. and Megerdoomian, K. and McMahon, M. T. and Tivnan, B. F. and Danforth, C. M.},
	Journal = {PNAS},
	Number = {8},
	Pages = {2389--2394},
	Title = {Human language reveals a universal positivity bias},
	Volume = {112},
	Year = {2015}}"""
    center = 5.0
    stems = False
    score_range_type = 'full'

    def loadDict(self,bananas,lang):
        # don't cheat
        LabMT = dict()
        f = self.openWithPath("data/LabMT/labMT2{}.txt".format(lang),"r")
        f.readline()
        # word    rank    happs   stddev  rank    rank    rank    rank
        i = 0
        for line in f:
            l = line.rstrip().split("\t")
            # this is for the english set
            # word,overallrank,happs,stddev,rank1,rank2,rank3,rank4 = l
            # for other langs, not the same
            # we'll at least assume that the first four ar the same
            word,overallrank,happs,stddev = l[:4]
            LabMT[word] = (i,float(happs),float(stddev))
            i+=1
        f.close()
        return LabMT

    # n_fixed = 
    # n_stems =
    # n_words = n_fixed+n_stems
    # score_range = 
    # n_pos = 
    # n_neg = 

class ANEW(sentiDict):
    """ANEW class."""

    # these are the global lists
    folder = 'ANEW'
    title = 'ANEW'
    title_long = 'Affective Norms of English Words'
    construction_note = "Survey: FSU Psych 101"
    license = "Free for research"
    citation = """@techreport{bradley1999a,
	Address = {Gainesville, FL},
	Author = {Bradley, M. M. and Lang, P. J.},
	Institution = {University of Florida},
	Key = {psychology},
	Title = {Affective norms for English words ({ANEW}): Stimuli, instruction manual and affective ratings},
	Type = {Technical report C-1},
	Year = {1999}}"""
    center = 5.0
    stems = False
    score_range_type = 'full'

    def loadDict(self,bananas,lang):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        
        ANEW_data = dict()
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
            ANEW_data[description] = (i,float(valence_mean),float(valence_sd),float(arousal_mean),float(arousal_sd),float(dominance_mean),float(dominance_sd))
            i+=1
        f.close()
        return ANEW_data

class LIWC(sentiDict):
    """LIWC class."""

    # these are the global lists
    folder = 'LIWC'
    title = 'LIWC'
    title_long = 'Linguistic Inquiry and Word Count'
    construction_note = "Manual"
    license = "Paid, commercial"
    citation = """@article{pennebaker2001a,
	Author = {Pennebaker, James W and Francis, Martha E and Booth, Roger J},
	Journal = {Mahway: Lawrence Erlbaum Associates},
	Pages = {2001},
	Title = {Linguistic inquiry and word count: {LIWC} 2001},
	Volume = {71},
	Year = {2001}}"""
    center = 0.0
    stems = True
    score_range_type = 'integer'
    word_types = dict()
    
    def loadDict(self,bananas,lang):
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
        
        LIWC_data = dict()
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
            if word not in LIWC_data:
                LIWC_data[word] = [0 for j in range(len(word_type_dict)+2)]
                LIWC_data[word][0] = i
                # affect word
                if 125 in tags:
                    # posititive
                    if 126 in tags:
                        score = 1
                        LIWC_data[word][1] = score
                    # negative
                    elif 127 in tags:
                        score = -1
                        LIWC_data[word][1] = score
                for tag in tags:
                    LIWC_data[word][word_type_dict[tag][0]] = 1
                    
                # SORT THIS MESS OUT LATER
                # ...by adding all word types, the first score of 0
                # is now meaningless (if it had any meaning before...)
                #
                # # get the words that are "function" words (1)
                # # specifically not getting them with emotion
                # # if the bananas is false
                # elif self.stopVal == 0.0 and 1 in l and not bananas:
                #     score = 0
                #     if word in LIWC_data:
                #         print(word)
                #     LIWC_data[word][1] = score
                # # but if bananas, put them neutral regardless of affect!
                # elif self.stopVal == 0.0 and 1 in l and bananas:
                #     score = 0
                #     if word in LIWC_data:
                #         print(word)
                #     LIWC_data[word] = (i,score)
                
                i+=1
            else:
                # print("already in LIWC_data: {0}".format(word))
                pass
        f.close()
        return LIWC_data

class MPQA(sentiDict):
    """MPQA class."""
    # these are the global lists
    folder = 'MPQA'
    title = 'MPQA'
    title_long = "The Multi-Perspective Question Answering (MPQA) Subjectivity Dictionary"
    construction_note = "Manual + ML"
    license = "GNU GPL"
    citation = """@article{wilson2005a,
	Author = {Theresa Wilson and Janyce Wiebe and Paul Hoffmann},
	Journal = {Proceedings of Human Language Technologies Conference/Conference on Empirical Methods in Natural Language Processing (HLT/EMNLP 2005)},
	Title = {Recognizing Contextual Polarity in Phrase-Level Sentiment Analysis},
	Year = {2005}}"""
    center = 0.0
    stems = True
    score_range_type = 'integer'
    
    def loadDict(self,bananas,lang):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        MPQA = dict()
        scores = [-1,0,1]
        emotions = ["negative","neutral","positive"]
        f = self.openWithPath("data/MPQA/subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.tff","r")
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
        # print("MPQA duplicates: {0}".format(num_duplicates))
        return MPQA

class Liu(sentiDict):
    folder = 'OL'
    title = 'OL'
    title_long = "Opinion Lexicon (Developed by Bing Liu)"
    construction_note = "Dictionary propagation"
    license = "Free"
    citation = """@article{liu2010a,
	Author = {Liu, Bing},
	Journal = {Handbook of natural language processing},
	Pages = {627--666},
	Publisher = {Chapman \& Hall Goshen, CT},
	Title = {Sentiment analysis and subjectivity},
	Volume = {2},
	Year = {2010}}"""
    center = 0.0
    stems = False
    score_range_type = 'integer'
    
    def loadDict(self,bananas,lang):
        """Load the corpus into a dictionary, straight from the origin corpus file."""
        liu = dict()
        f = self.openWithPath("data/OL/negative-words.txt","r")
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
        f = self.openWithPath("data/OL/positive-words.txt","r")
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
    folder = 'WK'
    title = 'WK'
    title_long = "Warriner and Kuperman rated words from SUBTLEX by Mechanical Turk"
    construction_note = "Survey: MT, at least 14 ratings"
    license = "CC"
    citation = """@article{warriner2014a,
	Author = {Warriner, Amy Beth and Kuperman, Victor},
	Journal = {Cognition and Emotion},
	Pages = {1--21},
	Publisher = {Taylor \& Francis},
	Title = {Affective biases in {E}nglish are bi-dimensional},
	Year = {2014}}"""
    center = 5.0
    stems = False
    score_range_type = 'full'
    
    def loadDict(self,bananas,lang):
        Warriner = dict()
        f = self.openWithPath("data/WK/BRM-emot-submit.csv","r")
        f.readline()
        # ,Word,V.Mean.Sum,V.SD.Sum,V.Rat.Sum,A.Mean.Sum,A.SD.Sum,A.Rat.Sum,D.Mean.Sum,D.SD.Sum,D.Rat.Sum,V.Mean.M,V.SD.M,V.Rat.M,V.Mean.F,V.SD.F,V.Rat.F,A.Mean.M,A.SD.M,A.Rat.M,A.Mean.F,A.SD.F,A.Rat.F,D.Mean.M,D.SD.M,D.Rat.M,D.Mean.F,D.SD.F,D.Rat.F,V.Mean.Y,V.SD.Y,V.Rat.Y,V.Mean.O,V.SD.O,V.Rat.O,A.Mean.Y,A.SD.Y,A.Rat.Y,A.Mean.O,A.SD.O,A.Rat.O,D.Mean.Y,D.SD.Y,D.Rat.Y,D.Mean.O,D.SD.O,D.Rat.O,V.Mean.L,V.SD.L,V.Rat.L,V.Mean.H,V.SD.H,V.Rat.H,A.Mean.L,A.SD.L,A.Rat.L,A.Mean.H,A.SD.H,A.Rat.H,D.Mean.L,D.SD.L,D.Rat.L,D.Mean.H,D.SD.H,D.Rat.H
        # i,word,v_mean_sum,v_sd_sum,v_rat_sum,a_mean_sum,a_sd_sum,a_rat_sum,d_mean_sum,d_sd_sum,d_rat_sum,v_mean_m,v_sd_m,v_rat_m,v_mean_f,v_sd_f,v_rat_f,a_mean_m,a_sd_m,a_rat_m,a_mean_f,a_sd_f,a_rat_f,d_mean_m,d_sd_m,d_rat_m,d_mean_f,d_sd_f,d_rat_f,v_mean_y,v_sd_y,v_rat_y,v_mean_o,v_sd_o,v_rat_o,a_mean_y,a_sd_y,a_rat_y,a_mean_o,a_sd_o,a_rat_o,d_mean_y,d_sd_y,d_rat_y,d_mean_o,d_sd_o,d_rat_o,v_mean_l,v_sd_l,v_rat_l,v_mean_h,v_sd_h,v_rat_h,a_mean_l,a_sd_l,a_rat_l,a_mean_h,a_sd_h,a_rat_h,d_mean_l,d_sd_l,d_rat_l,d_mean_h,d_sd_h,d_rat_h
        for line in f:
            l = line.rstrip().split(',')
            i,word,v_mean_sum,v_sd_sum,v_rat_sum,a_mean_sum,a_sd_sum,a_rat_sum,d_mean_sum,d_sd_sum,d_rat_sum,v_mean_m,v_sd_m,v_rat_m,v_mean_f,v_sd_f,v_rat_f,a_mean_m,a_sd_m,a_rat_m,a_mean_f,a_sd_f,a_rat_f,d_mean_m,d_sd_m,d_rat_m,d_mean_f,d_sd_f,d_rat_f,v_mean_y,v_sd_y,v_rat_y,v_mean_o,v_sd_o,v_rat_o,a_mean_y,a_sd_y,a_rat_y,a_mean_o,a_sd_o,a_rat_o,d_mean_y,d_sd_y,d_rat_y,d_mean_o,d_sd_o,d_rat_o,v_mean_l,v_sd_l,v_rat_l,v_mean_h,v_sd_h,v_rat_h,a_mean_l,a_sd_l,a_rat_l,a_mean_h,a_sd_h,a_rat_h,d_mean_l,d_sd_l,d_rat_l,d_mean_h,d_sd_h,d_rat_h = l
            Warriner[word] = (int(i),float(v_mean_sum),float(v_sd_sum))
        f.close()
        return Warriner

class PANASX(sentiDict):
    folder = 'PANAS-X'
    title = 'PANAS-X'
    title_long = "The Positive and Negative Affect Schedule —-- Expanded"
    construction_note = "Manual"
    license = "Copyrighted paper"
    citation = """@jurthesis{watson1999panas,
	Author = {Watson, David and Clark, Lee Anna},
	School = {University of Iowa},
	Title = {The {PANAS-X}: Manual for the positive and negative affect schedule-expanded form: Manual for the positive and negative affect schedule-expanded form},
	Year = {1999}}"""
    center = 0.0
    stems = False
    score_range_type = 'integer'
    
    def loadDict(self,bananas,lang):
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

class Pattern(sentiDict):
    folder = "Pattern"
    title = "Pattern"
    title_long = "Pattern 2.6 python library"
    note = "A web mining module for the Python programming language"
    construction_note = "Unspecified"
    license = "BSD"
    citation = """@article{de2012pattern,
	Author = {De Smedt, Tom and Daelemans, Walter},
	Journal = {The Journal of Machine Learning Research},
	Number = {1},
	Pages = {2063--2067},
	Publisher = {JMLR. org},
	Title = {Pattern for {P}ython},
	Volume = {13},
	Year = {2012}}"""
    center = 0.0
    stems = False
    score_range_type = "full"

    def loadDict(self,bananas,lang):
        import xml.etree.ElementTree as etree
        relpath = abspath(__file__).split(u'/')[:-1]
        relpath.append('data/{0}/en-sentiment.xml'.format(self.folder))
        filename = '/'.join(relpath)
        tree = etree.parse(filename)
        root = tree.getroot()
        # look at some stuff:
        # print(root)
        # for child in root:
        #     print(child)
        #     print(child.tag)
        #     print(child.form)
        #     print(child.attrib['form'])

        my_dict = dict()
            
        # print(len(my_dict))
        # print(root[0].attrib)
        for i,child in enumerate(root):
            if child.attrib['form'] in my_dict:
                my_dict[child.attrib['form']][1].append(float(child.attrib['polarity']))
            else:
                my_dict[child.attrib['form']] = [i,[float(child.attrib['polarity'])]]

        # since we are not detecting sense, take an average
        for word in my_dict:
            my_dict[word] = (my_dict[word][0],sum(my_dict[word][1])/len(my_dict[word][1]))

        # look at the words
        # print(len(my_dict))
        # my_dict['13th']
        # pos_words = [word for word in my_dict if my_dict[word][1] > 0]
        # print(len(pos_words))
        # neg_words = [word for word in my_dict if my_dict[word][1] < 0]
        # print(len(neg_words))
        return my_dict

class SentiWordNet(sentiDict):
    folder = "WentiWordNet"
    title = "SentiWordNet"
    title_long = "WordNet synsets each assigned three sentiment scores: positivity, negativity, and objectivity"
    note = "WordNet synsets each assigned three sentiment scores: positivity, negativity, and objectivity"
    construction_note = "Synset synonyms"
    license = "CC BY-SA 3.0"
    citation = """@inproceedings{baccianella2010sentiwordnet,
    title={SentiWordNet 3.0: An Enhanced Lexical Resource for Sentiment Analysis and Opinion Mining.},
	Author = {Baccianella, Stefano and Esuli, Andrea and Sebastiani, Fabrizio},
	Booktitle = {LREC},
	Pages = {2200--2204},
	Title = {Senti{W}ord{N}et 3.0: An Enhanced Lexical Resource for Sentiment Analysis and Opinion Mining.},
	Volume = {10},
	Year = {2010}}"""
    center = 0.0
    stems = False
    score_range_type = "full"

    def loadDict(self,bananas,lang):
        f = self.openWithPath("data/{0}/SentiWordNet_3.0.0_20130122.txt".format(self.folder),"r")
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
            pos_scores = list(map(float,my_dict[word][0::2]))
            neg_scores = list(map(float,my_dict[word][1::2]))
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
    note = "Words manually rated -5 to 5 with impact scores by Finn Nielsen"
    title_long = note
    construction_note = "Manual"
    license = "ODbL v1.0"
    citation = """@inproceedings{nielsen2011new,
	Author = {Nielsen, Finn {\AA}rup},
	Booktitle = {CEUR Workshop Proceedings},
	Editor = {Matthew Rowe and Milan Stankovic and Aba-Sah Dadzie and Mariann Hardey},
	Month = {May},
	Pages = {93-98},
	Title = {A new {ANEW}: Evaluation of a word list for sentiment analysis in microblogs},
	Volume = {Proceedings of the ESWC2011 Workshop on 'Making Sense of Microposts': Big things come in small packages 718},
	Year = {2011}}"""
    center = 0.0
    stems = False
    score_range_type = "full"


    def loadDict(self,bananas,lang):
        # afinn = dict(map(lambda x: (x[0],int(x[1])),
        #              [ line.split("\t") for line in self.openWithPath("data/AFINN/AFINN/AFINN-111.txt","r") ]))
        afinn = dict()
        i = 0
        for line in self.openWithPath("data/AFINN/AFINN/AFINN-111.txt","r"):
            x = line.split("\t")
            afinn[x[0]] = (i,int(x[1]))
            i += 1
        # afinn = dict([ (line.rstrip().split("\t")[0],int(line.rstrip().split("\t")[1])) for line in self.openWithPath("data/AFINN/AFINN/AFINN-111.txt","r") ])
        # pos_words = [word for word in afinn if afinn[word] > 0]
        # neg_words = [word for word in afinn if afinn[word] < 0]
        # neu_words = [word for word in afinn if afinn[word] == 0]
        # print(afinn)
        return afinn
    
class GI(sentiDict):
    folder = "GI"
    title = "GI"
    title_long = "General Inquirer"
    note = "Database of words and manually created semantic and cognitive categories, including positive and negative connotations"
    construction_note = "Harvard-IV-4"
    license = "Unspecified"
    citation = """@article{stone1966general,
	Author = {Stone, Philip J and Dunphy, Dexter C and Smith, Marshall S},
	Journal = {MIT Press},
	Publisher = {MIT press},
	Title = {The General Inquirer: A Computer Approach to Content Analysis.},
	Year = {1966}}"""
    center = 0.0
    stems = False
    score_range_type = "integer"

    def loadDict(self,bananas,lang):
        # coding: utf-8
        f = self.openWithPath("data/GI/inqtabs.txt","r")
        header = f.readline().rstrip()
        # for line in f:
        #     splitline = line.rstrip().split("\t")
        #     word = splitline[0]
        #     pos = splitline[2]
        #     neg = splitline[3]
        #     if len(pos) > 0:
        #         my_dict[word] = 1
        #     if len(neg) > 0:
        #         my_dict[word] = -1
                
        my_dict = dict()
        i = 0
        for line in f:
            splitline = line.rstrip().split("\t")
            word = splitline[0].lower()
            if word[-1] in map(str,range(10)):
                if word[-2] == "#":
                    word = word[:-2]
            pos = splitline[2]
            neg = splitline[3]
            if word in my_dict:
                if (my_dict[word][1] == 1) and len(neg) > 0:
                    print("oops, {0} is both pos and negative".format(word))
                if (my_dict[word][1] == 0) and len(pos) > 0:
                    print("oops, {0} is both pos and negative".format(word))
            else:
                if len(pos) > 0 and len(neg) > 0:
                    print("oops, {0} is both pos and negative in a single entry".format(word))
                elif len(pos) > 0 and len(neg) == 0:
                    my_dict[word] = (i,1)
                    i+=1
                elif len(pos) == 0 and len(neg) > 0:
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
    title = "WDAL"
    title_long = "Whissel's Dictionary of Affective Language"
    note = "About 9000 words rated in terms of their Pleasantness, Activation, and Imagery (concreteness)"
    construction_note = "Survey: Columbia students"
    license = "Unspecified"
    citation = """@article{whissell1986dictionary,
	Author = {Whissell, Cynthia and Fournier, Michael and Pelland, Ren{\'e} and Weir, Deborah and Makarec, Katherine},
	Journal = {Perceptual and Motor Skills},
	Number = {3},
	Pages = {875--888},
	Publisher = {Ammons Scientific},
	Title = {A dictionary of affect in language: IV. Reliability, validity, and applications},
	Volume = {62},
	Year = {1986}}"""
    center = 1.5
    stems = False
    score_range_type = "full"

    def loadDict(self,bananas,lang):
        f = self.openWithPath("data/WDAL/words.txt","r")
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
    title_long = "Created from the “sentiment140” corpus of tweets, using emoticons as positive and negative labels"
    note = "Created from the “sentiment140” corpus of tweets, using emoticons as positive and negative labels"
    construction_note = "PMI with emoticons"
    license = "Free for research"
    citation = """@inproceedings{MohammadKZ2013,
	Address = {Atlanta, Georgia, USA},
	Author = {Mohammad, Saif M. and Kiritchenko, Svetlana and Zhu, Xiaodan},
	Booktitle = {Proceedings of the seventh international workshop on Semantic Evaluation Exercises (SemEval-2013)},
	Month = {June},
	Title = {NRC-Canada: Building the State-of-the-Art in Sentiment Analysis of Tweets},
	Year = {2013}}"""
    center = 0.0
    stems = False
    score_range_type = "full"

    def loadDict(self,bananas,lang):
        i = 0
        # coding: utf-8
        f = self.openWithPath("data/NRC/Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
        unigrams = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in unigrams:
                unigrams[word] = (i,float(score))
                i+=1
            else:
                print("complaining")
        f.close()
        
        # print("read in {0} unigrams".format(len(unigrams)))
        
        f = self.openWithPath("data/NRC/Sentiment140-Lexicon-v0.1/bigrams-pmilexicon.txt","r")
        bigrams = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in bigrams:
                bigrams[word] = (i,float(score))
                i+=1
            else:
                print("complaining")
        f.close()

        # print("read in {0} bigrams".format(len(bigrams)))        
        
        f = self.openWithPath("data/NRC/Sentiment140-Lexicon-v0.1/pairs-pmilexicon.txt","r")
        pairs = dict()
        for line in f:
            word,score,poscount,negcount = line.rstrip().split("\t")
            if word not in pairs:
                pairs[word] = (i,float(score))
                i+=1
            else:
                print("complaining")
        f.close()

        # print("read in {0} pairs".format(len(pairs)))

        # print("length of all of them: {0}".format(len(pairs)+len(bigrams)+len(unigrams)))
        
        all_grans = unigrams.copy()
        all_grans.update(bigrams)
        all_grans.update(pairs)
        
        # pos_words = [word for word in all_grans if all_grans[word] > 0]
        # neg_words = [word for word in all_grans if all_grans[word] < 0]
        # neu_words = [word for word in all_grans if all_grans[word] == 0]
        # len(pos_words)
        # len(neg_words)
        # all_grans['happy']
        # pos_words = [word for word in all_grans if float(all_grans[word]) > 0]
        # len(neg_words)
        # len(pos_words)
        # neg_words = [word for word in all_grans if float(all_grans[word]) < 0]
        # neu_words = [word for word in all_grans if float(all_grans[word]) == 0]
        # len(neg_words)
        # len(neu_words)

        # for word in all_grans:
        #     if word == "":
        #         print(word,all_grans[word])
        #     if len(word) == 1:
        #         print(word,all_grans[word])

        return all_grans

class SOCAL(sentiDict):
    # https://www.aclweb.org/anthology/J/J11/J11-2001.pdf
    citation="""@article{taboada2011lexicon,
	Author = {Taboada, Maite and Brooke, Julian and Tofiloski, Milan and Voll, Kimberly and Stede, Manfred},
	Date-Added = {2016-07-13 20:17:18 +0000},
	Date-Modified = {2016-07-13 20:17:18 +0000},
	Journal = {Computational linguistics},
	Number = {2},
	Pages = {267--307},
	Publisher = {MIT Press},
	Title = {Lexicon-based methods for sentiment analysis},
	Volume = {37},
	Year = {2011}}"""

class SenticNet(sentiDict):
    citation="""@article{cambria2016affective,
	Author = {Cambria, Erik},
	Date-Added = {2016-07-13 20:46:11 +0000},
	Date-Modified = {2016-07-13 20:46:11 +0000},
	Journal = {IEEE Intelligent Systems},
	Number = {2},
	Pages = {102--107},
	Publisher = {IEEE},
	Title = {Affective computing and sentiment analysis},
	Volume = {31},
	Year = {2016}}"""

class Emoticons(sentiDict):
    citation="""@inproceedings{gonccalves2013comparing,
  title={Comparing and combining sentiment analysis methods},
  author={Gon{\c{c}}alves, Pollyanna and Ara{\'u}jo, Matheus and Benevenuto, Fabr{\'\i}cio and Cha, Meeyoung},
  booktitle={Proceedings of the first ACM conference on Online social networks},
  pages={27--38},
  year={2013},
  organization={ACM}}"""

class SASA(sentiDict):
    citation="""@inproceedings{wang2012system,
	Author = {Wang, Hao and Can, Dogan and Kazemzadeh, Abe and Bar, Fran{\c{c}}ois and Narayanan, Shrikanth},
	Booktitle = {Proceedings of the ACL 2012 System Demonstrations},
	Date-Added = {2016-07-13 20:32:04 +0000},
	Date-Modified = {2016-07-13 20:32:04 +0000},
	Organization = {Association for Computational Linguistics},
	Pages = {115--120},
	Title = {A system for real-time twitter sentiment analysis of 2012 us presidential election cycle},
	Year = {2012}}"""

class SentiStrength(sentiDict):
    citation="""
@article{thelwall2010sentiment,
	Author = {Thelwall, Mike and Buckley, Kevan and Paltoglou, Georgios and Cai, Di and Kappas, Arvid},
	Date-Added = {2016-07-13 20:51:52 +0000},
	Date-Modified = {2016-07-13 20:51:52 +0000},
	Journal = {Journal of the American Society for Information Science and Technology},
	Number = {12},
	Pages = {2544--2558},
	Publisher = {Wiley Online Library},
	Title = {Sentiment strength detection in short informal text},
	Volume = {61},
	Year = {2010}}"""

class VADER(sentiDict):
    citation="""@inproceedings{hutto2014vader,
  title={Vader: A parsimonious rule-based model for sentiment analysis of social media text},
  author={Hutto, Clayton J and Gilbert, Eric},
  booktitle={Eighth International AAAI Conference on Weblogs and Social Media},
  year={2014}}"""

class WNAffect(sentiDict):
    citation="""@inproceedings{strapparava2004wordnet,
	Author = {Strapparava, Carlo and Valitutti, Alessandro and others},
	Booktitle = {LREC},
	Date-Added = {2016-07-13 21:38:33 +0000},
	Date-Modified = {2016-07-13 21:38:33 +0000},
	Pages = {1083--1086},
	Title = {WordNet Affect: an Affective Extension of WordNet.},
	Volume = {4},
	Year = {2004}}"""

class Umigon(sentiDict):
    citation="""@inproceedings{levallois2013umigon,
	Author = {Levallois, Clement},
	Booktitle = {Second Joint Conference on Lexical and Computational Semantics (* SEM)},
	Date-Added = {2016-07-13 21:41:50 +0000},
	Date-Modified = {2016-07-13 21:41:50 +0000},
	Pages = {414--417},
	Title = {Umigon: sentiment analysis for tweets based on terms lists and heuristics},
	Volume = {2},
	Year = {2013}}"""

class USent(sentiDict):
    citation="""@inproceedings{pappas2013distinguishing,
  title={Distinguishing the popularity between topics: A system for up-to-date opinion retrieval and mining in the web},
  author={Pappas, Nikolaos and Katsimpras, Georgios and Stamatatos, Efstathios},
  booktitle={International Conference on Intelligent Text Processing and Computational Linguistics},
  pages={197--209},
  year={2013},
  organization={Springer}}"""
    
# class Sentence(object):
#     words = []
    
#     def __init__():
#         pass
    
