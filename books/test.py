import sys, os

try:
  from labMTsimple.storyLab import *
except ImportError:
  import sys, os
  sys.path.append('/Users/andyreagan/work/2014/labMTsimple')
  sys.path.append(os.path.join(os.path.dirname(__file__), "labMTsimple"))
  from labMTsimple.storyLab import *
except:
  print 'you need have to storyLab.py in your search path'
  print 'either 1) install with "pip install labMTsimple"'
  print '2) add the path to storyLab.py to $PYTHONPATH'
  print '   and have labMT1.txt local'
  print '3) run from a directory containing storyLab.py and labMT1.txt'

try:
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval = 0.0, returnVector=True)
except IOError:
  print 'you need to have the labMT1.txt data on python search path'

## take a look at these guys
print 'the word laughter in the hash has the data:'
print labMT['laughter']
print 'the top 5 scores, and those words, are:'
print labMTvector[0:5]
print labMTwordList[0:5]

## test shift a subsample of two twitter days
import codecs ## handle utf8
f = codecs.open("data/18.01.14.txt","r","utf8")
saturday = f.read()
f.close()
f = codecs.open("data/21.01.14.txt","r","utf8")
tuesday = f.read()
f.close()

## compute valence score
print 'computing happiness...'

## compute valence score and return frequency vector for generating wordshift
saturdayValence,saturdayFvec = emotion(saturday,labMT,shift=True,happsList=labMTvector)
tuesdayValence,tuesdayFvec = emotion(tuesday,labMT,shift=True,happsList=labMTvector)
print 'the valence of {0} is {1:.5}'.format('saturday',saturdayValence)
print 'the valence of {0} is {1:.5}'.format('tuesday',tuesdayValence)

f = open("saturdayFvec.csv","w")
f.write('{0:.0f}'.format(saturdayFvec[0]))
for i in xrange(1,len(saturdayFvec)):
  f.write("\n")
  f.write('{0:.0f}'.format(saturdayFvec[i]))
f.close()

f = open("tuesdayFvec.csv","w")
f.write('{0:.0f}'.format(tuesdayFvec[0]))
for i in xrange(1,len(tuesdayFvec)):
  f.write("\n")
  f.write('{0:.0f}'.format(tuesdayFvec[i]))
f.close()

f = open("labMTvec.csv","w")
f.write('{0:.8f}'.format(labMTvector[0]))
for i in xrange(1,len(labMTvector)):
  f.write("\n")
  f.write('{0:.8f}'.format(labMTvector[i]))
f.close()

f = open("labMTwords.csv","w")
f.write(labMTwordList[0])
for i in xrange(1,len(labMTwordList)):
  f.write("\n")
  f.write(labMTwordList[i])
f.close()

shiftHtml(labMTvector,labMTwordList,tuesdayFvec,saturdayFvec,'test.html')
