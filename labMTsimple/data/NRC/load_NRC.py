# coding: utf-8
f = open("Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
f.readline()
unigrams = dict()
f = open("Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    my_dict[word] = score
    
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    unigrams[word] = score
    
f = open("Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
unigrams = dict()
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    unigrams[word] = score
    
len(unigrams)
f = open("Sentiment140-Lexicon-v0.1/bigrams-pmilexicon.txt","r")
bigrams = dict()
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    bigrams[word] = score
    
len(bigrams)
pairs = dict()
f = open("Sentiment140-Lexicon-v0.1/pairs-pmilexicon.txt,"r")
f = open("Sentiment140-Lexicon-v0.1/pairs-pmilexicon.txt","r")
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    pairs[word] = score
    
len(pairs)
len(pairs)+len(bigrams)+len(unigrams)
all = unigrams.copy()
len(all)
all.update(bigrams)
all.update(pairs)
len(all)
pos_words = [word for word in all if all[word] > 0]
neg_words = [word for word in all if all[word] < 0]
neu_words = [word for word in all if all[word] == 0]
len(pos_words)
len(neg_words)
all['happy']
pos_words = [word for word in all if float(all[word]) > 0]
len(neg_words)
len(pos_words)
neg_words = [word for word in all if float(all[word]) < 0]
neu_words = [word for word in all if float(all[word]) == 0]
len(neg_words)
len(neu_words)
get_ipython().magic(u'save load_NRC.py 1-39')
