# note: nose2 will run all functions that begin with test

from labMTsimple.storyLab import *
from labMTsimple.speedy import *
import subprocess
import codecs

TOL = 1e-3

def test_storyLab_labMT_english():
    """Test as much of storyLab as possible.

    Basically an extended example."""
    
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
    

def my_test_speedy(dictionary,test_dict,prefix=False):
    """Speedy test."""

    # lang = "english"
    # dictionary = "LabMT"
    print("loading {0}".format(dictionary))
    
    my_senti_dict = sentiDict(dictionary,datastructure="dict")
    dict_score = my_senti_dict.score(test_dict)
    dict_word_vec = my_senti_dict.wordVecify(test_dict)
    
    my_senti_marisa = sentiDict(dictionary,datastructure="marisatrie")
    marisa_score = my_senti_marisa.score(test_dict)
    marisa_word_vec = my_senti_marisa.wordVecify(test_dict)

    # this will actually seg fault....
    # my_senti_da = sentiDict(dictionary,datastructure="datrie")
    # da_score = my_senti_da.score(test_dict)
    # da_word_vec = my_senti_da.wordVecify(test_dict)

    print(dict_score)
    print(marisa_score)
    if not prefix:
        assert abs(dict_score-marisa_score) < TOL
        diff = dict_word_vec - marisa_word_vec
        print(dict_word_vec,marisa_word_vec)
        print(my_senti_dict.fixedwords[0])
        print(my_senti_marisa.fixedwords[0])
        print(len(my_senti_dict.stemwords))
        print(len(my_senti_marisa.stemwords))
        assert (dict_word_vec == marisa_word_vec).all()
    else:
        assert len(dict_word_vec) == len(marisa_word_vec)
        print(dict_word_vec,marisa_word_vec)
        print(my_senti_dict.fixedwords[0])
        print(my_senti_marisa.fixedwords[0])
        print(my_senti_dict.stemwords[0])
        print(my_senti_marisa.stemwords[0])


def test_speedy_all():
    """Test all of the speedy dictionaries on scoring some dict of words."""
    
    # generate a word dict to test
    f = codecs.open("examples/data/18.01.14.txt", "r", "utf8")
    ref_text_raw = f.read()
    f.close()
    test_dict = dict()
    replaceStrings = ['---','--','\'\'']
    for replaceString in replaceStrings:
        ref_text_raw = ref_text_raw.replace(replaceString,' ')
    words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",ref_text_raw,flags=re.UNICODE)]
    for word in words:
        if word in test_dict:
            test_dict[word] += 1
        else:
            test_dict[word] = 1
    
    titles = ['LabMT','ANEW','LIWC','MPQA','Liu','Warriner',]
    prefixes = [False,False,True,True,False,False,]
    for title,prefix_bool in zip(titles,prefixes):
        my_test_speedy(title,test_dict,prefix=prefix_bool)
