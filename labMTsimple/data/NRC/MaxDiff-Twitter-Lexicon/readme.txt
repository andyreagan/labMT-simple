MaxDiff Twitter Sentiment Lexicon
Version 1.0
24 December 2014
Copyright (C) 2014 National Research Council Canada (NRC)
Contact: Saif Mohammad (saif.mohammad@nrc-cnrc.gc.ca)

**********************************************
TERMS OF USE
**********************************************

1. This lexicon can be used freely for research purposes. 
2. The paper listed below provides details of the creation and use of the lexicon. If you use a lexicon, then please cite the associated paper:
	Kiritchenko, S., Zhu, X., Mohammad, S. (2014). Sentiment Analysis of Short Informal Texts.  Journal of Artificial Intelligence Research, 50:723-762, 2014.
3. If interested in commercial use of the lexicon, send email to the contact. 
4. If you use the lexicon in a product or application, then please credit the authors and NRC appropriately. Also, if you send us an email, we will be thrilled to know about how you have used the lexicon.
5. National Research Council Canada (NRC) disclaims any responsibility for the use of the lexicon and does not provide technical support. However, the contact listed above will be happy to respond to queries and clarifications.
6. Rather than redistributing the data, please direct interested 
   parties to this page:
   http://www.purl.com/net/lexicons 

We will be happy to hear from you:
- with feedback regarding the lexicon. 
- with information on how you have used the lexicon. 
- if interested in having us analyze your data for sentiment, emotion, and other affectual information.
- if interested in a collaborative research project.


**********************************************
DESCRIPTION
**********************************************

The lexicon provides real-valued scores for the strength of association of terms with positive sentiment. The sentiment annoations were done manually through Mechanical Turk using the MaxDiff method of annotation.

 
**********************************************
DATA SOURCE
**********************************************

High-frequency terms from the Sentiment140 Corpus and the Hashtag Sentiment Corpus were manually annotated for sentiment using the MaxDiff method. The lexicon includes regular English words, Twitter-specific terms (e.g., emoticons, abbreviations, creative spellings), and negated expressions.

For more details, refer to Section 6.1.2 in
	Kiritchenko, S., Zhu, X., Mohammad, S. (2014). Sentiment Analysis of Short Informal Texts.  Journal of Artificial Intelligence Research, 50:723-762, 2014.


**********************************************
FILE FORMAT
**********************************************

This lexicon is available in two forms: (a) with scores between 0 (most negative) and 1 (most positive), and (b) with scores between -1 (most negative) and 1 (most positive). 

The files has the following format:
 - each line corresponds to a unique term;
 - each line has the format: term<TAB>score
where 'score' is the strength of association with positive sentiment:
- In “Maxdiff-Twitter-Lexicon_0to1” it is a number between 0 (most negative) and 1 (most positive).
- In “Maxdiff-Twitter-Lexicon_-1to1” it is a number between -1 (most negative) and 1 (most positive).

**********************************************
More Information
**********************************************
Details on the process of creating the lexicon can be found in:
Kiritchenko, S., Zhu, X., Mohammad, S. (2014). Sentiment Analysis of Short Informal Texts.  Journal of Artificial Intelligence Research, 50:723-762, 2014.

 
