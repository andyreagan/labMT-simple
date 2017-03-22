# note: nose2 will run all functions that begin with test

from labMTsimple.storyLab import *
from labMTsimple.speedy import *
import subprocess
import codecs
from json import loads
from jinja2 import Template

# this has some useful functions
# sys.path.append("/Users/andyreagan/tools/python/")
# from kitchentable.dogtoys import *

TOL = 1e-3

def storyLab_labMT_english():
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

    outFile = "test.html"
    shiftHtml(labMTvector, labMTwordList, ref_freq, comp_freq, outFile)

    outFile = "test-stopped.html"    
    shiftHtml(labMTvector, labMTwordList, ref_freq_stopped, comp_freq_stopped, outFile)
    
    # # also make the inkscape version
    # shiftHtml(labMTvector, labMTwordList, ref_freq, comp_freq, "test-inkscape.html")
    # generateSVG("test-inkscape.html")
    # generatePDF("test-inkscape.svg",program="inkscape")
    # subprocess.call("open test-inkscape.pdf",shell=True)
    
    sortedMag,sortedWords,sortedType,sumTypes = shift(ref_freq, comp_freq, labMTvector, labMTwordList)

    assert sortedMag[0] < 0
    assert sortedWords[0] == "love"
    
    shiftMag,shiftType,sumTypes = shift(ref_freq, comp_freq, labMTvector, labMTwordList, sort=False)

def speedy_dict_marisa_test(my_senti_dict,my_senti_marisa,test_dict):
    """Speedy test."""

    # lang = "english"
    # dictionary = "LabMT"
    print("loading {0}".format(my_senti_dict.title))
    
    dict_score = my_senti_dict.score(test_dict)
    dict_word_vec = my_senti_dict.wordVecify(test_dict)
    marisa_score = my_senti_marisa.score(test_dict)
    marisa_word_vec = my_senti_marisa.wordVecify(test_dict)

    print(dict_score)
    print(marisa_score)
    if not my_senti_dict.stems:
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
    if my_senti_marisa.matcherTrieBool(u"happy"):
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
        print("the dude abides!")
    
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
    '''Generate a word dict to test.'''
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

def speedy_dict_marisa_test_all():
    ref_dict = open_codecs_dictify("examples/data/18.01.14.txt")
    comp_dict = open_codecs_dictify("examples/data/21.01.14.txt")

    # this test the loading for each
    senti_dicts = [LabMT(),ANEW(),LIWC(),MPQA(),Liu(),WK(),]
    senti_marisas = [LabMT(datastructure="marisatrie"),ANEW(datastructure="marisatrie"),LIWC(datastructure="marisatrie"),MPQA(datastructure="marisatrie"),Liu(datastructure="marisatrie"),WK(datastructure="marisatrie"),]
    stopVal = 1.0
    for senti_dict,senti_marisa in zip(senti_dicts,senti_marisas):
        
        my_test_speedy(senti_dict,senti_marisa,ref_dict)

        # build it out here
        ref_word_vec = senti_marisa.wordVecify(ref_dict)
        ref_word_vec_stopped = senti_marisa.stopper(ref_word_vec,stopVal=stopVal)
        comp_word_vec = senti_marisa.wordVecify(comp_dict)
        comp_word_vec_stopped = senti_marisa.stopper(comp_word_vec,stopVal=stopVal)        
        shiftHtml(senti_marisa.scorelist, senti_marisa.wordlist, ref_word_vec_stopped, comp_word_vec_stopped, "test-shift-{0}.html".format(senti_dict.title),corpus=senti_marisa.corpus)

        shiftHtml(senti_marisa.scorelist, senti_marisa.wordlist, ref_word_vec, comp_word_vec, "test-shift-titles.html".format(senti_dict.title),customTitle=True,title="Insert title here",ref_name="bananas",comp_name="apples")

def load_26():
    all_sentiment_dictionaries = [LabMT(),ANEW(),LIWC01(),LIWC07(),LIWC15(),MPQA(),OL(),WK(),PANASX(),Pattern(),SentiWordNet(),AFINN(),GI(),WDAL(),EmoLex(),Sent140Lex(),SOCAL(),SenticNet(),Emoticons(),SentiStrength(),VADER(),Umigon(),USent(),EmoSenticNet()]
    # MaxDiff(),HashtagSent(),
    # SASA(),WNA(),SANN()

