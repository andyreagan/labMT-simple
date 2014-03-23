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

import os

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

def emotionFileReaderRaw(stopval=1.0,fileName='labMT1raw.txt',min=1.0,max=9.0,returnVector=False):

  try:
    f = open(fileName,'r')
  except IOError:
    relpath = os.path.abspath(__file__).split('/')[1:-1]
    relpath.append('data')
    relpath.append('labMT1raw.txt')
    fileName = ''
    for pathp in relpath:
      fileName += '/' + pathp
    f = open(fileName,'r')

  tmpDict = dict()

  while f:
    word = f.readline()
    tmpDict[word] = []
    for i in xrange(10):
      tmpDict[word].append(map(int,f.readline().split('\t'))[1])
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

def shiftHtml(scoreList,wordList,refFreq,compFreq,outFile):
  ## write out the template
  f = open('tmp.js','w')
  f.write('function initializePlot() { loadCsv(); }\n\n')

  ## dump the data
  f.write('function loadCsv() {\n')
  f.write('    lens = [')
  for score in scoreList:
    f.write(str(score)+',')
  f.write('];\n\n')
  f.write('    words = [')
  for word in wordList:
    f.write('"'+str(word)+'",')
  f.write('];\n\n')
  f.write('    refFraw = [')
  for freq in refFreq:
    f.write('{0:.0f},'.format(freq))
  f.write('];\n\n')
  f.write('    compFraw = [')
  for freq in compFreq:
    f.write('{0:.0f},'.format(freq))
  f.write('];\n\n')
  f.write('    initializePlotPlot(refFraw,compFraw,lens,words);\n };\n')

  ## rest of the main js
  f.write('  function initializePlotPlot(refFraw,compFraw,lens,words) {\n')
  f.write('    // draw the lens\n')
  f.write('    drawLens(d3.select("#lens01"),lens,refFraw,compFraw);\n')
  f.write('\n')
  f.write('    // initially apply the lens, and draw the shift\n')
  f.write('    var refF = Array(refFraw.length);\n')
  f.write('    var compF = Array(compFraw.length);\n')
  f.write('    for (var i=0; i<refFraw.length; i++) {\n')
  f.write('	if (lens[i] > 4 && lens[i] < 6) {\n')
  f.write('            refF[i]= 0;\n')
  f.write('            compF[i]= 0;\n')
  f.write('        }\n')
  f.write('	else {\n')
  f.write('            refF[i]= refFraw[i];\n')
  f.write('            compF[i]= compFraw[i];\n')
  f.write('	}\n')
  f.write('    }\n')
  f.write('    shiftObj = shift(refF,compF,lens,words);\n')
  f.write('    plotShift(d3.select("#figure01"),shiftObj.sortedMag.slice(0,200),\n')
  f.write('              shiftObj.sortedType.slice(0,200),\n')
  f.write('              shiftObj.sortedWords.slice(0,200),\n')
  f.write('              shiftObj.sumTypes,\n')
  f.write('              shiftObj.refH,\n')
  f.write('              shiftObj.compH);\n')
  f.write('\n')
  f.write('};\n')
  f.write('\n')
  f.write('initializePlot();\n')
  f.close()
  
  ## dump out a static shift view page
  ## need to replace all of the js loads
  f = open(outFile,'w')  
  f.write('<html>\n')
  f.write('<head>\n')
  f.write('<title>Simple Shift Plot</title>\n')
  f.write('<script src="static/d3.v3.min.js" charset="utf-8"></script>\n')
  f.write('<script src="static/plotShift.js" charset="utf-8"></script>\n')
  f.write('<script src="static/shift.js" charset="utf-8"></script>\n')
  f.write('<script src="static/drawLens.js" charset="utf-8"></script>\n')
  f.write('  <style>\n')
  f.write('    body {\n')
  f.write('      font-family: Verdana,Arial,sans-serif;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    h4 {\n')
  f.write('    font-size: .8em;\n')
  f.write('    margin: 60px 0 5px 0;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    h5 {\n')
  f.write('    font-size: .8em;\n')
  f.write('    margin: 10px 0 5px 0;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    body {\n')
  f.write('    min-width: 650px;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    #caption01 {\n')
  f.write('      width: 500px;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    #lens01 {\n')
  f.write('      width: 600px;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    #figure01 {\n')
  f.write('      width: 600px;\n')
  f.write('    }\n')
  f.write('\n')
  f.write('    .domain {\n')
  f.write('      fill: none;\n')
  f.write('      stroke: black;\n')
  f.write('      stroke-width: 2;\n')
  f.write('     }\n')
  f.write('\n')
  f.write('  </style>\n')
  f.write('</head>\n')
  f.write('<body>\n')
  f.write('\n')
  f.write('<div id="header"></div>\n')
  f.write('<center>\n')
  f.write('\n')
  f.write('<div id="caption01">\n')
  f.write('Move the stop-window to remove words from the lense.\n')
  f.write('Removing 4 though 6, the default, corresponds to the tuned hedonometer for large corpuses.</div>\n')
  f.write('<br>\n')
  f.write('\n')
  f.write('<div id="lens01" class="figure"></div>\n')
  f.write('\n')
  f.write('<br>\n')
  f.write('\n')
  f.write('Click on the graph and drag up to reveal additional words.\n')
  f.write('\n')
  f.write('<div id="figure01" class="figure"></div>\n')
  f.write('\n')
  f.write('</center>\n')
  f.write('\n')
  f.write('<div id="footer"></div>\n')
  f.write('\n')
  f.write('<script src="tmp.js" charset="utf-8"></script>\n')
  f.write('\n')
  f.write('</body>\n')
  f.write('</html>\n')
  f.close()

  if not os.path.exists('static'):
    os.mkdir('static')
  
  for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','drawLens.js']:
    if not os.path.isfile('static/'+staticfile):
      import shutil
      relpath = os.path.abspath(__file__).split('/')[1:-1]
      relpath.append('static')
      relpath.append(staticfile)
      fileName = ''
      for pathp in relpath:
        fileName += '/' + pathp    
      print 'copying over '+fileName
      shutil.copy(fileName,'static/'+staticfile)

if __name__ == '__main__':
  ## run from standard in
  import fileinput
  labMT = emotionFileReader(0.0)
  happsList = [emotion(line,labMT) for line in fileinput.input()]
  
  for value in happsList:
    print value
    
  






