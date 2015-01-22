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

data <- read.csv("savedyaks.csv",header=F,stringsAsFactors=F)
names(data) <- c("ID","string","score")
data <- unique(data)

data$score <- as.numeric(data$score,na.rm=T)

corpus <- VCorpus(VectorSource(data$string))
#inspect(corpus)
# Remove punctionation and convert to lowercase
corpus <- tm_map(corpus, stripWhitespace)
corpus <- tm_map(corpus,content_transformer(tolower))
corpus <- tm_map(corpus, removeWords, append(stopwords("english"),c("just", "like", "get")) )
corpus <- tm_map(corpus,removePunctuation)

# corpusBackup <- corpus
# # Remove stems
# corpus <- tm_map(corpus,stemDocument)
# # Restem to normalize words
# corpus <- tm_map(corpus,stemCompletion, dictionary=corpusBackup)


documentMatrix <- TermDocumentMatrix(corpus, control = list(minWordLength = 1))
#inspect(documentMatrix)

commonWords <- removeSparseTerms(x=documentMatrix, sparse=0.995)
colorfunc <- colorRampPalette(c("#345290","#7f8182","#a7a9ac","#86c1ea"))

m <- as.matrix(commonWords)
v <- sort(rowSums(m), decreasing=T)
documentNames <- names(v)
d <- data.frame(word=documentNames, freq=v)
wordcloud(d$word, d$freq, min.freq=1, col=colorfunc(length(d$word)),
          ordered.colors=T,scale=c(5,0.75))




data <- read.csv("allposts_fixed.csv",header=F)
names(data) <- c("ID","string","score")
rows <- which(data$score == 0)
data <- data[sample(rows,10000),]
corpus <- VCorpus(VectorSource(data$string))
# Remove punctionation and convert to lowercase
corpus <- tm_map(corpus, stripWhitespace)
corpus <- tm_map(corpus,content_transformer(tolower))
corpus <- tm_map(corpus,removePunctuation)
corpus <- tm_map(corpus, removeWords, stopwords("english"))
documentMatrix <- TermDocumentMatrix(corpus, control = list(minWordLength = 1))
commonWords <- removeSparseTerms(x=documentMatrix, sparse=0.995)
colorfunc <- colorRampPalette(c("#345290","#7f8182","#a7a9ac","#86c1ea"))

m <- as.matrix(commonWords)
v <- sort(rowSums(m), decreasing=T)
documentNames <- names(v)
d <- data.frame(word=documentNames, freq=v)
wordcloud(d$word, d$freq, min.freq=1, col=colorfunc(length(d$word)),
          ordered.colors=T,scale=c(5,0.75))

