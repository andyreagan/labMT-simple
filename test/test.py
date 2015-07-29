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

    comp_happs_stopped = emotionV(comp_freq_stopped, labMTvector)

    ref_happs_stopped = emotionV(ref_freq_stopped, labMTvector)
        
    # without stop words
    assert abs(ref_happs - 5.51733944613) < TOL
    assert ref_freq[5000] == 409

    # with stop words
    assert abs(ref_happs_stopped - 6.01346892642) < TOL
    assert ref_freq_stopped[5000] == 0

    print("-"*80)
    print(ref_happs)
    print(ref_happs_stopped)
    print(comp_happs)
    print(comp_happs_stopped)
    print("-"*80)    

    outFile = "test-rsvg.html"
    shiftPDF(labMTvector, labMTwordList, ref_freq, comp_freq, outFile, open_pdf=True)

    outFile = "test-rsvg-stopped.html"    
    shiftPDF(labMTvector, labMTwordList, ref_freq_stopped, comp_freq_stopped, outFile, open_pdf=True)
    
    # also make the inkscape version
    shiftHtml(labMTvector, labMTwordList, ref_freq, comp_freq, "test-inkscape.html")
    generateSVG("test-inkscape.html")
    generatePDF("test-inkscape.svg",program="inkscape")
    # subprocess.call("open test-inkscape.pdf",shell=True)    
    
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

    # check that they all match happy
    if my_senti_marisa.matcherTrieBool("happy"):
        print("happy is in the list")
    else:
        print("happy is *NOT* in the list")

    # let's find the index of the word happy in each
    # this is really a word-by-word test, because
    # of the stem matching
    word = u"happy"
    happy_dict = {word: 1}
    happy_vec = my_senti_marisa.wordVecify(happy_dict)
    assert sum(happy_vec) == 1
    index = list(happy_vec).index(1)
    print("index of the happy match: {0}".format(index))
    # 3,30,222,2221,2818,5614    
    print("length of fixed words: {0}".format(len(my_senti_marisa.fixedwords)))

    word = u"abide"
    print("checking on {0}".format(word))
    happy_dict = {word: 1}
    happy_vec = my_senti_marisa.wordVecify(happy_dict)
    if my_senti_marisa.matcherTrieBool(word):
        my_index = list(happy_vec).index(1)
        print(my_index)
        print(marisa_word_vec[my_index])
    
    print("count in test text: {0}".format(marisa_word_vec[index]))
    print(test_dict["happy"])
    print(test_dict["happyy"])
    print(test_dict["happyyy"])

    # checked that no dictionaries match anything beyond happy in the stems
    # so, they must match it fixed
    # => check it right against the straight count
    assert test_dict["happy"] == marisa_word_vec[index]

    if index > len(my_senti_marisa.fixedwords):
        print("matched by a stem")
        print(my_senti_marisa.stemwords[index-len(my_senti_marisa.fixedwords)])
    else:
        print("matched by a fixed word")
        print(my_senti_marisa.fixedwords[index])
def open_codecs_dictify(file):
    # generate a word dict to test
    f = codecs.open(file, "r", "utf8")
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
    return test_dict

def test_speedy_all():
    """Test all of the speedy dictionaries on scoring some dict of words."""

    test_dict = open_codecs_dictify("examples/data/18.01.14.txt")
    ref_dict = test_dict
    comp_dict = open_codecs_dictify("examples/data/21.01.14.txt")

    # this test the loading for each
    titles = ['LabMT','ANEW','LIWC','MPQA','Liu','Warriner',]
    prefixes = [False,False,True,True,False,False,]
    stopVal = 1.0
    for title,prefix_bool in zip(titles,prefixes):
        my_test_speedy(title,test_dict,prefix=prefix_bool)

        # build it out here
        my_senti_marisa = sentiDict(title,datastructure="marisatrie")
        ref_word_vec = my_senti_marisa.wordVecify(ref_dict)
        ref_word_vec_stopped = my_senti_marisa.stopper(ref_word_vec,stopVal=stopVal)
        comp_word_vec = my_senti_marisa.wordVecify(comp_dict)
        comp_word_vec_stopped = my_senti_marisa.stopper(comp_word_vec,stopVal=stopVal)        
        shiftPDF(my_senti_marisa.scorelist, my_senti_marisa.wordlist, ref_word_vec_stopped, comp_word_vec_stopped, "test-shift-{0}.html".format(title),corpus=my_senti_marisa.corpus)

    shiftPDF(my_senti_marisa.scorelist, my_senti_marisa.wordlist, ref_word_vec, comp_word_vec, "test-shift-titles.html".format(title),customTitle=True,title="Insert title here",ref_name="bananas",comp_name="apples")
    
def cleanup():
    subprocess.call("\\rm -r test-* static",shell=True)


