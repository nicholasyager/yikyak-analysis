#!/usr/bin/python3

import argparse
import csv
import random
import string

class Corpus:

    def __init__(self):
        pass

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
            neutral  = 1 - positive - negative

            if positive > negative:
                positive = 1
                negative = 0
                neutral  = 0
            elif positive < negative:
                positive = 0
                negative = 1
                neutral  = 0
            elif positive == negative:
                positive = 0
                negative = 0
                neutral  = 1

            value = (positive,negative,neutral)
            # split the SyssetTerms
            wordWithSense = row[4].split(' ')
            for term in wordWithSense:
                pair = term.split('#')
                word = pair[0]
                sense = int(pair[1])
                if sense == 1 and word not in sentiments and neutral != 1:
                    sentiments[word] = value
                     
    counts = [0,0,0]
    for key, values in sentiments.items():
        for index, value in enumerate(values):
            counts[index] += value

    return sentiments, counts

def loadStopwords(path):
    """
    Read a list of stopwords

    Accepts:
        path: A string path to the stopwords document

    Returns:
        stopwords: A list of stopwords

    """

    with open(path,"r") as f:
        stopwords = f.readlines()
        stopwords = [string.rstrip() for string in stopwords]

    return stopwords

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
        next(reader,None)
        for row in reader:
            sentence = row[1].rstrip().lower()
            if sentence not in corpus:
                corpus.append(sentence)

    return corpus

def loadTraining(path):
    """
    Read a csv file containing documents pre-classified for training."

    Accepts:
        path: A string path to the corpus.

    Returns:
        corpus: A list of documents.
    """
    sentiments = {}
    sentimentCounts = [0,0,0]

    with open(path,'r') as csvfile:
        reader = csv.reader(csvfile,delimiter=',',quotechar="'")
        next(reader,None)
        for row in reader:
            sentence = row[1].rstrip().lower()
            grams = getNGrams(sentence)
            if row[0] == "positive":
                incrementIndex = 1
            elif row[0] == "negative":
                incrementIndex = 2
            elif row[0] == "neutral":
                incrementIndex = 3

            for gram in grams:
                if gram in sentiments:
                    sentimentCounts[incrementIndex-1] += 1
                    sentiments[gram][incrementIndex] +=1
                    sentiments[gram][0] +=1
                else:
                    sentimentCounts[incrementIndex-1] += 1
                    data = [1,0,0,0]
                    data[incrementIndex] +=1
                    sentiments[gram] = data

    return sentiments, sentimentCounts


def normalize(lst):
    total = sum(lst)
    if total > 0:
        for index, element in enumerate(lst):
            lst[index] = element/total
    return lst

def maxIndex(lst):
    return lst.index(max(lst))

def weightedRandom(lst):

    total = 0
    reference = random.uniform(0,1)

    for index,element in enumerate(lst):
        total += element
        if total >= reference:
            return index

    raise(Error)



def getNGrams(string,n=3):
    words = string.split(" ")

    grams = []

    if len(words) == 1:
        return words

    for m in range(n):
        
        m += 1

        for index, word in enumerate(words):
            if index == len(words)-(m-1):
                break

            grams.append(" ".join(words[index:index+m]))


    return grams

def main(corpusPath, stopwordPath, trainingPath):
    
    sentimentCounts = [1,1,1]
    if trainingPath != "None":
        sentiments,sentimentCounts = loadTraining(trainingPath)
    else:
        sentiments = {}

    stopwords = loadStopwords(stopwordPath)

    corpus = loadCorpus(corpusPath)
    print("Loaded {0} documents.".format(len(corpus)))


    sentimentOptions = ["positive","negative","neutral"]

    color = ["\x1B[32m","\x1B[31m","\x1B[34m", "\x1B[39m"]

    exclude = set(string.punctuation)

    random.shuffle(corpus)

    output = open("sentimentResults.csv","w")
    output.write('"score","message"\n')

    for docIndex, document in enumerate(corpus):
        print(len(sentiments)," -- ",sentimentCounts)
        documentScore = [1,1,1]

        keywords = []
        for word in document.split(" "):
            if word not in stopwords and word != "":
                keywords.append(word)
                keywords.append(" ")

        documentKeywords = "".join(keywords).rstrip()

        strippedDocument = "".join([ch for ch in documentKeywords if ch not in exclude])
        grams = getNGrams(strippedDocument)
        nWords = len(document.split(" "))

        haveData = 0

        for classifier in range(3):
            classifierLikelihood = sentimentCounts[classifier] / sum(sentimentCounts)
            for index, gram in enumerate(grams):
            
                if gram not in sentiments:
                    continue

                haveData += 1

                likelihood = sentiments[gram][classifier+1] / sentiments[gram][0]
                likelihood += 1/nWords
                print(gram, likelihood)

                classifierLikelihood *= likelihood

            documentScore[classifier] = classifierLikelihood

        if haveData == 0 and docIndex != 0:
            corpus.append(document)
            continue

        documentScore = normalize(documentScore)
        print(documentScore)

        index = weightedRandom(documentScore)

        if trainingPath == "None":
            response = input("{0} \x1B[39m-- {1}? (y/n): ".format(document, sentimentOptions[index])) 

            if response == "n":
                index = int(input("Is this positive, negative, or neutral(0/1/2): "))

        else:
            print("{0} -- {1}".format(document,sentimentOptions[index]))


        output.write("'{0}','{1}'\n".format(sentimentOptions[index],document.replace('"',"").replace("'","")))

        for gram in grams:
            sentimentCounts[index] += 1
            if gram in sentiments:
                sentiments[gram][0] += 1
                sentiments[gram][index+1] += 1

            else:
                data = [1,0,0,0]
                data[index+1] = 1
                sentiments[gram] = data 
       
    output.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sentiment analysis on a corpus.')
    parser.add_argument('path', metavar='path', help="Path to the corpus")
    parser.add_argument('stopwordPath', metavar='stopwordPath',
                        help='Path to the stopword file.')
    parser.add_argument('trainingPath', metavar='trainingPath', default="None",
                        help='Path to training file')
    args = parser.parse_args()

    main(args.path,args.stopwordPath,args.trainingPath)

