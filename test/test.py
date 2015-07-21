# note: nose2 will run all functions that begin with test

from labMTsimple.storyLab import *
from labMTsimple.speedy import *
import subprocess
import codecs

TOL = 1e-3

def test_b():
    assert 'b' == 'b'

def test_labMT_english():
    # load the basics
    lang = "english"
    labMT, labMTvector, labMTwordList = emotionFileReader(stopval = 0.0, lang=lang, returnVector=True)

    # make sure the words got loaded in correctly in the dictionary
    assert labMT["test"][1] == '4.06'
    # make sure the vector is aligned
    index = int(labMT["test"][0])-1
    assert labMTwordList[index] == 'test'
    assert labMTvector[index] == 4.06
    
    f = codecs.open("examples/data/18.01.14.txt", "r", "utf8")
    ref_text_raw = f.read()
    f.close()
    f = codecs.open("examples/data/21.01.14.txt", "r", "utf8")
    comp_text_raw = f.read()
    f.close()

    ref_happs, ref_freq = emotion(ref_text_raw, labMT, shift=True, happsList=labMTvector)
    comp_happs, comp_freq = emotion(comp_text_raw, labMT, shift=True, happsList=labMTvector)

    ref_freq_stopped = stopper(ref_freq, labMTvector, labMTwordList, stopVal=1.0)
    # make sure that it blocked "the" and "nigger"
    index = int(labMT["the"][0])-1
    assert ref_freq_stopped[index] == 0    
    index = int(labMT["nigger"][0])-1
    assert ref_freq_stopped[index] == 0

    ref_freq_stopped = stopper(ref_freq, labMTvector, labMTwordList, stopVal=1.0, ignore=["laughter"])
    # make sure that it blocked "the" and "nigger" still
    index = int(labMT["the"][0])-1
    assert ref_freq_stopped[index] == 0    
    index = int(labMT["nigger"][0])-1
    assert ref_freq_stopped[index] == 0
    # also check that it now blocked laughter    
    index = int(labMT["laughter"][0])-1
    assert ref_freq_stopped[index] == 0

    ref_freq_stopped = stopper(ref_freq, labMTvector, labMTwordList, stopVal=1.0)
    
    comp_freq_stopped = stopper(comp_freq, labMTvector, labMTwordList, stopVal=1.0)

    ref_happs_from_vector = emotionV(ref_freq, labMTvector)
    # make sure this is the same as from emotion
    print(ref_happs_from_vector)
    print(ref_happs)
    assert abs(ref_happs_from_vector - ref_happs) < TOL
    
    ref_happs_stopped = emotionV(ref_freq_stopped, labMTvector)
        
    # without stop words
    assert abs(ref_happs - 5.51733944613) < TOL
    assert ref_freq[5000] == 409

    # with stop words
    assert abs(ref_happs_stopped - 6.01346892642) < TOL
    assert ref_freq_stopped[5000] == 0

    outFile = "test-rsvg.html"
    shiftPDF(labMTvector, labMTwordList, ref_freq, comp_freq, outFile)
    
    # also make the inkscape version
    shiftHtml(labMTvector, labMTwordList, ref_freq, comp_freq, "test-inkscape.html")
    generateSVG("test-inkscape.html")
    generatePDF("test-inkscape.svg",program="inkscape")
    subprocess.call("open test-inkscape.pdf",shell=True)    
    
    sortedMag,sortedWords,sortedType,sumTypes = shift(ref_freq, comp_freq, labMTvector, labMTwordList)

    assert sortedMag[0] < 0
    assert sortedWords[0] == "love"
    
    shiftMag,shiftType,sumTypes = shift(ref_freq, comp_freq, labMTvector, labMTwordList, sort=False)
    

