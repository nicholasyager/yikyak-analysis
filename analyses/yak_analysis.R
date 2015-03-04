rm(list=ls())
par(mfrow=c(1,1))
packages <- c('tm','SnowballC','wordcloud')
for (index in 1:length(packages)){
  package = packages[index]
  exists = require(package,character.only = T)
  if (exists == FALSE) {
    install.packages(package)
    require(package,character.only = T)
  }
}

data <- read.csv("allposts.csv",header=F,stringsAsFactors=F)
names(data) <- c("ID","User","string","score","lat","lon","date")
data <- unique(data)

data2 <- read.csv("savedyaks.csv", header=T, stringsAsFactors=F)
names(data2) <- c("ID","string","score")
data2 <- unique(data2)

data$score <- as.numeric(data$score,na.rm=T)

strings <- append(data$string, data2$string)

corpus <- VCorpus(VectorSource(strings))
#inspect(corpus)
# Remove punctionation and convert to lowercase
corpus <- tm_map(corpus, stripWhitespace)
corpus <- tm_map(corpus,content_transformer(tolower))
corpus <- tm_map(corpus, removeWords, append(stopwords("english"),c("just", "like", "get")) )
corpus <- tm_map(corpus,removePunctuation)

#corpusDictionary <- corpus
# # Remove stems
#corpus <- tm_map(corpus,stemDocument)
# # Restem to normalize words
#corpus <- tm_map(corpus,stemCompletion, dictionary=corpusDictionary)


documentMatrix <- TermDocumentMatrix(corpus, control = list(minWordLength = 1))
#inspect(documentMatrix)

commonWords <- removeSparseTerms(x=documentMatrix, sparse=0.999)
colorfunc <- colorRampPalette(c("#345290","#86c1ea","#a7a9ac"))

#commonWords <- documentMatrix

m <- as.matrix(commonWords)
v <- sort(rowSums(m), decreasing=T)
documentNames <- names(v)
d <- data.frame(word=documentNames, freq=v)
#png("wordcloud%03d.png",width=500, height=500)
#wordcloud(d$word, d$freq, min.freq=3, col=colorfunc(length(d$word)),random.order=F,
#          ordered.colors=T,scale=c(5,0.5))
#dev.off()
png("wordcloud_freq-%03d.png",width=500, height=500)
wordcloud(d$word[1:400],
          d$freq[1:400],
          min.freq=1, col=colorfunc(400),
          ordered.colors=T,scale=c(4,0.5),random.order=F)
dev.off()
# tf-idf ----------------------------------

matrix = as.matrix(documentMatrix)
idfMatrix = matrix
idfMatrix[which(idfMatrix > 0)] = 1
idf = log(ncol(matrix)/sort(rowSums(idfMatrix), decreasing=F))
wordNames <- names(idf)
d2 <- data.frame(word=wordNames, freq=idf)
samples = sort(sample(1:nrow(d2),300),decreasing=F)

keywords = c()
keywordScores = c()
for (documentIndex in 1:ncol(matrix)){
  termFrequencies = matrix[,documentIndex]
  termIndices = which(termFrequencies > 0)
  if (length(termIndices) > 0) {
    documentTFIDFs = data.frame()
    words = c()
    for (index in 1:length(termIndices)) {
      termIndex = termIndices[index]
      tf = termFrequencies[termIndex]
      termIDF = d2$freq[which(d2$word == names(tf))]
      tfidf = tf * termIDF
      words = append(words,names(tf))
      documentTFIDFs = rbind(documentTFIDFs,c(tfidf))
    }
    row.names(documentTFIDFs) = words
    names(documentTFIDFs) <- c("score")
    sortedDocument = order(documentTFIDFs$score, decreasing = T)
    print(paste(rownames(documentTFIDFs)[sortedDocument[1]],documentTFIDFs[sortedDocument[1],]))

    keyword = rownames(documentTFIDFs)[sortedDocument[1]]
    score =  documentTFIDFs[sortedDocument[1],1]

    if (keyword %in% keywords) {
      index = which(keywords == keyword)
      keywordScores[index] = keywordScores[index] + 1
    } else {
      keywords = append(keywords, keyword)
      keywordScores  = append(keywordScores, 1)
    }

  }
}
keywordData = data.frame(keyword = keywords, score=keywordScores)
orderedIndices = order(keywordData$score, decreasing = T)
#samples = sort(sample(orderedIndices,400),decreasing=F)
samples = orderedIndices[1:400]
png("wordcloud_tfidf-%03d.png",width=500, height=500)
wordcloud(keywordData$keyword[samples],
          keywordData$score[samples],
          min.freq=1, col=colorfunc(length(samples)),
          ordered.colors=T,scale=c(3,0.5),random.order=F)
dev.off()

# General Stats ----------------------------------------------------------------

# Load the Yaks and label accordingly
data <- read.csv("savedyaks.csv",header=T,stringsAsFactors=F)
names(data) <- c("ID","string","score")

# Calculate the number of characters per Yak
lengths <- sapply(data$string,nchar)

# Calculate the number of words per Yak
words <- sapply(sapply(data$string, strsplit, " "), length)

png("lexical_histogram.png", width=500, height=500)
par(mfrow=c(2,1))
hist(lengths,probability = F,col="#345290",
               main="Number of Characters per Geneseo Yak",
               xlab="Number of Characters")
hist(words,probability = F,col="#7f8182",
     main="Number of Words per Geneseo Yak",
     xlab="Number of Words")
par(mfrow=c(1,1))
dev.off()

sentiments <- read.csv("../sentimentResults.csv",header=T)

barColors <- c("#905234","#7f8182","#345290")

par(mar=c(5.1,4.1,2.1,2.1))
barplot(table(sentiments$score)/nrow(sentiments),
        names=c("Negative","Neutral","Positive"),
        ylab="Proportion of Yaks",
        xlab="Sentiment",
        col=barColors
        )
abline(h=0)

yaks <- table(sentiments$score)/nrow(sentiments)
tweets <- c(0.3554217, 0.2791165, 0.3654618)

labels <- rep(c("Negative","Neutral","Positive"),2)
sources <- append(rep(c("Yak"),3),rep(c("Tweet"),3))
vec <- append(yaks, tweets)

df <- data.frame(source=sources, sentiment=labels, value=vec)

barplot(rbind(yaks, tweets), beside=T,
        names=c("Negative","Neutral","Positive"),
        ylab="Proportion of Documents",
        xlab="Sentiment",
        legend=c("Yaks","Tweets"))
abline(h=0)

par(mar=c(5.1,4.1,2.1,2.1))
barplot(tweets,
        names=c("Negative","Neutral","Positive"),
        ylab="Proportion of Tweets",
        xlab="Sentiment",
        col=barColors
)



barplot
abline(h=0)


