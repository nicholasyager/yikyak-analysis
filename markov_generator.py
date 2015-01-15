#!/usr/bin/python

"""
markov_generator.py

Create a Markov chain from a corpra of text, and generate some text.
"""

import argparse
import csv
import random

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

    nGrams = {}

    for document in corpus:

        words = document.split(" ")

        for index, word in enumerate(words):
            # Do not go past the end of the sentence.
            if index > len(words)-n:
                break

            gramList = []

            for jump in range(n):
                gramList.append(words[index+jump])
            gram = tuple(gramList)

            if gram in nGrams:
                nGrams[gram] += 1
            else:
                nGrams[gram] = 1
        

    return nGrams

def weightedRandom(probList):
    """
    Return the index picked from a list of probabilities.
    """
    sum = 0
    reference = random.randint(0,1)
    for index, prob in enumerate(probList):
        sum += prob
        if sum >= reference:
            return index
    return len(probList)-1

def main(path,n):
    """
    Load a corpus, count the transitions between trigrams, and generate a 
    probable sentance.
    """

    punctuation = [".","!","?",")","("]

    corpus = loadCorpus(args.path)
    print("Loaded a corpus of {0} documents.".format(len(corpus)))
    nGrams = createNGram(corpus, args.n)
    gramList = list(nGrams.keys())
    print("Generated {0} {1}-grams.".format(len(nGrams),n))

    string = ""
    maxString = ""

    # Select an n-gram to start with
    currentGram = random.choice(gramList)
    oldGram = tuple(["" for index in range(n)])
    totalProbability = 1
    currentProbability = 1
    for attempt in range(1000):
        
        # Find all related n-grams
        possibilities = [gram for gram in gramList if gram[0:n-1] == currentGram[0:n-1]]
   
        if len(possibilities) == 0:
            string +=  " " +" ".join(currentGram[1:])
            if totalProbability < currentProbability:
                currentProbability = totalProbability
                maxString = string
            currentGram = random.choice(gramList)
            string = currentGram[0]
            totalProbability =1
            continue

        totalCounts = 0
        counts = []
        probabilities = []

        for key in possibilities:
            count = nGrams[key]
            totalCounts += count
            counts.append(count)

        for count in counts:
            probabilities.append(count/totalCounts)
       
        # Pick a gram to continue with
        nextIndex = weightedRandom(probabilities)
        totalProbability *= probabilities[nextIndex]
        oldGram = currentGram
        currentGramList = [word for index, word in enumerate(possibilities[nextIndex]) if  0 < index <= n-1]
        currentGramPad = [""]
        currentGramList.extend(currentGramPad)
        currentGram = tuple(currentGramList)
        string += " " + currentGram[0]
        

    print(maxString, currentProbability)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a possible sequence of '+
                                     "words from a corpus of text.")
    parser.add_argument('path', metavar='path', help="Path to the corpus")
    parser.add_argument('n', metavar='n',type=int,
                        help='The number of words per n-gram.')
    args = parser.parse_args()

    main(args.path,args.n)
