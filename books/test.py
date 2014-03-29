from labMTsimple.storyLab import *

labMT,labMTvector,labMTwordList = emotionFileReader(stopval = 0.0, returnVector=True)

import codecs ## handle utf8
f = codecs.open("data/moby_dick_text.txt","r","utf8")
raw_text = f.read()
f.close()

words_extra_split = [[y.lower().lstrip("?';:.$%&()\\!*[]{}|\"<>,^-_=+").rstrip("@#?';:.$%&()\\!*[]{}|\"<>,^-_=+") for y in x.split('--')] for x in raw_text.split()]
words = [x for i in xrange(len(words_extra_split)) for x in words_extra_split[i]]

print len(words)
print words[0:10]
for word in words[0:10]:
  print word
## compute valence score and return frequency vector for generating wordshift
textValence,textFvec = emotion(raw_text,labMT,shift=True,happsList=labMTvector)
print 'the valence of {0} is {1:.5}'.format('moby_dick',textValence)

# split the text into chunks of size 10000
# and print those frequency vectors
allFvec = []
from numpy import floor
for i in xrange(int(floor(len(words)/10000))):
  chunk = ''
  if i == int(floor(len(words)/10000))-1:
    # take the rest
    print 'last chunk'
    print 'getting words ' + str(i*10000) + ' through ' + str(len(words)-1)
    for j in xrange(i*10000,len(words)-1):
      chunk += words[j]+' '
  else:
    print 'getting words ' + str(i*10000) + ' through ' + str((i+1)*10000)
    for j in xrange(i*10000,(i+1)*10000):
      chunk += words[j]+' '
  print chunk[0:10]
  textValence,textFvec = emotion(chunk,labMT,shift=True,happsList=labMTvector)
  print 'the valence of {0} part {1} is {2}'.format('moby_dick',i,textValence)
  
  allFvec.append(textFvec)

  f = open("data/moby_dick_freq_{0:02d}.csv".format(i),"w")
  f.write('{0:.0f}'.format(textFvec[0]))
  for i in xrange(1,len(textFvec)):
    f.write("\n")
    f.write('{0:.0f}'.format(textFvec[i]))
  f.close()

f = open("data/moby_dick_freq_all.csv","w")
f.write('{0:.0f}'.format(allFvec[0][0]))
for k in xrange(1,len(allFvec)):
  f.write(',{0:.0f}'.format(allFvec[k][0]))
for i in xrange(1,len(allFvec[0])):
  f.write("\n")
  f.write('{0:.0f}'.format(allFvec[0][i]))
  for k in xrange(1,len(allFvec)):
    f.write(',{0:.0f}'.format(allFvec[k][i]))
f.close()

f = open("data/labMTvec.csv","w")
f.write('{0:.8f}'.format(labMTvector[0]))
for i in xrange(1,len(labMTvector)):
  f.write("\n")
  f.write('{0:.8f}'.format(labMTvector[i]))
f.close()

f = open("data/labMTwords.csv","w")
f.write(labMTwordList[0])
for i in xrange(1,len(labMTwordList)):
  f.write("\n")
  f.write(labMTwordList[i])
f.close()

# shiftHtml(labMTvector,labMTwordList,tuesdayFvec,saturdayFvec,'test.html')


