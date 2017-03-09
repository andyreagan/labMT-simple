from distutils.core import setup
setup(name='sasa',
      version='0.1.3',
      description='SAIL/AIL Sentiment Analyzer',
      author='Abe Kazemzadeh',
      author_email='kazemzad@usc.edu',
      url='https://code.google.com/p/sasa-tool/',
      packages=['sasa'],
      package_dir={'sasa':'sasa'},
      package_data={'sasa': ['models/model.unigram.nb.bool.politics.unbiased']},
      install_requires=['nltk'],
      #package_data={'sasa': ['models/*']},
      license='apache 2.0',
      classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Sociology",
        "Topic :: Text Processing :: Linguistic"],
      long_description="""
===============================================
SASA Sentiment Analysis Tool
===============================================

This is a tool for doing sentiment analysis. The short-term goal of this
project is to share the sentiment analysis research. The long-term goal of
this project is to allow researchers the ability to demonstrate and test
sentiment analysis tools, so that performance can be evaluated and compared.

Currently, the models are trained on Twitter data from the 2012 US
Presidential election. In the future we hope to have general models as well as
models for other domains.

This code was first released by the collaboration of two labs at the
University of Southern California (USC), the Signal Analysis and
Interpretation Laboratory (SAIL) and Annenberg Innovation Laboratory
(AIL). The sentiment research at SAIL is supported by grants including NSF,
NIH, and DARPA. The sentiment research at AIL is sponsored by the lab
sponsors, especially IBM, an AIL founding sponsor, and Orange, the flagship
brand of France Telecom.

This work was made possible by using existing open source projects and
code. NLTK (nltk.org) provides some of the basic classes of the SASA tool,
e.g. frequency distributions and classifiers. Christopher Potts'
twitter-specific tokenizer for sentiment analysis is used for tokenization.
""",
      
      )
