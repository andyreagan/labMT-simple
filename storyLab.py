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
#   from storyLab import microscope
#   lens = microscope(0)
#   from storyLab import happiness
#   happs = happiness(tmpstr,lens)
#
# In a shell:
#   alias happiness="$(pwd)/storyLab.py"
#   cat storyLab.py | happiness
#   storyLab.py happiness
#
# written by Andy Reagan
# 2013-12-09

def microscope(stopval):
  ## stopval is our lens, \Delta h
  ## read the labMT dataset into a dict with this lens
  f = open('labMT1.txt','r')
  tmp = dict([(line.split('\t')[0],[x.rstrip() for x in line.split('\t')[1:]]) for line in f])
  f.close()
  ## remove words
  stopWords = []
  if stopval > 0:
    for word in tmp:
      if abs(float(tmp[word][1])-5.0) < stopval:
        stopWords.append(word)
  for word in stopWords:
    del tmp[word]
  return tmp

def happiness(tmpstr,LabMT):
  score_list = []
  # doing this without the NLTK
  words = [x.lower().lstrip("?';:.$%&()\\!*[]{}|\"<>,^-_=+").rstrip("@#?';:.$%&()\\!*[]{}|\"<>,^-_=+") for x in tmpstr.split()]
  for word in words:
    if word in LabMT:
      score_list.append(float(LabMT[word][1]))

  ## with numpy (and mean in the namespace)
  ## happs = mean(score_list)
  
  ## without numpy
  if len(score_list) > 0:
    happs = sum(score_list)/float(len(score_list))
  else:
    happs = 0
    
  return happs

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

if __name__ == '__main__':
  ## run from standard in
  import fileinput
  labMT = readLabMT(0)
  happsList = [happiness(line,labMT) for line in fileinput.input()]
  
  for value in happsList:
    print value
    
  


