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
import re
import codecs
import copy

def emotionFileReader(stopval=1.0,lang="english",min=1.0,max=9.0,returnVector=False):
  ## stopval is our lens, \Delta h
  ## read the labMT dataset into a dict with this lens
  ## must be tab-deliminated

  labMT1flag = False
  scoreIndex = 1 # second value

  fileName = 'labMT/labMT2{0}.txt'.format(lang)

  try:
    f = codecs.open(fileName,'r','utf8')
  except IOError:
    relpath = os.path.abspath(__file__).split(u'/')[1:-1]
    relpath.append('data')
    relpath.append(fileName)
    fileName = '/'+'/'.join(relpath)
    f = codecs.open(fileName,'r','utf8')
  except:
    raise('could not open the needed file')

  # skip the first line
  f.readline()

  tmpDict = dict([(line.split(u'\t')[0].rstrip(u'"').lstrip(u'"'),
        [x.rstrip(u'"') for x in line.split(u'\t')[1:]]) for line in f])

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
  f = codecs.open(fileName,'r','utf8')
  f.readline()
  tmpList = [float(line.split(u'\t')[2]) for line in f]
  f.close()
  ## build vector of all words
  f = codecs.open(fileName,'r','utf8')
  f.readline()
  wordList = [line.split(u'\t')[0] for line in f]
  f.close()

  if returnVector:
    return tmpDict,tmpList,wordList
  else:
    return tmpDict

def emotionFileReaderRaw(stopval=1.0,fileName=u'labMT1raw.txt',min=1.0,max=9.0,returnVector=False):

  try:
    f = codecs.open(fileName,'r','utf8')
  except IOError:
    relpath = os.path.abspath(__file__).split('/')[1:-1]
    relpath.append('data')
    relpath.append('labMT1raw.txt')
    fileName = ''
    for pathp in relpath:
      fileName += '/' + pathp
    f = codecs.open(fileName,'r','utf8')

  tmpDict = dict()

  while f:
    word = f.readline()
    tmpDict[word] = []
    for i in range(10):
      tmpDict[word].append(map(int,f.readline().split(u'\t'))[1])
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
    freqList = [0 for i in range(len(happsList))]

  # doing this without the NLTK
  # words = [x.lower().lstrip(u"?';:.$%&()\\!*[]{}|\"<>,^-_=+").rstrip(u"@#?';:.$%&()\\!*[]{}|\"<>,^-_=+") for x in re.split(u'\s',tmpStr,flags=re.UNICODE)]
  
  # better re search
  # keeping all of the non-alphanumeric chars that show up inside words in the labMT set
  # which were found by:
  # lang = "english";
  # labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)
  # charset = set([])
  # for word in labMTwordList:
  #     if len(re.findall('[^\w]+',word)) > 0:
  #         for i in range(len(re.findall('[^\w]+',word))):
  #             charset.add(re.findall('[^\w]+',word)[i])

  words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",tmpStr,flags=re.UNICODE)]

  # only use the if shifting
  if shift:
    for word in words:
      if word in someDict:
        scoreList.append(float(someDict[word][scoreIndex]))
        freqList[int(someDict[word][0])-1] += 1
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

def stopper(tmpVec,labMTvector,labMTwords,stopVal=1.0,ignore=[]):
  ignoreWords = ["nigga","nigger","niggaz","niggas"];
  for word in ignore:
    ignoreWords.append(word)
  newVec = copy.copy(tmpVec)
  for i in range(len(labMTvector)):
    if abs(labMTvector[i]-5.0) < stopVal:
      newVec[i] = 0
    if labMTwords[i] in ignoreWords:
      newVec[i] = 0

  return newVec

def emotionV(frequencyVec,scoreVec):
  tmpSum = sum(frequencyVec)
  if tmpSum > 0:
    happs = 0.0
    for i in range(len(scoreVec)):
      happs += frequencyVec[i]*float(scoreVec[i])
    happs = float(happs)/float(tmpSum)
    return happs
  else:
    return -1

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

