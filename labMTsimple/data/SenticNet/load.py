f = open("senticnet3.rdf.xml","r")
import re
all_words = list()
all_scores = list()
word = False
for line in f:
    if len(re.findall('<text xmlns="http://sentic.net/api">([-&\w ]+)</text>',line)) > 0:
        # print(re.findall('<text xmlns="http://sentic.net/api">([\w ]+)</text>',line))
        word = True
        all_words.append(re.findall('<text xmlns="http://sentic.net/api">([-&\w ]+)</text>',line)[0])
    if len(re.findall('<polarity xmlns="http://sentic.net/api" rdf:datatype="http://www.w3.org/2001/XMLSchema#float">([-+0-9\.]+)</polarity>',line)) > 0:
        if not word:
            print("missing word after "+all_words[-1])
        word = False
        all_scores.append(re.findall('<polarity xmlns="http://sentic.net/api" rdf:datatype="http://www.w3.org/2001/XMLSchema#float">([-+0-9\.]+)</polarity>',line)[0])

print(len(all_words))
print(len(all_scores))

scraped = dict()
for i,word,score in zip(range(len(all_words)),all_words,all_scores):
    scraped[word] = (i,float(score))

import json
json.dump(scraped,open("senticnet3.json","w"),indent=4)
    
        
