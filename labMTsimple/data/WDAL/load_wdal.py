# coding: utf-8
f = open("words.txt","r")
f.readline()
my_dict = dict()
for line in f:
    a = line.rstrip().split(" ")
    word = a[0]
    pleasantness,activation,imagery = a[-4:]
    my_dict[word] = float(pleasantness)
    
for line in f:
    a = line.rstrip().split(" ")
    word = a[0]
    pleasantness,activation,imagery = a[-3:]
    my_dict[word] = float(pleasantness)
    
f = open("words.txt","r")
my_dict = dict()
f.readline()
for line in f:
    a = line.rstrip().split(" ")
    word = a[0]
    pleasantness,activation,imagery = a[-3:]
    my_dict[word] = float(pleasantness)
    
len(my_dict)
pos_words = [word for word in my_dict if my_dict[word] > 1.5]
print(len(pos_words))
neg_words = [word for word in my_dict if my_dict[word] < 1.5]
print(len(neg_words))
neg_words = [word for word in my_dict if my_dict[word] <= 1.5]
print(len(neg_words))
neg_words = [word for word in my_dict if my_dict[word] < 1.5]
neu_words = [word for word in my_dict if my_dict[word] == 1.5]
print(len(neu_words))
len(my_dict)
