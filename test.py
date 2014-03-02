## set up
from storyLab import *
labMT,labMTvector,labMTwordList = emotionFileReader(returnVector=True)
print labMT['laughter']
print labMTvector[0:5]
print labMTwordList[0:5]

## for testing
happyWords = "happy happy happy happy"
sadWords = "sad sad sad sad sad"

## for more testing
f = open("test/lance.txt","r")
happyWords = f.read()
f.close()
f = open("test/gop.txt","r")
sadWords = f.read()
f.close()

## test vectors
happyHapps,happyHappsL = emotion(happyWords,labMT,shift=True,happsList=labMTvector)
sadHapps,sadHappsL = emotion(sadWords,labMT,shift=True,happsList=labMTvector)
print "lance is {0}".format(happyHapps)
print "gop is {0}".format(sadHapps)
print sadHappsL[5986]

## make a shift: shift(values,ref,comp)
shiftMag,shiftType = shift(labMTvector,happyHappsL,sadHappsL)
shiftMagAbs = map(abs,shiftMag)

## sort them both
indices = sorted(range(len(shiftMag)), key=shiftMagAbs.__getitem__, reverse=True)
sortedMag = [shiftMag[i] for i in indices]
sortedType = [shiftType[i] for i in indices]
sortedWords = [labMTwordList[i] for i in indices]
  
print indices[0:10]
print sortedMag[0:20]
print sortedType[0:20]
print sortedWords[0:20]

f = open("test/sampleSortedMag.csv","w")
for val in sortedMag:
  f.write(str(val))
  f.write("\n")
f.close()

f = open("test/sampleSortedType.csv","w")
for val in sortedType:
  f.write(str(val))
  f.write("\n")
f.close()

f = open("test/sampleSortedWords.csv","w")
for val in sortedWords:
  f.write(val)
  f.write("\n")
f.close()


