#!/usr/bin/python
#
# storyLab.py
#
# a python module for using the labMT1.0 dataset
# no dependencies, unless using the plot function
#  (then we use matplotlib)
#
# USAGE
#
# In python:
#   tmpstr = 'a happy sentence'
#   from storyLab import emotionFileReader
#   lens = emotionFileReader(0.0)
#   from storyLab import emotion
#   happs = emotion(tmpstr,lens)
# 
# My test:
# >>> test = emotionFileReader(max=3.0)
# >>> len(test)
# 410
# >>> emotion('hate hate hate the',test)
# 2.34
# >>> test2 = emotionFileReader(min=7.0)
# >>> emotion('hate hate hate the',test2)
# 0
# >>> emotion('hate hate hate the happy',test2)
# 8.22
# >>> test3 = emotionFileReader()
# >>> emotion('hate hate hate the happy',test3)
# 4.044
# >>> allEmotions('hate hate hate the happy',test3)
# [4.044]
# >>> allEmotions('hate hate hate the happy',test,test2,test3)
# [2.34, 8.22, 4.044]
#
# In a shell:
#   alias happiness="$(pwd)/storyLab.py"
#   cat storyLab.py | happiness
#   storyLab.py happiness
#
# written by Andy Reagan
# 2014-03-01

def emotionFileReader(stopval=1.0,fileName='labMT1.txt',min=1.0,max=9.0,returnVector=False):
  ## stopval is our lens, \Delta h
  ## read the labMT dataset into a dict with this lens
  ## must be tab-deliminated
  ## if labMT1 file, emotion value as third tab
  ## else, it's the second tab
  labMT1flag = False

  if fileName == 'labMT1.txt':
    scoreIndex = 1 # second value
    labMT1flag = True
  if 'labMT2' in fileName:
    scoreIndex = 1
  try:
    f = open(fileName,'r')
  except IOError:
    import os
    relpath = os.path.abspath(__file__).split('/')[1:-1]
    relpath.append('data')
    relpath.append('labMT1.txt')
    fileName = ''
    for pathp in relpath:
      fileName += '/' + pathp
    f = open(fileName,'r')
    
  tmpDict = dict([(str(line.split('\t')[0].rstrip('"').lstrip('"')),
                  [x.rstrip() for x in line.split('\t')[1:]]) for line in f])

  f.close()
  
  ## remove words
  stopWords = []

  for word in tmpDict:
    ## start the index at 0
    if labMT1flag:
      tmpDict[word][0] = int(tmpDict[word][0])-1
    if abs(float(tmpDict[word][scoreIndex])-5.0) < stopval:
      stopWords.append(word)
    else:
      if float(tmpDict[word][scoreIndex]) < min:
        stopWords.append(word)
      else:
        if float(tmpDict[word][scoreIndex]) > max:
          stopWords.append(word)
  
  for word in stopWords:
    del tmpDict[word]

  ## build vector of all scores
  f = open(fileName,'r')
  tmpList = [float(line.split('\t')[2]) for line in f]
  f.close()
  ## build vector of all words
  f = open(fileName,'r')
  wordList = [line.split('\t')[0] for line in f]
  f.close()

  if returnVector:
    return tmpDict,tmpList,wordList
  else:
    return tmpDict

def emotion(tmpStr,someDict,scoreIndex=1,shift=False,happsList=[]):
  scoreList = []
  # make a frequency vector
  if shift:
    freqList = [0 for i in xrange(len(happsList))]

  # doing this without the NLTK
  words = [x.lower().lstrip("?';:.$%&()\\!*[]{}|\"<>,^-_=+").rstrip("@#?';:.$%&()\\!*[]{}|\"<>,^-_=+") for x in tmpStr.split()]
  # only use the if once
  if shift:
    for word in words:
      if word in someDict:
        scoreList.append(float(someDict[word][scoreIndex]))
        freqList[someDict[word][0]] += 1
  else:
    for word in words:
      if word in someDict:
        scoreList.append(float(someDict[word][scoreIndex]))

  ## with numpy (and mean in the namespace)
  ## happs = mean(scoreList)
  
  ## without numpy
  if len(scoreList) > 0:
    happs = sum(scoreList)/float(len(scoreList))
  else:
    happs = 0

  if shift:
    return happs,freqList
  else:
    return happs

def allEmotions(tmpStr,*allDicts):
  emotionList = []
  for tmpDict in allDicts:
    emotionList.append(emotion(tmpStr,tmpDict))
  return emotionList

def plothapps(happsTimeSeries,picname):
  ## uses matplotlib
  import matplotlib.pyplot as plt

  ## create a figure, fig is now a matplotlib.figure.Figure instance
  fig = plt.figure()

  ## plot the time series
  ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) ##  [left, bottom, width, height]
  ax1.plot(range(len(happs)),happsTimeSeries)
  ax1.set_xlabel('Time')
  ax1.set_ylabel('Happs')
  ax1.set_title('Happiness over time')

  plt.savefig(picname)
  plt.close(fig)

def shift(emoList,refFreq,compFreq):
  ## normalize frequencies
  Nref = float(sum(refFreq))
  Ncomp = float(sum(compFreq))
  for i in xrange(len(refFreq)):
    refFreq[i] = float(refFreq[i])/Nref
    compFreq[i] = float(compFreq[i])/Ncomp
  ## compute the reference happiness
  refHapps = sum([refFreq[i]*emoList[i] for i in xrange(len(emoList))])
  ## determine shift magnitude, type
  shiftMag = [0 for i in xrange(len(emoList))]
  shiftType = [0 for i in xrange(len(emoList))]
  for i in xrange(len(emoList)):
    freqDiff = compFreq[i]-refFreq[i]
    shiftMag[i] = (emoList[i]-refHapps)*freqDiff
    if freqDiff > 0:
      shiftType[i] += 2
    if emoList[i] > refHapps:
      shiftType[i] += 1

  return shiftMag,shiftType

if __name__ == '__main__':
  ## run from standard in
  import fileinput
  labMT = emotionFileReader(0.0)
  happsList = [emotion(line,labMT) for line in fileinput.input()]
  
  for value in happsList:
    print value
    
  






