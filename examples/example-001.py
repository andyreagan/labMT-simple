import sys, os
from labMTsimple.storyLab import *
import codecs ## handle utf8

if __name__ == '__main__':
  lang = 'english'
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
  
  ## take a look at these guys
  print('the word laughter in the hash has the data:')
  print(labMT['laughter'])
  print('the top 5 scores, and those words, are:')
  print(labMTvector[0:5])
  print(labMTwordList[0:5])
  
  ## test shift a subsample of two twitter days
  f = codecs.open("data/18.01.14.txt","r","utf8")
  saturday = f.read()
  f.close()
  
  f = codecs.open("data/21.01.14.txt","r","utf8")
  tuesday = f.read()
  f.close()
  
  ## compute valence score
  print('computing happiness...')
  
  ## compute valence score and return frequency vector for generating wordshift
  saturdayValence,saturdayFvec = emotion(saturday,labMT,shift=True,happsList=labMTvector)
  tuesdayValence,tuesdayFvec = emotion(tuesday,labMT,shift=True,happsList=labMTvector)

  ## but we didn't apply a lens yet, so stop the vectors first
  tuesdayStoppedVec = stopper(tuesdayFvec,labMTvector,labMTwordList,stopVal=1.0)
  saturdayStoppedVec = stopper(saturdayFvec,labMTvector,labMTwordList,stopVal=1.0)

  saturdayValence = emotionV(saturdayStoppedVec,labMTvector)
  tuesdayValence = emotionV(tuesdayStoppedVec,labMTvector)
  
  print('the valence of {0} is {1:.5}'.format('saturday',saturdayValence))
  print('the valence of {0} is {1:.5}'.format('tuesday',tuesdayValence))


