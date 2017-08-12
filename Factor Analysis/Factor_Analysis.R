#######Factor Analysis#########


##Loading the data

#setwd("C:/Users/nitis/Desktop")

      install.packages("foreign")
      library(foreign)
      
      saq = read.csv("Fac_an.csv")
      
      odds = seq(1,45,by=2)
      
      saq = saq[,odds]
      
      colnames(saq) <- as.character(unlist(saq[1,]))
      
      saq = saq[-1, ]
      
      saq[] <- lapply(saq, function(x) if(is.factor(x)) factor(x) else x)
      

##Coverting into numeric (If neccesary)
indx <- sapply(saq, is.factor)
      
saq[indx] <- sapply(saq[indx], function(x) as.numeric(as.character(x)))

##Initial analysis

install.packages("psych")
library(psych)
cor.plot(saq,numbers=TRUE,main="Correlations")
cor.plot(saq[,1:10],numbers=TRUE,main="Correlations")

##Determining number of factors from nfactor library (Numeric values required)

install.packages("nFactors")
library(nFactors)
ev <- eigen(cor(saq)) # get eigenvalues
ap <- parallel(subject=nrow(saq),var=ncol(saq),
               rep=100,cent=.05)
nS <- nScree(x=ev$values, aparallel=ap$eigen$qevpea)
plotnScree(nS)

##From scree plot we see solutions from four different methods. We already know that we have only one factor explaining the fear of SPSS (higher value representing fear). Acceleration Factor gives us the number of factors required as 1.

install.packages("FactoMineR")
library(FactoMineR)

result <- PCA(saq)

##Factor analysis with psych

library(psych)

wls = fa(saq,nfactors=1,n.obs = 2571,fm="wls") # wieghted least squares

print(wls,cut=0,digits=3)

pa = fa(saq,nfactors=1,n.obs = 2571,fm="pa") # principal factor solution

print(pa,cut=0,digits=3)

ml = fa(saq,nfactors=1,n.obs = 2571,fm="ml") # Maximum likelyhood solution

print(ml,cut=0,digits=3)

fa.diagram(pa)

fa.diagram(ml)

fa.diagram(wls)

##From the above result "Test of the hypothesis that 1 factor is sufficient", it is confirmed that we can successfully interpret the data through a single factor, let's name it "Anxiety of SPSS".

##Let us also try four factors

wls = fa(saq,nfactors=4,n.obs = 2571,fm="wls") # wieghted least squares

print(wls,cut=0,digits=3)

pa = fa(saq,nfactors=4,n.obs = 2571,fm="pa") # principal factor solution

print(pa,cut=0,digits=3)

ml = fa(saq,nfactors=4,n.obs = 2571,fm="ml") # Maximum likelyhood solution

print(ml,cut=0,digits=3)

fa.diagram(pa)

fa.diagram(ml)

fa.diagram(wls)
