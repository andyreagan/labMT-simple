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
import subprocess
from jinja2 import Template
from numpy import unique

def emotionFileReader(stopval=1.0,lang="english",min=1.0,max=9.0,returnVector=False):
    """Load the dictionary of sentiment words.
  
    Stopval is our lens, $\Delta _h$, read the labMT dataset into a dict with this lens (must be tab-deliminated).

    With returnVector = True, returns tmpDict,tmpList,wordList. Otherwise, just the dictionary."""

    labMT1flag = False
    scoreIndex = 1 # second value

    fileName = 'labMT/labMT2{0}.txt'.format(lang)

    try:
        f = codecs.open(fileName,'r','utf8')
    except IOError:
        fileName = os.path.join(os.path.dirname(__file__), 'data', fileName)
        f = codecs.open(fileName,'r','utf8')
    except:
        raise('could not open the needed file')

    # skip the first line
    f.readline()

    tmpDict = dict([(line.split(u'\t')[0].rstrip(u'"').lstrip(u'"'),
                     [x.rstrip(u'"') for x in line.split(u'\t')[1:]]) for line in f])

    f.close()
  
    # remove words
    stopWords = []

    for word in tmpDict:
        # start the index at 0
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

    # build vector of all scores
    f = codecs.open(fileName,'r','utf8')
    f.readline()
    tmpList = [float(line.split(u'\t')[2]) for line in f]
    f.close()
    # build vector of all words
    f = codecs.open(fileName,'r','utf8')
    f.readline()
    wordList = [line.split(u'\t')[0] for line in f]
    f.close()

    if returnVector:
        return tmpDict,tmpList,wordList
    else:
        return tmpDict

def emotion(tmpStr,someDict,scoreIndex=1,shift=False,happsList=[]):
    """Take a string and the happiness dictionary, and rate the string.

    If shift=True, will return a vector (also then needs the happsList)."""
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

    # this new replace isn't the exact same as the original parse
    # but it's closer to the one that MITRE developed, and I think
    # that it is an improvement
    replaceStrings = ['---','--','\'\'']
    for replaceString in replaceStrings:
        tmpStr = tmpStr.replace(replaceString,' ')
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

    # with numpy (and mean in the namespace)
    # happs = mean(scoreList)
  
    # without numpy
    if len(scoreList) > 0:
        happs = sum(scoreList)/float(len(scoreList))
    else:
        happs = 0

    if shift:
        return happs,freqList
    else:
        return happs

def stopper(tmpVec,score_list,word_list,stopVal=1.0,ignore=[],center=5.0):
    """Take a frequency vector, and 0 out the stop words.
  
    Will always remove the nig* words.
    
    Return the 0'ed vector."""

    ignoreWords = ["nigga","nigger","niggaz","niggas"];
    for word in ignore:
        ignoreWords.append(word)
    newVec = copy.copy(tmpVec)
    for i in range(len(score_list)):
        if abs(score_list[i]-center) < stopVal:
            newVec[i] = 0
        if word_list[i] in ignoreWords:
            newVec[i] = 0

    return newVec

def stopper_mat(tmpVec,score_list,word_list,stopVal=1.0,ignore=[],center=5.0):
    """Take a frequency vector, and 0 out the stop words.
  
    A sparse-aware matrix stopper.
    F-vecs are rows: [i,:]
    
    Will always remove the nig* words.
  
    Return the 0'ed matrix, sparse."""

    ignoreWords = ["nigga","nigger","niggaz","niggas"];
    for word in ignore:
        ignoreWords.append(word)
    indices_to_ignore = []
    for i in range(len(score_list)):
        if abs(score_list[i]-center) < stopVal:
            indices_to_ignore.append(i)
        if word_list[i] in ignoreWords:
            indices_to_ignore.append(i)
    indices_to_ignore = unique(indices_to_ignore)

    tmpVec[:,indices_to_ignore] = 0
  
    return tmpVec

def emotionV(frequencyVec,scoreVec):
    """Given the frequency vector and the score vector, compute the happs.
    
    Doesn't use numpy, but equivalent to `np.dot(freq,happs)/np.sum(freq)`."""
    
    tmpSum = sum(frequencyVec)
    if tmpSum > 0:
        happs = 0.0
        for i in range(len(scoreVec)):
            happs += frequencyVec[i]*float(scoreVec[i])
        happs = float(happs)/float(tmpSum)
        return happs
    else:
        return -1