def shift(refFreq,compFreq,lens,words,sort=True):
  ## normalize frequencies
  Nref = float(sum(refFreq))
  Ncomp = float(sum(compFreq))
  for i in range(len(refFreq)):
    refFreq[i] = float(refFreq[i])/Nref
    compFreq[i] = float(compFreq[i])/Ncomp
  ## compute the reference happiness
  refH = sum([refFreq[i]*lens[i] for i in range(len(lens))])
  ## determine shift magnitude, type
  shiftMag = [0 for i in range(len(lens))]
  shiftType = [0 for i in range(len(lens))]
  for i in range(len(lens)):
    freqDiff = compFreq[i]-refFreq[i]
    shiftMag[i] = (lens[i]-refH)*freqDiff
    if freqDiff > 0:
      shiftType[i] += 2
    if lens[i] > refH:
      shiftType[i] += 1

  indices = sorted(range(len(shiftMag)), key=lambda k: abs(shiftMag[k]), reverse=True)
  sumTypes = [0.0 for i in range(4)]
  for i in range(len(lens)):
    sumTypes[shiftType[i]] += shiftMag[i]

  sortedMag = [shiftMag[i] for i in indices]
  sortedType = [shiftType[i] for i in indices]
  sortedWords = [words[i] for i in indices]

  if sort:
    return sortedMag,sortedWords,sortedType,sumTypes
  else:
    return shiftMag,shiftType,sumTypes

def shiftHtml(scoreList,wordList,refFreq,compFreq,outFile):
  if not os.path.exists('static'):
    os.mkdir('static')

  ## write out the template
  f = codecs.open('static/'+outFile.split('.')[0]+'-data.js','w','utf8')
  # f.write('function initializePlot() { loadCsv(); }\n\n')

  ## dump the data
  # f.write('function loadCsv() {\n')
  f.write('lens = [')
  for score in scoreList:
    f.write(str(score)+',')
  f.write('];\n\n')
  f.write('words = [')
  for word in wordList:
    f.write('"'+str(word)+'",')
  f.write('];\n\n')
  f.write('refFraw = [')
  for freq in refFreq:
    f.write('{0:.0f},'.format(freq))
  f.write('];\n\n')
  f.write('compFraw = [')
  for freq in compFreq:
    f.write('{0:.0f},'.format(freq))
  f.write('];\n\n')
  f.close()
  
  ## dump out a static shift view page
  f = codecs.open(outFile,'w','utf8')  
  f.write('<html>\n')
  f.write('<head>\n')
  f.write('<title>Simple Shift Plot</title>\n')

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
  f.write('<link href="static/hedotools.shift.css" rel="stylesheet">\n')
  f.write('</head>\n')
  f.write('<body>\n')
  f.write('\n')
  f.write('<div id="header"></div>\n')
  f.write('<center>\n')
  # f.write('<div id="lens01" class="figure"></div>\n')
  # f.write('\n')
  # f.write('<br>\n')
  # f.write('\n')
  f.write('<p>Click on the graph and drag up to reveal additional words.</p>\n')
  f.write('\n')
  f.write('<br>\n')
  f.write('\n')
  f.write('<div id="figure01" class="figure"></div>\n')
  f.write('\n')
  f.write('</center>\n')
  f.write('\n')
  f.write('<div id="footer"></div>\n')
  f.write('\n')
  f.write('<script src="static/d3.andy.js" charset="utf-8"></script>\n')
  f.write('<script src="static/jquery-1.11.0.min.js" charset="utf-8"></script>\n')
  f.write('<script src="static/urllib.js" charset="utf-8"></script>\n')
  f.write('<script src="static/hedotools.init.js" charset="utf-8"></script>\n')
  f.write('<script src="static/hedotools.shifter.js" charset="utf-8"></script>\n')
  f.write('<script src="static/'+outFile.split('.')[0]+'-data.js" charset="utf-8"></script>\n')
  f.write('<script src="static/example-on-load.js" charset="utf-8"></script>\n')
  f.write('\n')
  f.write('</body>\n')
  f.write('</html>\n')
  f.close()


  
  # for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','example-on-load.js']:
  for staticfile in ['d3.andy.js','jquery-1.11.0.min.js','urllib.js','hedotools.init.js','hedotools.shifter.js','example-on-load.js','hedotools.shift.css']:
    if not os.path.isfile('static/'+staticfile):
      import shutil
      relpath = os.path.abspath(__file__).split('/')[1:-1]
      relpath.append('static')
      relpath.append(staticfile)
      fileName = ''
      for pathp in relpath:
        fileName += '/' + pathp    
      shutil.copy(fileName,'static/'+staticfile)

