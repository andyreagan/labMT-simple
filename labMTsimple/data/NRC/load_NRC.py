# coding: utf-8
f = open("Sentiment140-Lexicon-v0.1/unigrams-pmilexicon.txt","r")
unigrams = dict()
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    unigrams[word] = score
f.close()

# len(unigrams)
f = open("Sentiment140-Lexicon-v0.1/bigrams-pmilexicon.txt","r")
bigrams = dict()
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    bigrams[word] = score
f.close()

# len(bigrams)
f = open("Sentiment140-Lexicon-v0.1/pairs-pmilexicon.txt","r")
pairs = dict()
for line in f:
    word,score,poscount,negcount = line.rstrip().split("\t")
    pairs[word] = score
f.close()
    
# len(pairs)
# len(pairs)+len(bigrams)+len(unigrams)
# all = unigrams.copy()
# len(all)
# all.update(bigrams)
# all.update(pairs)
# len(all)
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