def shift(refFreq,compFreq,lens,words,sort=True):
    """Compute a shift, and return the results.
    
    If sort=True, will return the three sorted lists, and sumTypes. Else, just the two shift lists, and sumTypes (words don't need to be sorted)."""
    
    # normalize frequencies
    Nref = float(sum(refFreq))
    Ncomp = float(sum(compFreq))
    for i in range(len(refFreq)):
       refFreq[i] = float(refFreq[i])/Nref
       compFreq[i] = float(compFreq[i])/Ncomp
    # compute the reference happiness
    refH = sum([refFreq[i]*lens[i] for i in range(len(lens))])
    # determine shift magnitude, type
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

def shiftHtmlJupyter(scoreList,wordList,refFreq,compFreq,outFile,corpus="LabMT",advanced=False,customTitle=False,title="",ref_name="reference",comp_name="comparison",ref_name_happs="",comp_name_happs="",isare="",saveFull=True,selfshift=False,bgcolor="white"):
    """Shifter that generates HTML in two pieces, designed to work inside of a Jupyter notebook.

    Saves the filename as given (with .html extension), and sneaks in a filename-wrapper.html, and the wrapper file has the html headers, everything to be a standalone file. The filenamed html is just the guts of the html file, because the complete markup isn't need inside the notebook."""

    import random
    divnum = int(random.uniform(0,9999999999))
    if len(ref_name_happs) == 0:
        ref_name_happs = ref_name.capitalize()
    if len(comp_name_happs) == 0:
        comp_name_happs = comp_name.capitalize()

    if not customTitle:
        title = "Example shift using {0}".format(corpus)
    
    if not os.path.exists('static'):
        os.mkdir('static')

    # strip off the .html
    outFileShort = outFile
    if outFile[-5:] == ".html":
        outFileShort = outFile[:-5]
      
    # write out the template
    lens_string = ','.join(map(lambda x: '{0:.12f}'.format(x),scoreList))
    words_string = ','.join(map(lambda x: '"{0}"'.format(x),wordList))
    refFreq_string = ','.join(map(lambda x: '{0:.0f}'.format(x),refFreq))
    compFreq_string = ','.join(map(lambda x: '{0:.0f}'.format(x),compFreq))

    wrapper = Template("""<html>
<head>
<title>Simple Shift Plot</title>
<link href="static/css/hedotools.shift.css" rel="stylesheet">
<script src="static/js/d3.js" charset="utf-8"></script>
<script src="static/js/jquery-1.11.0.min.js" charset="utf-8"></script>
<script src="static/js/urllib.js" charset="utf-8"></script>
<script src="static/js/hedotools.init.js" charset="utf-8"></script>
<script src="static/js/hedotools.shifter.js" charset="utf-8"></script>
</head>
<body>

<div id="header"></div>

{{ inner }}

</body>
</html>""")

    # dump out a static shift view page
    template = Template('''<center>
<div id="figure{{ divnum }}" class="figure"></div>
</center>
<script type="text/javascript">
    var lens = [{{ lens }}];
    var words = [{{ words }}];
    var refF = [{{ refF }}];
    var compF = [{{ compF }}];

    var my_shifter =  hedotools.shifter();
    my_shifter._refF(refF);
    my_shifter._compF(compF);
    my_shifter._lens(lens);
    my_shifter._words(words);

    // my_shifter.plotdist(true);

    // do the shifting
    {% if selfshift %}
    my_shifter.selfShifter();
    {% else %}
    my_shifter.shifter();
    {% endif %}

    my_shifter.setWidth(400);
    // my_shifter.setHeight(800);

    // don't use the default title
    // set own title
    // but leave all of the default sizes and labels
  
    // extract these:
    var compH = my_shifter._compH();
    var refH = my_shifter._refH();
    // from the code inside the shifter:
    if (compH >= refH) {
        var happysad = "happier";
    }
    else { 
        var happysad = "less happy";
	}

    // also from inside the shifter:
    // var comparisonText = splitstring(["Reference happiness: "+refH.toFixed(2),"Comparison happiness: "+compH.toFixed(2),"Why comparison is "+happysad+" than reference:"],boxwidth-10-logowidth,'14px arial');
    // our adaptation:
    var comparisonText = ["{{ title }}","","{{ ref_name_happs }} happiness: "+refH.toFixed(2),"{{ comp_name_happs }} happiness: "+compH.toFixed(2),"Why {{ comp_name }}{{ isare }}"+happysad+" than {{ ref_name }}:"];
    // set it:
    my_shifter.setText(comparisonText);
    my_shifter.setTextBold(0);
    my_shifter.setBgcolor("{{ bgcolor }}");
    my_shifter.setTopTextSizes([24,16,16,16,16]);
    my_shifter.setTextColors(["#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8",]);
    my_shifter.setFontSizes([16,10,22,11,8,8,13]);
    // [bigshifttextsize,xaxisfontsize,xylabelfontsize,wordfontsize,distlabeltext,creditfontsize,resetfontsize];

    my_shifter.setfigure(d3.select('#figure{{ divnum }}'));
    my_shifter.plot();

    // remove these right away....
    // d3.selectAll('g.resetbutton').remove();
    // d3.selectAll('.credit').remove();
</script>
''')

    if isare == "":
        isare = " is "
        if list(comp_name)[-1] == "s":
            isare = " are "
    f = codecs.open(outFile,'w','utf8')
    inner=template.render(lens=lens_string, words=words_string,
                            refF=refFreq_string, compF=compFreq_string,
                            title=title, ref_name=ref_name, comp_name=comp_name,
                            ref_name_happs=ref_name_happs, comp_name_happs=comp_name_happs,
                            isare=isare,divnum=divnum,selfshift=selfshift,bgcolor=bgcolor)
    f.write(inner)
    f.close()
    print("wrote shift to {}".format(outFile))

    if saveFull:
        f = codecs.open(outFileShort+"-wrapper.html",'w','utf8')
        f.write(wrapper.render(inner=inner))
        f.close()
        print("wrote wrapped shift html to {}".format(outFileShort+"-wrapper.html"))
    
