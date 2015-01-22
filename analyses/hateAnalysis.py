#!/usr/bin/python3

import argparse
import csv

def loadSentiments(path):
    """
    Parse a WordNet database for use in sentiment analysis.

    Accepts:
        path: A string to the WordNet file.

    Returns:
        sentiments: A tuple of (positive,objective,negative) scores for words.
    """

    sentiments = {}

    with open(path,"r") as wordnetFile:
        csvreader = csv.reader(filter(lambda row: row[0]!='#',wordnetFile),
                               delimiter="\t")
        for row in csvreader:

            # Check for empty lines
            if row[0] == '':
                continue

            positive = float(row[2])
            negative = float(row[3])
            objective = 1 - positive - negative
            value = (positive,objective,negative)
            # split the SyssetTerms
            wordWithSense = row[4].split(' ')
            for term in wordWithSense:
                pair = term.split('#')
                word = pair[0]
                sense = int(pair[1])
                if sense == 1 and word not in sentiments:
                    sentiments[word] = value
                     
    
    return sentiments

def loadHate(path):
    """
    Read a csv list of words found in hate speech.

    Accepts:
        path: A path to the csv of hate speech.

    Returns:
        hateDict: A dictionary of words and their offensiveness.
    """

    hateDict = {}
    classCounts = [0,0,0,0,0,0,0,0]

    with open(path,"r") as wordnetFile:
        csvreader = csv.reader(wordnetFile,delimiter=",")
        next(csvreader, None) #Skip the header
        for row in csvreader:
            # Check for empty lines
            if row[0] == '' or row[0] in hateDict:
                continue

            word = row[0]
            offense = float(row[8])
            if offense <= 0.25:
                continue
            if offense == 0:
                offense = 0.1
            classification = [float(row[1]),float(row[2]),float(row[3]),
                              float(row[4]),float(row[5]),float(row[6]),
                              float(row[7]),0]
            total = sum(classification)
            for index,classifier in enumerate(classification):
                classification[index] /= total
            
            hateDict[word] = classification
    # Normalize classifiers
    totalTokens = len(hateDict)
    laplacian = 1/totalTokens
    for word, classification in hateDict.items():
        for index, classifier in enumerate(classification):
            classCounts[index] += classifier

    return hateDict, classCounts

def loadCorpus(path):
    """
    Read a csv file containing documents, and return a list of the documents.

    Accepts:
        path: A string path to the corpus.

    Returns:
        corpus: A list of documents.
    """

    wordCounts = {}
    corpus = []

    with open(path,'r') as csvfile:
        reader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in reader:
            sentence = row[1].rstrip().lower()
            if sentence not in corpus:
                for word in sentence.split(' '):
                    if word in wordCounts:
                        wordCounts[word] += 1
                    else:
                        wordCounts[word] = 1
                corpus.append(sentence)

    return corpus, wordCounts


def main(corpusPath, wordnetPath):
    
    corpus,wordCounts = loadCorpus(corpusPath)
    totalWords = sum([count for key, count in wordCounts.items()])
    print("Loaded {0} documents.".format(len(corpus)))

    hateWords, classCounts = loadHate(wordnetPath)
    laplacian = 1/sum(classCounts)
    print("Loaded {0} hate words.".format(len(hateWords)))

    classes = ["ethnicity","nationality","religion","gender","sexuality","disability","class","none"]

    totals = [0,0,0,0,0,0,0,0]

    for document in corpus:
        documentScore = [1,1,1,1,1,1,1,1]
        possible = False
        for token in document.split(" "):
            score = [1,1,1,1,1,1,1,1]

            if token in hateWords:
                possible = True
                hateWordClass = hateWords[token]
                for classifier in range(8):
                    likelihood = hateWordClass[classifier] + laplacian
                    prior = 1/8
                    #prior = classCounts[classifier]/sum(classCounts)
                    score[classifier] = likelihood * prior
                totalScore = sum(score)
                if possible:
                    print(score,token)

                for classifier in range(8):
                    #score[classifier] /= totalScore
                    documentScore[classifier] *= score[classifier]
        if possible:
            totalScore = sum(documentScore)
            for classifier in range(8):
                documentScore[classifier] /= totalScore
        else:
            documentScore = [0,0,0,0,0,0,0,1]
        maxIndex = documentScore.index(max(documentScore))
        #print(documentScore)
        #print(document,classes[maxIndex])
        totals[maxIndex] += 1
    print(totals)



        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sentiment analysis on a corpus.')
    parser.add_argument('path', metavar='path', help="Path to the corpus")
    parser.add_argument('wordnetPath', metavar='wordnetPath',
                        help='Path to the WordNet sentiments file.')
    args = parser.parse_args()

    main(args.path,args.wordnetPath)

