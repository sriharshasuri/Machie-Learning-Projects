
# Load the required liraries
library(readr)
library(dplyr)
library(tidyr)
library(arules)
library(arulesViz)
library(methods)


# Load orders and products datasets
ordr_pr <- read_csv("order_products__prior.csv")
prods <- read_csv("products.csv")

# Join datasets and summarise all the products for each order
order_baskets <- ordr_pr %>% inner_join(prods, by="product_id") %>% 
                             group_by(order_id) %>%
                             summarise(basket = as.vector(list(product_name)))

# Form transactions database from the above dataset
transactions <- as(order_baskets$basket, "transactions")


# Histogram of number of items per order
hist(size(transactions), breaks = 0:150, xaxt="n", ylim=c(0,250000), 
     main = "Number of Items per basket", xlab = "#Items")
axis(1, at=seq(0,160,by=10), cex.axis=0.8)
mtext(paste("Total:", length(transactions), "baskets,"))


# Frequent items with minimum support of 0.02
item_frequencies <- itemFrequency(transactions, type="a")
support <- 0.02
freq_items <- sort(item_frequencies, decreasing = F)
freq_items <- freq_items[freq_items>support*length(transactions)]


# Plot of frequent items
par(mar=c(2,10,2,2)); options(scipen=5)
barplot(freq_items, horiz=T, las=1, main="Frequent Items", cex.names=.8, 
        xlim=c(0,500000))
mtext(paste("support:",support), padj = .8)
abline(v=support*length(transactions), col="red")

# Frequent itemsets with minimum support of 0.008
support <- 0.008
itemsets <- apriori(transactions, parameter = list(target = "frequent itemsets", supp=support, minlen=2), control = list(verbose = FALSE))

# Plot of frequent itemsets
par(mar=c(5,18,2,2)+.1)
sets_order_supp <- DATAFRAME(sort(itemsets, by="support", decreasing = F))
barplot(sets_order_supp$support, names.arg=sets_order_supp$items, xlim=c(0,0.02), horiz = T, las = 2, cex.names = .8, main = "Frequent Itemsets")
mtext(paste("support:",support), padj = .8)




# Prominent association rules using apriori algorithm
rules1 <- apriori(transactions, parameter = list(supp = 0.00001, conf = 0.6, maxlen=3), control = list(verbose = FALSE)) 


summary(quality(rules1))

plot(rules1)

inspect(sort(rules1, by="lift")[1:10])
inspect(sort(rules1, by="confidence")[1:10])