def shiftHtml(scoreList,wordList,refFreq,compFreq,outFile,corpus="LabMT",advanced=False,customTitle=False,title="",ref_name="reference",comp_name="comparison",ref_name_happs="",comp_name_happs="",isare=""):
    """Make an interactive shift for exploring and sharing.

    The most insane-o piece of code here (lots of file copying,
    writing vectors into html files, etc).
    
    Accepts a score list, a word list, two frequency files 
    and the name of an HTML file to generate
    
    ** will make the HTML file, and a directory called static
    that hosts a bunch of .js, .css that is useful."""

    if len(ref_name_happs) == 0:
        ref_name_happs = ref_name.capitalize()
    if len(comp_name_happs) == 0:
        comp_name_happs = comp_name.capitalize()

    if not customTitle:
        title = "Example shift using {0}".format(corpus)
    
    if not os.path.exists('static'):
        os.mkdir('static')

    outFileShort = outFile.split('.')[0]
      
    # write out the template
    lens_string = ','.join(map(lambda x: '{0:.2f}'.format(x),scoreList))
    words_string = ','.join(map(lambda x: '"{0}"'.format(x),wordList))
    refFreq_string = ','.join(map(lambda x: '{0:.0f}'.format(x),refFreq))
    compFreq_string = ','.join(map(lambda x: '{0:.0f}'.format(x),compFreq))
    
    # dump out a static shift view page
    template = Template('''<html>
<head>
<title>Simple Shift Plot</title>
<link href="static/hedotools.shift.css" rel="stylesheet">
</head>
<body>

<div id="header"></div>
<center>

<div id="lens01" class="figure"></div>
<br>
<!-- <p>Click on the graph and drag up to reveal additional words.</p> -->

<br>

<div id="figure01" class="figure"></div>

</center>

<div id="footer"></div>

<script src="static/d3.js" charset="utf-8"></script>
<script src="static/jquery-1.11.0.min.js" charset="utf-8"></script>
<script src="static/urllib.js" charset="utf-8"></script>
<script src="static/hedotools.init.js" charset="utf-8"></script>
<script src="static/hedotools.shifter.js" charset="utf-8"></script>
<script type="text/javascript">
    var lens = [{{ lens }}];
    var words = [{{ words }}];
    var refF = [{{ refF }}];
    var compF = [{{ compF }}];

    var my_shifter =  hedotools.shifter();
    my_shifter._refF(refF);
    my_shifter._compF(compF);
    my_shifter._lens(lens);
    my_shifter._words(words);

    // my_shifter.plotdist(true);

    // do the shifting
    my_shifter.shifter();
    my_shifter.setWidth(400);
    // my_shifter.setHeight(800);

    // don't use the default title
    // set own title
    // but leave all of the default sizes and labels
  
    // extract these:
    var compH = my_shifter._compH();
    var refH = my_shifter._refH();
    // from the code inside the shifter:
    if (compH >= refH) {
        var happysad = "happier";
    }
    else { 
        var happysad = "less happy";
	}

    // also from inside the shifter:
    // var comparisonText = splitstring(["Reference happiness: "+refH.toFixed(2),"Comparison happiness: "+compH.toFixed(2),"Why comparison is "+happysad+" than reference:"],boxwidth-10-logowidth,'14px arial');
    // our adaptation:
    var comparisonText = ["{{ title }}","","{{ ref_name_happs }} happiness: "+refH.toFixed(2),"{{ comp_name_happs }} happiness: "+compH.toFixed(2),"Why {{ comp_name }}{{ isare }}"+happysad+" than {{ ref_name }}:"];
    // set it:
    my_shifter.setText(comparisonText);
    my_shifter.setTextBold(0);
    my_shifter.setTopTextSizes([24,16,16,16,16]);
    my_shifter.setTextColors(["#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8",]);
    my_shifter.setFontSizes([16,10,22,11,8,8,13]);
    // [bigshifttextsize,xaxisfontsize,xylabelfontsize,wordfontsize,distlabeltext,creditfontsize,resetfontsize];

    my_shifter.setfigure(d3.select('#figure01'));
    my_shifter.plot();

    // remove these right away....
    d3.selectAll('g.resetbutton').remove();
    d3.selectAll('.credit').remove();
</script>

</body>
</html>''')

    if isare == "":
        isare = " is "
        if list(comp_name)[-1] == "s":
            isare = " are "
    f = codecs.open(outFile,'w','utf8')
    f.write(template.render(outFileShort=outFileShort,
                            lens=lens_string, words=words_string,
                            refF=refFreq_string, compF=compFreq_string,
                            title=title, ref_name=ref_name, comp_name=comp_name,
                            ref_name_happs=ref_name_happs, comp_name_happs=comp_name_happs,
                            isare=isare))
    f.close()
    print("wrote shift to {}".format(outFile))
    # copy_static_files()
    link_static_files()