def write_table():
    # all_sentiment_dictionaries = [LabMT(),ANEW(),LIWC07(),MPQA(),OL(),WK(),LIWC01(),LIWC15(),PANASX(),Pattern(),SentiWordNet(),AFINN(),GI(),WDAL(),EmoLex(),MaxDiff(),HashtagSent(),Sent140Lex(),SOCAL(),SenticNet(),Emoticons(),SentiStrength(),VADER(),Umigon(),USent(),EmoSenticNet()]
    all_sentiment_dictionaries = [LabMT(),
                                  ANEW(),
                                  LIWC07(),
                                  MPQA(),
                                  OL(),
                                  WK(),
                                  LIWC01(),
                                  LIWC15(),
                                  PANASX(),
                                  Pattern(),
                                  SentiWordNet(),
                                  AFINN(),
                                  GI(),
                                  WDAL(),
                                  EmoLex(),
                                  MaxDiff(),
                                  HashtagSent(),
                                  Sent140Lex(),
                                  SOCAL(),
                                  SenticNet(),
                                  Emoticons(),
                                  SentiStrength(),
                                  VADER(),
                                  Umigon(),
                                  USent(),
                                  EmoSenticNet()]

    for sentiment_dictionary in all_sentiment_dictionaries:
        sentiment_dictionary.computeStatistics(0.0)

    table_template = Template(r'''{\scriptsize
  \begin{tabular*}{\linewidth}{ l | l | l | l | l | l}
  %% \begin{tabular*}{l}{ l | l | l | l | l | l | l | l | l | l}
    \hline
    Dictionary & \# Entries & Range & Construction & License & Ref.\\
    \hline
    \hline{% for sentiment_dictionary in all_sentiment_dictionaries %}{% if loop.index is equalto 7 %}
    \hline{% endif %}
    {{ sentiment_dictionary.title }} & {{ sentiment_dictionary.n_total | int }} & {{ sentiment_dictionary.score_range_str }} & {{ sentiment_dictionary.construction_note }} & {{ sentiment_dictionary.license }} & \cite{ {{- sentiment_dictionary.citation_key -}} }\\{% endfor %}
\end{tabular*}}
''')

    f = open("tex/maintable-automatic-short.tex","w")
    f.write(table_template.render({"all_sentiment_dictionaries": all_sentiment_dictionaries}))
    f.close()
    
    f = open("tex/maintable-automatic.tex","w")
    f.write(r"""  {\scriptsize
  \begin{tabular*}{\linewidth}{ l | l | l | l | l | l | l | l | l | l}
    \hline
    Dictionary & \# Fixed & \# Stems & Total & Range & \# Pos & \# Neg & Construction & License & Ref.\\
    \hline
    \hline
""")
    
    for i,sentiment_dictionary in enumerate(all_sentiment_dictionaries):
        print(i+1,sentiment_dictionary.title)
        if i==6:
            f.write("\\hline\n")
        f.write("    {0} & {1:.0f} & {2:.0f} & {3:.0f} & {4} & {5:.0f} & {6:.0f} & {7} & {8} & \\cite{{{9}}}\\\\\n".format(sentiment_dictionary.title,
                                                            sentiment_dictionary.n_fixed,
                                                            sentiment_dictionary.n_stem,
                                                            sentiment_dictionary.n_total,
                                                            sentiment_dictionary.score_range_str,
                                                            sentiment_dictionary.n_pos,
                                                            sentiment_dictionary.n_neg,
                                                            sentiment_dictionary.construction_note,
                                                            sentiment_dictionary.license,
                                                            sentiment_dictionary.citation_key))
    f.write("""  \end{tabular*}}
""")
    f.close()
    
    f = open("tex/body-description.tex","w")
    f.write(r"""\begin{description} \itemsep1pt \parskip1pt \parsep0pt
""")
    for i,sentiment_dictionary in enumerate(all_sentiment_dictionaries):
        f.write("    \\item[{0}] --- {1} \\cite{{{2}}}.\n".format(sentiment_dictionary.title,
                                                            sentiment_dictionary.note,
                                                            sentiment_dictionary.citation_key))
    f.write(r"""  \end{description}
""")
    f.close()
    
def test_speedy_all():
    """Test all of the speedy dictionaries on scoring some dict of words."""
    # speedy_dict_marisa_test_all()
    # storyLab_labMT_english()
    # LIWC_other_features()
    load_26()
    # write_table()

    cleanup()
    
