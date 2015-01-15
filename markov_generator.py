#!/usr/bin/python

"""
markov_generator.py

Create a Markov chain from a corpra of text, and generate some text.
"""

import argparse
import csv

def loadCorpus(path):
    """
    Read a csv file containing documents, and return a list of the documents.

    Accepts:
        path: A string path to the corpus.

    Returns:
        corpus: A list of documents.
    """
    corpus = []

    with open(path,'r') as csvfile:
        reader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in reader:
            sentence = row[1].rstrip().lower()
            corpus.append(sentence)
            print(sentence)

    return corpus

def createNGram(corpus, n):
    """
    Count the transitions between an n-word chunk and another word.

    Accepts:
        corpus: A list of documents.
        n:      An integer of the number of words per n-gram.

    Returns:
        ngram:  A dictionary of n-grams with their associated probability. Each
                key is a tuple of n words, with a probability value.
    """

    #for document in corpus:
        

    pass

def main(path,n):
    """
    Load a corpus, count the transitions between trigrams, and generate a 
    probable sentance.
    """

    corpus = loadCorpus(args.path)
    ngrams = createNGram(corpus, args.n)

    print(ngrams)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a possible sequence of '+
                                     "words from a corpus of text.")
    parser.add_argument('path', metavar='path', help="Path to the corpus")
    parser.add_argument('n', metavar='n',type=int,
                        help='The number of words per n-gram.')
    args = parser.parse_args()

    main(args.path,args.n)