def shiftHtmlPreshifted(scoreList,wordList,refFreq,compFreq,outFile,corpus="LabMT",advanced=False,customTitle=False,title="",ref_name="reference",comp_name="comparison",ref_name_happs="",comp_name_happs="",isare=""):
    """Make an interactive shift for exploring and sharing.

    The most insane-o piece of code here (lots of file copying,
    writing vectors into html files, etc).
    
    Accepts a score list, a word list, two frequency files 
    and the name of an HTML file to generate
    
    ** will make the HTML file, and a directory called static
    that hosts a bunch of .js, .css that is useful."""

    if len(ref_name_happs) == 0:
        ref_name_happs = ref_name.capitalize()
    if len(comp_name_happs) == 0:
        comp_name_happs = comp_name.capitalize()

    if not customTitle:
        title = "Example shift using {0}".format(corpus)
    
    if not os.path.exists('static'):
        os.mkdir('static')

    sortedMag,sortedWords,sortedType,sumTypes = shift(refFreq,compFreq,scoreList,wordList,sort=True)

    outFileShort = outFile.split('.')[0]
      
    # write out the template
    sortedMag_string = ','.join(map(lambda x: '{0:.12f}'.format(x),sortedMag[:200]))
    sortedWords_string = ','.join(map(lambda x: '"{0}"'.format(x),sortedWords[:200]))
    sortedType_string = ','.join(map(lambda x: '{0:.0f}'.format(x),sortedType[:200]))
    sumTypes_string = ','.join(map(lambda x: '{0:.3f}'.format(x),sumTypes))

    # normalize frequencies
    Nref = float(sum(refFreq))
    Ncomp = float(sum(compFreq))
    for i in range(len(refFreq)):
        refFreq[i] = float(refFreq[i])/Nref
        compFreq[i] = float(compFreq[i])/Ncomp
    # compute the reference happiness
    refH = "{0:.4}".format(sum([refFreq[i]*scoreList[i] for i in range(len(scoreList))]))
    compH = "{0:.4}".format(sum([compFreq[i]*scoreList[i] for i in range(len(scoreList))]))
    
    # dump out a static shift view page
    template = Template('''<html>
<head>
<title>Simple Shift Plot</title>
<link href="static/hedotools.shift.css" rel="stylesheet">
</head>
<body>

<div id="header"></div>
<center>

<div id="lens01" class="figure"></div>
<br>
<!-- <p>Click on the graph and drag up to reveal additional words.</p> -->

<br>

<div id="figure01" class="figure"></div>

</center>

<div id="footer"></div>

<script src="static/d3.js" charset="utf-8"></script>
<script src="static/jquery-1.11.0.min.js" charset="utf-8"></script>
<script src="static/urllib.js" charset="utf-8"></script>
<script src="static/hedotools.init.js" charset="utf-8"></script>
<script src="static/hedotools.shifter.js" charset="utf-8"></script>
<script type="text/javascript">
    var sortedMag = [{{ sortedMag }}];
    var sortedWords = [{{ sortedWords }}];
    var sortedType = [{{ sortedType }}];
    var sumTypes = [{{ sumTypes }}];
    var refH = {{ refH }};
    var compH = {{ compH }};

    var my_shifter = hedotools.shifter();
    my_shifter._sortedMag(sortedMag);
    my_shifter._sortedWords(sortedWords);
	my_shifter._sortedType(sortedType);
	my_shifter._sumTypes(sumTypes);

    // my_shifter.plotdist(true);

    // do the shifting
    // my_shifter.shifter();
    my_shifter.setWidth(400);
    // my_shifter.setHeight(800);

    // don't use the default title
    // set own title
    // but leave all of the default sizes and labels
  
    // extract these:
    // from the code inside the shifter:
    if (compH >= refH) {
        var happysad = "happier";
    }
    else { 
        var happysad = "less happy";
	}

    // also from inside the shifter:
    // var comparisonText = splitstring(["Reference happiness: "+refH.toFixed(2),"Comparison happiness: "+compH.toFixed(2),"Why comparison is "+happysad+" than reference:"],boxwidth-10-logowidth,'14px arial');
    // our adaptation:
    var comparisonText = ["{{ title }}","","{{ ref_name_happs }} happiness: "+refH.toFixed(2),"{{ comp_name_happs }} happiness: "+compH.toFixed(2),"Why {{ comp_name }}{{ isare }}"+happysad+" than {{ ref_name }}:"];
    // set it:
    my_shifter.setText(comparisonText);
    my_shifter.setTextBold(0);
    my_shifter.setTopTextSizes([24,16,16,16,16]);
    my_shifter.setTextColors(["#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8","#D8D8D8",]);
    my_shifter.setFontSizes([16,10,22,11,8,8,13]);
    // [bigshifttextsize,xaxisfontsize,xylabelfontsize,wordfontsize,distlabeltext,creditfontsize,resetfontsize];

    my_shifter.setfigure(d3.select('#figure01'));
    my_shifter.plot();

    // remove these right away....
    d3.selectAll('g.resetbutton').remove();
    d3.selectAll('.credit').remove();
</script>

</body>
</html>''')

    if isare == "":
      isare = " is "
      if list(comp_name)[-1] == "s":
          isare = " are "
    f = codecs.open(outFile,'w','utf8')
    f.write(template.render(outFileShort=outFileShort,
                          sortedMag=sortedMag_string, sortedWords=sortedWords_string,
                          sortedType=sortedType_string, sumTypes=sumTypes_string,
                          title=title, ref_name=ref_name, comp_name=comp_name,
                          ref_name_happs=ref_name_happs, comp_name_happs=comp_name_happs,
                          refH=refH,compH=compH,
                          isare=isare))
    f.close()
    print("wrote shift to {}".format(outFile))
    # copy_static_files()
    link_static_files()

