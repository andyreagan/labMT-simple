labMT-simple
============

TL;DR a simple labMT usage script

a python module for using the labMT1.0 dataset

no dependencies, unless using the plot function (then we use matplotlib)

Usage
-----

The Python script test.py uses this module to test a subsample of
Twitter data:

.. code:: python

    from storyLab import *
    labMT,labMTvector,labMTwordList = emotionFileReader(returnVector=True)

    ## take a look at these guys
    print labMT['laughter']
    print labMTvector[0:5]
    print labMTwordList[0:5]

    ## test shift a subsample of two twitter days
    import codecs ## handle utf8
    f = codecs.open("25.01.14.txt","r","utf8")
    saturday = f.read()
    f.close()
    f = codecs.open("28.01.14.txt","r","utf8")
    tuesday = f.read()
    f.close()

    ## compute valence score
    saturdayValence = emotion(saturday,labMT)
    tuesdayValence = emotion(tuesday,labMT)
    print 'the valence of {0} is {1}'.format('saturday',saturdayValence)
    print 'the valence of {0} is {1}'.format('tuesday',tuesdayValence)

    ## compute valence score and return frequency vector for generating wordshift
    saturdayValence,saturdayFvec = emotion(saturday,labMT,shift=True,happsList=labMTvector)
    tuesdayValence,tuesdayFvec = emotion(tuesday,labMT,shift=True,happsList=labMTvector)

    ## make a shift: shift(values,ref,comp)
    shiftMag,shiftType = shift(labMTvector,tuesdayFvec,saturdayFvec)
    ## take the absolute value of the shift magnitude
    shiftMagAbs = map(abs,shiftMag)

    ## sort them both
    indices = sorted(range(len(shiftMag)), key=shiftMagAbs.__getitem__, reverse=True)
    sortedMag = [shiftMag[i] for i in indices]
    sortedType = [shiftType[i] for i in indices]
    sortedWords = [labMTwordList[i] for i in indices]

    ## take a peek at the top words  
    print indices[0:10]
    print sortedMag[0:20]
    print sortedType[0:20]
    print sortedWords[0:20]

    ## print each of these to a file
    f = open("sampleSortedMag.csv","w")
    for val in sortedMag:
      f.write(str(val))
      f.write("\n")
    f.close()

    f = open("sampleSortedType.csv","w")
    for val in sortedType:
      f.write(str(val))
      f.write("\n")
    f.close()

    f = open("sampleSortedWords.csv","w")
    for val in sortedWords:
      f.write(val)
      f.write("\n")
    f.close()

