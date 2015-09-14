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
for line in f:
    splitline = line.rstrip().split("\t")
    word = splitline[0]
    pos = splitline[2]
    neg = splitline[3]
    if len(pos) > 0:
        my_dict[word] = 1
    if len(neg) > 0:
        my_dict[word] = -1
        
len(my_dict)
pos_words = [word for word in my_dict if my_dict[word] > 0]
neg_words = [word for word in my_dict if my_dict[word] < 0]
len(pos_words)
len(neg_words)
