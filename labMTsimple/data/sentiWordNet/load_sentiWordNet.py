# coding: utf-8
f = open("SentiWordNet_3.0.0_20130122.txt","r")
for line in f:
    splitline = line.rstrip().split("\t")
    words = map(lambda x: x[:-2],splitline[4].split(" "))
    print(words)
    
my_dict = dict()
for line in f:
    splitline = line.rstrip().split("\t")
    words = map(lambda x: x[:-2],splitline[4].split(" "))
    print(words)
    for word in words:
        if word not in my_dict:
            my_dict[word] = splitline[2:4]
        else:
            print("duplicate")
            
len(my_dict)
f = open("SentiWordNet_3.0.0_20130122.txt","r")
for line in f:
    splitline = line.rstrip().split("\t")
    words = map(lambda x: x[:-2],splitline[4].split(" "))
    print(words)
    for word in words:
        if word not in my_dict:
            my_dict[word] = splitline[2:4]
        else:
            print("duplicate")
            
len(my_dict)
my_dict = dict()
f = open("SentiWordNet_3.0.0_20130122.txt","r")
for line in f:
    splitline = line.rstrip().split("\t")
    words = map(lambda x: x[:-2],splitline[4].split(" "))
    print(words)
    for word in words:
        if word not in my_dict:
            my_dict[word] = splitline[2:4]
        else:
            my_dict[word] = my_dict[word]+splitline[2:4]
            
my_dict['deflagrate']
a = range(10)
a[0::2]
a[1::2]
for word in my_dict:
    pos_scores = my_dict[word][0::2]
    neg_scores = my_dict[word][1::2]
    my_dict[word] = (sum(pos_scores)/len(pos_scores),sum(neg_scores)/len(neg_scores))
    
for word in my_dict:
    pos_scores = map(float,my_dict[word][0::2])
    neg_scores = map(float,my_dict[word][1::2])
    my_dict[word] = (sum(pos_scores)/len(pos_scores),sum(neg_scores)/len(neg_scores))
    
f = open("SentiWordNet_3.0.0_20130122.txt","r")
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
            
for word in my_dict:
    pos_scores = map(float,my_dict[word][0::2])
    neg_scores = map(float,my_dict[word][1::2])
    my_dict[word] = (sum(pos_scores)/len(pos_scores),sum(neg_scores)/len(neg_scores))
    
my_dict['deflagrate']
len(my_dict)
pos_words = [word for word in my_dict if my_dict[word][0] > my_dict[word][1]]
len(pos_words)
neg_words = [word for word in my_dict if my_dict[word][0] < my_dict[word][1]]
len(neg_words)
neutral_words = [word for word in my_dict if my_dict[word][0] == my_dict[word][1]]
len(neutral_words)
