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
            sentence = row[0].rstrip().lower()

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

        for line in csvfile:
            sentiment = [1,0,0,0]
            parts = line.rstrip().split(",")
            print(parts)
            if parts[2] == "positive":
                sentiment[1] += 1
                sentimentCounts[0] += 1
            elif parts[2] == "negative":
                sentiment[2] += 1
                sentimentCounts[1] += 1
            else:
                sentiment[3] +=1 
                sentimentCounts[2] += 1


            sentiments[parts[0]] = sentiment

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
    print(lst)
    raise(Error)



def getNGrams(string,n=3,singles=True):
    words = string.split(" ")

    grams = []

    if len(words) == 1:
        return words

    # Check for empty strings
    keepWords = []
    for word in words:
        if word != "":
            keepWords.append(word)

    words = keepWords

    for index, word in enumerate(words):
        if index == len(words)-(n-1):
            break

        grams.append(" ".join(words[index:index+n]))
    if singles:
        grams.extend(words)

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

    random.shuffle(corpus)

    output = open("sentimentResults.csv","w")
    output.write('"score","message"\n')

    failLoop = 0

    remaining = []

    newSentiments = {}
    newSentimentCounts = [0,0,0]

    while True:

        for docIndex, document in enumerate(corpus):
            documentScore = [1,1,1]

            keywords = []
            for word in document.split(" "):
                #if word not in stopwords and word != "":
                #    keywords.append(word)
                #    keywords.append(" ")
                if word != "":
                    keywords.append(word)
                    keywords.append(" ")


            documentKeywords = "".join(keywords).rstrip()

            grams = getNGrams(documentKeywords)
            nWords = len(document.split(" "))

            haveData = 0


            for classifier in range(3):
                classifierLikelihood = sentimentCounts[classifier] / sum(sentimentCounts)
                for index, gram in enumerate(grams):
                
                    if gram not in sentiments:
                        continue

                    haveData += 1

                    print(gram, sentiments[gram])

                    likelihood = sentiments[gram][classifier+1] / ( sentiments[gram][0])
                    likelihood += 1/nWords
                    classifierLikelihood *= likelihood

                documentScore[classifier] = classifierLikelihood
                
            if haveData == 0 and failLoop >= 0:
                remaining.append(document)
                corpus.remove(document)
                failLoop += 1
                continue


            print(len(sentiments)," -- ",sentimentCounts)

            failLoop = 0
            corpus.remove(document)

            documentScore = normalize(documentScore)
            print(documentScore)

            #index = weightedRandom(documentScore)
            index = documentScore.index(max(documentScore))

            if trainingPath == "None":
                response = input("{0} \x1B[39m-- {1}? (y/n): ".format(document, sentimentOptions[index])) 

                if response == "n":
                    while True:
                        try:
                            index = int(input("Is this positive, negative, or neutral(0/1/2): "))
                            break
                        except ValueError:
                            print("Incorrect response. Input numeric.")

            else:
                print("{0} -- {1}".format(document,sentimentOptions[index]))


            output.write('"{0}","{1}",{2}\n'.format(sentimentOptions[index],document.replace('"',"").replace("'","").replace(',',''),documentScore[index]))


            """
            No learning for now!
            """
            
            grams = getNGrams(documentKeywords, singles=False)

            for gram in grams:
                newSentimentCounts[index] += 1
                if gram in newSentiments:
                    newSentiments[gram][0] += 1
                    newSentiments[gram][index+1] += 1

                else:
                    data = [1,0,0,0]
                    data[index+1] = 1
                    newSentiments[gram] = data 
          

        if len(remaining) == 0:
            output.close()
            exit()
        else:
            input("Next iteration")
            sentiments = dict(list(sentiments.items()) + \
                              list(newSentiments.items()))
            for index, count in enumerate(sentimentCounts):
                sentimentCounts[index] += count
            corpus = remaining


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sentiment analysis on a corpus.')
    parser.add_argument('path', metavar='path', help="Path to the corpus")
    parser.add_argument('stopwordPath', metavar='stopwordPath',
                        help='Path to the stopword file.')
    parser.add_argument('--train', metavar='trainingPath', default="None",
                        help='Path to emoji training file.')
    args = parser.parse_args()


    main(args.path,args.stopwordPath,args.train)