def shiftHtmlSelf(scoreList,wordList,compFreq,outFile):
  if not os.path.exists('static'):
    os.mkdir('static')

  ## write out the template
  f = codecs.open('static/'+outFile.split('.')[0]+'-data.js','w','utf8')
  # f.write('function initializePlot() { loadCsv(); }\n\n')

  ## dump the data
  # f.write('function loadCsv() {\n')
  f.write('lens = [')
  for score in scoreList:
    f.write(str(score)+',')
  f.write('];\n\n')
  f.write('words = [')
  for word in wordList:
    f.write('"'+str(word)+'",')
  f.write('];\n\n')
  f.write('compFraw = [')
  for freq in compFreq:
    f.write('{0:.0f},'.format(freq))
  f.write('];\n\n')
  f.close()
  
  ## dump out a static shift view page
  f = codecs.open(outFile,'w','utf8')  
  f.write('<html>\n')
  f.write('<head>\n')
  f.write('<title>Simple Shift Plot</title>\n')

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
  f.write('<link href="static/hedotools.shift.css" rel="stylesheet">\n')
  f.write('</head>\n')
  f.write('<body>\n')
  f.write('\n')
  f.write('<div id="header"></div>\n')
  f.write('<center>\n')
  # f.write('<div id="lens01" class="figure"></div>\n')
  # f.write('\n')
  # f.write('<br>\n')
  # f.write('\n')
  f.write('<p>Click on the graph and drag up to reveal additional words.</p>\n')
  f.write('\n')
  f.write('<br>\n')
  f.write('\n')
  f.write('<div id="figure01" class="figure"></div>\n')
  f.write('\n')
  f.write('</center>\n')
  f.write('\n')
  f.write('<div id="footer"></div>\n')
  f.write('\n')
  f.write('<script src="static/d3.andy.js" charset="utf-8"></script>\n')
  f.write('<script src="static/jquery-1.11.0.min.js" charset="utf-8"></script>\n')
  f.write('<script src="static/urllib.js" charset="utf-8"></script>\n')
  f.write('<script src="static/hedotools.init.js" charset="utf-8"></script>\n')
  f.write('<script src="static/hedotools.shifter.js" charset="utf-8"></script>\n')
  f.write('<script src="static/'+outFile.split('.')[0]+'-data.js" charset="utf-8"></script>\n')
  f.write('<script src="static/example-on-load-self.js" charset="utf-8"></script>\n')
  f.write('\n')
  f.write('</body>\n')
  f.write('</html>\n')
  f.close()


  
  # for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','example-on-load.js']:
  for staticfile in ['d3.andy.js','jquery-1.11.0.min.js','urllib.js','hedotools.init.js','hedotools.shifter.js','example-on-load-self.js','hedotools.shift.css']:
    if not os.path.isfile('static/'+staticfile):
      import shutil
      relpath = os.path.abspath(__file__).split('/')[1:-1]
      relpath.append('static')
      relpath.append(staticfile)
      fileName = ''
      for pathp in relpath:
        fileName += '/' + pathp    
      shutil.copy(fileName,'static/'+staticfile)

  # shutil.copy(outFile,'static/template.html')

if __name__ == '__main__':
  ## run from standard in
  import fileinput
  labMT = emotionFileReader(0.0)
  happsList = [emotion(line,labMT) for line in fileinput.input()]
  
  for value in happsList:
    print(value)
    
  






