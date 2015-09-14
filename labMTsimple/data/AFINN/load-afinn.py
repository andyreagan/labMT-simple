afinn = dict(map(lambda (k,v): (k,int(v)), 
                     [ line.split(t) for line in open("AFINN/AFINN-111.txt") ]))
pos_words = [word for word in afinn if afinn[word] > 0]
neg_words = [word for word in afinn if afinn[word] < 0]
neu_words = [word for word in afinn if afinn[word] == 0]
