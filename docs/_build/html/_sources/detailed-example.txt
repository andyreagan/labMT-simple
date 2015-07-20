Detailed Examples
=================

Preparing texts
---------------

This is simple really: just load the text to be scored into python.
I'm using a subset of a couple days of public tweets to text, and I've already put the tweet text into `.txt` files that I load into strings:

```python
f = codecs.open("data/18.01.14.txt","r","utf8")
saturday = f.read()
f.close()

f = codecs.open("data/21.01.14.txt","r","utf8")
tuesday = f.read()
f.close()
```


Loading dictionaries
--------------------

Again this is really simple, just use the `emotionFileReader` function:
```python
lang = 'english'
labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
```

Then we can score the text and get the word vector at the same time:

```python
saturdayValence,saturdayFvec = emotion(saturday,labMT,shift=True,happsList=labMTvector)
tuesdayValence,tuesdayFvec = emotion(tuesday,labMT,shift=True,happsList=labMTvector)
```

But we don't want to use these happiness scores yet, because they included all words (including neutral words).
So, set all of the neutral words to 0, and generate the scores:


```python
tuesdayStoppedVec = stopper(tuesdayFvec,labMTvector,labMTwordList,stopVal=1.0)
saturdayStoppedVec = stopper(saturdayFvec,labMTvector,labMTwordList,stopVal=1.0)

saturdayValence = emotionV(saturdayStoppedVec,labMTvector)
tuesdayValence = emotionV(tuesdayStoppedVec,labMTvector)
```