def cleanup():
    '''Remove all test files.'''
    print("removing all test files generated...go comment the \"cleanup()\" call to keep them")
    subprocess.call("\\rm -r test-* static",shell=True)

def LIWC_other_features():
    """Test LIWC on scoring all word types from the set."""

    # load up some words
    ref_dict = open_codecs_dictify("examples/data/18.01.14.txt")
    # ref_dict = {"i": 1,"am": 1,"happy":5}
    ref_wordcount = sum([ref_dict[word] for word in ref_dict])
    print("ref dict loaded, has {0} words".format(ref_wordcount))
    
    # initialize LIWC
    my_LIWC = LIWC()

    # make a word vector
    my_word_vec = my_LIWC.wordVecify(ref_dict)
    print("word vec made, has {0} length".format(len(my_word_vec)))
    print(sum(my_word_vec))
    print(my_word_vec)

    happs = dot(my_word_vec,my_LIWC.scorelist)/sum(my_word_vec)
    print("happs={0}".format(happs))

    all_features = zeros(len(my_LIWC.data["happy"])-2)
    for word in my_LIWC.data:
        all_features += array(my_LIWC.data[word][2:])*my_word_vec[my_LIWC.data[word][0]]
    # normalize by total number of words
    all_features = all_features/ref_wordcount
    print(all_features)
    print("all features has length: {0}".format(len(all_features)))
    print(all_features[47])

    print(my_LIWC.word_types)
    values = [my_LIWC.word_types[key] for key in my_LIWC.word_types]
    values.sort(key=lambda k: k[0])

    for value in values:
        print("LIWC_{0}".format(value[1]))

my_LIWC_stopped = LIWC(stopVal=0.5)
my_LIWC = LIWC()
my_LabMT = LabMT(stopVal=1.0)
my_ANEW = ANEW(stopVal=1.0)
def all_features(rawtext,uid,tweet_id,gram_id):
    '''Return the feature vector for a given tweets.

    Be careful about indexing!
    Assuming here that we're taking in text of the tweet/gram'''

    # create  simple list for the result
    result = [0 for i in range(75)]
    # the first field, tableID, is not included (leaving 75)
    result[0] = tweet_id
    result[1] = gram_id
    result[2] = uid

    words = listify(rawtext)
    word_dict = dictify(words)
    result[3] = len(words)

    # load the classes that we need

    # print(len(my_LIWC.data))
    # print(len(my_LIWC.scorelist))
    my_word_vec = my_LIWC_stopped.wordVecify(word_dict)
    # print(len(my_word_vec))
    # print(sum(my_word_vec))
    happs = my_LIWC_stopped.score(word_dict)
    # print(len(my_LIWC.data))
    # print(len(my_LIWC.scorelist))
    # print(happs)
    result[4] = sum(my_word_vec)
    result[5] = happs

    my_word_vec = my_LabMT.wordVecify(word_dict)
    happs = my_LabMT.score(word_dict)
    # print(len(my_word_vec))
    # print(sum(my_word_vec))
    # print(happs)
    result[6] = sum(my_word_vec)
    result[7] = happs
    my_word_vec = my_ANEW.wordVecify(word_dict)
    happs = my_ANEW.score(word_dict)
    # print(len(my_word_vec))
    # print(sum(my_word_vec))
    # print(result)
    result[8] = sum(my_word_vec)
    result[9] = happs

    # make a word vector
    my_word_vec = my_LIWC.wordVecify(word_dict)
    all_features = zeros(len(my_LIWC.data["happy"])-2)
    for word in my_LIWC.data:
        all_features += array(my_LIWC.data[word][2:])*my_word_vec[my_LIWC.data[word][0]]
    for i,score in enumerate(all_features):
        result[10+i] = all_features[i]

    return result
    
def all_features_test():
    f = codecs.open("test/example-tweets.json" ,"r", "utf8")
    i = 0
    for line in f:
        tweet = loads(line)
        tweet_features = all_features(tweet['text'],tweet['user']['id'],tweet['id'],-1)
        # print(tweet['text'])
        # print(tweet_features)

        # for regular testing, don't do them all...
        if i>100:
            break
        
        #endfor
        
    f.close()
    
    # f = open("example_grams.json" ,"r", "utf8")
    # for line in f:
    #     gram = loads(line)
    #     gram_features = all_features(gram['text'],gram['user']['id'],-1,gram['id'])
    # f.close()