def copy_static_files():
    """Deprecated method to copy files from this module's static directory into the directory where shifts are being made."""
    # print('copying over static files')
    # for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','example-on-load.js']:
    for staticfile in ['d3.js','jquery-1.11.0.min.js','urllib.js','hedotools.init.js','hedotools.shifter.js','hedotools.shift.css','shift-crowbar.js']:
        if not os.path.isfile('static/'+staticfile):
            import shutil
            relpath = os.path.abspath(__file__).split('/')[1:-1]
            relpath.append('static')
            relpath.append(staticfile)
            fileName = ''
        for pathp in relpath:
            fileName += '/' + pathp
        shutil.copy(fileName,'static/'+staticfile)

def link_static_files():
    """Same as copy_static_files, but makes symbolic links."""
    # print('copying over static files')
    # for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','example-on-load.js']:
    for staticfile in ['d3.js','jquery-1.11.0.min.js','urllib.js','hedotools.init.js','hedotools.shifter.js','hedotools.shift.css','shift-crowbar.js']:
        if not os.path.isfile('static/'+staticfile):
            relpath = os.path.abspath(__file__).split('/')[1:-1]
            relpath.append('static')
            relpath.append(staticfile)
            fileName = '/'+'/'.join(relpath)
            subprocess.call("ln -s {0} {1}".format(fileName,'static/'+staticfile),shell=True)

if __name__ == '__main__':
    # run from standard in
    import fileinput
    labMT = emotionFileReader(0.0)
    happsList = [emotion(line,labMT) for line in fileinput.input()]
  
    for value in happsList:
        print(value)
    
  






