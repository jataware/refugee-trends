library(timetk) 
library(tidyquant)
library(corrplot)
library(Hmisc)
library(tidyr)
library(dplyr)
library(scales)

options(scipen=999)

############################# Preprocessing  ############################# 
args <- commandArgs(trailingOnly = TRUE)

if (length(args)>0) {
  fname = args[1]
} else {
  fname = "Migration_GTrends.csv"
}

#import data
cat("Reading in file: ", fname)
dat <- read.csv(fname, header = TRUE, sep = ",", na.strings = "")

#replace NA's 
dat$EthiopiaArrivals <- ifelse(is.na(dat$EthiopiaArrivals), mean(dat$EthiopiaArrivals, na.rm=TRUE), dat$EthiopiaArrivals)

#Convert dates to as.Date format
dat$date = as.Date(dat$date, format = "%Y-%m-%d")
date <- dat$date

#Rescale the Arrival data to reduce variance.
dat$EthiopiaArrivals <- rescale((dat$EthiopiaArrivals), to = c(0, 100))

#Make df numeric
dat <- data.frame(lapply(dat[,-1], function(x) as.numeric(as.character(x))))


############################# Variable elimination ############################# 

# We will keep only the searched terms that correlated with arrival dates in Ethiopia.

Ethiopia.cor <- round(cor(dat),3)[,1]

hist(Ethiopia.cor,main="Google Searches vs. Ethiopia Arrivals", 
     xlab="Pearson Value")

y<-Ethiopia.cor[Ethiopia.cor> 0.2]
y.labels<- as.character(names(y))
data<- dat %>% dplyr::select(one_of(y.labels))


############################# Split the data ############################# 

#take a random sample of size 70% from a dataset dat 
set.seed(123)
index <- sample(1:nrow(data),size = 0.7*nrow(data))
train <- data[index,]
test <- data[-index,]
nrow(train)
nrow(test)

#plot the splited data
group <- rep(NA,40)
group <- ifelse(seq(1,40) %in% index,"Train","Test")
df <- data.frame(date=date,Arrivals=dat$EthiopiaArrivals)



#Plot test and train data
ggplot(df,aes(x = date,y = Arrivals, color = group)) + geom_point() +
  scale_color_discrete(name="") + theme(legend.position="top")


############################# MODEL1: Baseline ############################# 

# Baseline models and calculate the RMSE and MAE for  continuous outcome variable
best.guess <- mean(train$EthiopiaArrivals) 
RMSE.baseline <- sqrt(mean((best.guess-test$EthiopiaArrivals)^2))
RMSE.baseline
MAE.baseline <- mean(abs(best.guess-test$EthiopiaArrivals))
MAE.baseline

############################# MODEL2: Multiple (log)linear regression ############################# 

lin.reg <- lm(log(EthiopiaArrivals+1) ~., data = train)
summary(lin.reg)
test.pred.lin <- exp(predict(lin.reg,test))-1
RMSE.lin.reg <- sqrt(mean((test.pred.lin-test$EthiopiaArrivals)^2))
MAE.lin.reg <- mean(abs(test.pred.lin-test$EthiopiaArrivals))
RMSE.lin.reg
MAE.lin.reg


############################# MODEL3: Decision trees model ############################# 

# Create Decision trees model

library(rpart)
library(rpart.plot)

rt <- rpart(EthiopiaArrivals ~ ., data = train)
test.pred.rtree <- predict(rt,test)
RMSE.rtree <- sqrt(mean((test.pred.rtree-test$EthiopiaArrivals)^2))
MAE.rtree <- mean(abs(test.pred.rtree-test$EthiopiaArrivals))

printcp(rt)
rpart.plot(rt)

############################# MODEL4: Prune tree ############################# 
#Prune tree
min.xerror <- rt$cptable[which.min(rt$cptable[,"xerror"]),"CP"]
rt.pruned <- prune(rt,cp = min.xerror)
test.pred.rtree.p <- predict(rt.pruned,test)
RMSE.rtree.pruned <- sqrt(mean((test.pred.rtree.p-test$EthiopiaArrivals)^2))
MAE.rtree.pruned <- mean(abs(test.pred.rtree.p-test$EthiopiaArrivals))

rpart.plot(rt.pruned)

############################# MODEL5: Random Forest ############################# 
#Random Forest
#install.packages("randomForest")
library(randomForest)

set.seed(222)

rf <- randomForest(EthiopiaArrivals ~ ., data = train, importance = TRUE, ntree=655)
#number of trees
which.min(rf$mse)

imp <- as.data.frame(sort(importance(rf)[,1],decreasing = TRUE),optional = T)
names(imp) <- "% Inc MSE"
imp

#Variable importance Plot
varImpPlot(rf,type=1,cex=0.8)

test.pred.forest <- predict(rf,test)
RMSE.forest <- sqrt(mean((test.pred.forest-test$EthiopiaArrivals)^2))
MAE.forest <- mean(abs(test.pred.forest-test$EthiopiaArrivals))
RMSE.forest
MAE.forest

############## MODEL6: SVM ########
library(e1071)

svm <- svm(EthiopiaArrivals ~., data = train)
summary(svm)
test.pred.svm <- predict(svm,test)


RMSE.svm <- sqrt(mean((test.pred.svm-test$EthiopiaArrivals)^2))
MAE.svm <- mean(abs(test.pred.svm-test$EthiopiaArrivals))
RMSE.svm
MAE.svm

############################# PLOT ALL ############################# 
#The code draws from: https://www.r-bloggers.com/part-4a-modelling-predicting-the-amount-of-rain/

accuracy <- data.frame(Method = c("Baseline","Linear Regression","Full tree","Pruned tree","Random forest","SVM"),
                       RMSE   = c(RMSE.baseline,RMSE.lin.reg,RMSE.rtree,RMSE.rtree.pruned,RMSE.forest,RMSE.svm),
                       MAE    = c(MAE.baseline,MAE.lin.reg,MAE.rtree,MAE.rtree.pruned,MAE.forest,MAE.svm))

accuracy$RMSE <- round(accuracy$RMSE,2)
accuracy$MAE <- round(accuracy$MAE,2) 

cat("\n\n\nFile: ", fname)
cat("\n########### RESULTS ###########\n")
accuracy
cat("###############################\n\n")
write.csv(accuracy,'accuracy.csv')

all.predictions <- data.frame(actual = test$EthiopiaArrivals,
                              baseline = best.guess,
                              linear.regression = test.pred.lin,
                              full.tree = test.pred.rtree,
                              pruned.tree = test.pred.rtree.p,
                              random.forest = test.pred.forest,
                              svm = test.pred.svm)

# head(all.predictions) 


library(tidyr)
all.predictions <- gather(all.predictions,key = model,value = predictions, 2:7)
# head(all.predictions)
# tail (all.predictions)

ggplot(data = all.predictions,aes(x = actual, y = predictions)) + 
  geom_point(colour = "blue") + 
  geom_abline(intercept = 0, slope = 1, colour = "red") +
  geom_vline(xintercept = 3, colour = "green", linetype = "dashed") +
  facet_wrap(~ model,ncol = 2) + 
  coord_cartesian(xlim = c(0,70),ylim = c(0,70)) +
  ggtitle("Predicted vs. Actual, by model")

