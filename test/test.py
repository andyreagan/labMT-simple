from labMTsimple.storyLab import *
import subprocess

def test_b():
    assert 'b' == 'b'

def setup_test(lang):
    labMT,labMTvector,labMTwordList = emotionFileReader(stopval = 0.0, fileName ='labMT2'+lang+'.txt',returnVector=True)
    import codecs
    f = codecs.open("data/18.01.14.txt","r","utf8")
    ref = f.read()
    f.close()
    f = codecs.open("data/21.01.14.txt","r","utf8")
    comp = f.read()
    f.close()
    return [labMT,labMTvector,labMTwordList,ref,comp]

def do_test_stopwords(dataobject):
    happs,freqList = emotion(dataobject[3],dataobject[0],shift=True,happsList=dataobject[1])
    happsComp,freqListComp = emotion(dataobject[4],dataobject[0],shift=True,happsList=dataobject[1])

    stoppedVec = stopper(freqList,dataobject[1],dataobject[2],stopVal=1.0)
    stoppedVecComp = stopper(freqListComp,dataobject[1],dataobject[2],stopVal=1.0)

    happs2 = emotionV(stoppedVec,dataobject[1])
    
    return [happs,freqList,happs2,stoppedVec,stoppedVecComp]

def do_test_shift(dataobject,stopword_output,outputfile):
    print "making shift html"
    shiftHtml(dataobject[1],dataobject[2],stopword_output[3],stopword_output[4],outputfile)

def make_test_assertions(test_output,fname):    
    TOL = 1e-10

    # without stop words
    assert abs(test_output[0] - 5.51733944613) < TOL
    assert test_output[1][5000] == 409
    print "passed without stop words"

    # with stop words
    assert abs(test_output[2] - 6.01346892642) < TOL
    assert test_output[3][5000] == 0
    print "passed with stop words"

def cleanup_after_test(fname):
    # there are two options here
    # 1) clean everything up (uncomment second block) if the pdf can't be made
    # 2) leave all the files (comment everything)

    try:
        print "this will definitely only work for me"
        subprocess.check_output("phantomjs /Users/andyreagan/work/2014/2014-09d3-crowbar-chrome-automation/phantom-crowbar.js /Users/andyreagan/work/2014/labMTsimple/test.html shiftsvg test.svg",shell=True)
        subprocess.check_output("inkscape -f test.svg -A test.pdf",shell=True)
        # subprocess.check_output("\\rm "+fname,shell=True)
        # subprocess.check_output("\\rm test.svg",shell=True)
        # subprocess.check_output("\\rm -r static",shell=True)
        print "check test.pdf for the shift"
    except:
        print "didn't work, of course"
        print "don't cleanup yet to check the files"
        print "the static directory, and test.html are left to inspect"
        # subprocess.check_output("\\rm "+fname,shell=True)
        # subprocess.check_output("\\rm example-data.js",shell=True)
        # subprocess.check_output("\\rm -r static",shell=True)        


def test_labMT_english():
   dataobject = setup_test("english")
   try:
      test_output = do_test_stopwords(dataobject)
      fname = "test.html"
      do_test_shift(dataobject,test_output,fname)
      make_test_assertions(test_output,fname)
   finally:
      cleanup_after_test(fname)    





