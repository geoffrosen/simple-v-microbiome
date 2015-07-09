#!/usr/bin/Rscript --default-packages=methods,utils,graphics,argparse,Boruta,caret,pROC,grDevices,e1071

# This script will be used to do the following:
# 1. Select features with Boruta
# 2. Train a random forest classifier
# 3. Test and tune the random forest classifier
# 4. Output information about the classifier
# 5. Use the classifier on a novel set and output assignments

# Help from: http://stats.stackexchange.com/questions/141462/different-results-from-randomforest-via-caret-and-the-basic-randomforest-package

get.file.and.predict <- function(input_file, output_folder, positive_val, negative_val, classifier, threshold, boruta_ref, mapper) {

rare_guess <- read.delim(input_file, row.names=1)

for (fact in getSelectedAttributes(boruta_ref)) {
if (!is.element(fact, colnames(rare_guess))) {
rare_guess[[fact]] <- rep(0.0, nrow(rare_guess))
}
}

rare_guess <- rare_guess[, getSelectedAttributes(boruta_ref)]

pred_guess <- predict(classifier, rare_guess, type = "prob")

n <- input_file

write.csv(pred_guess, paste(output_folder, '/', basename(n), '_','probabilities.csv', sep=''))

pred_guess <- factor( ifelse(pred_guess[, positive_val] > threshold, positive_val, negative_val))

res_table <- cbind(row.names(rare_guess), as.matrix(pred_guess))

cname <- paste('predicted',class_var,n,sep="_")

colnames(res_table) <- c('SRS_SampleID', cname)

res_table <- merge(res_table, mapper, by='SRS_SampleID', all.x=TRUE, all.y=FALSE)

res_table <- res_table[,c('PSN', 'SRS_SampleID', cname)]

res_table <- res_table[-which(is.na(res_table$PSN)),]

write.csv(res_table, paste(output_folder,'/', basename(n), '_', 'calls.csv', sep=''), row.names=FALSE)

return(res_table[,c('PSN', cname)])

}


parser <- ArgumentParser()

parser$add_argument("-r", "--reference-fp", help="The reference file (should be rarefied, transposed, and put through qiimeToMaaslin)", required=TRUE)
parser$add_argument("-o", "--output-folder", help="Output folder to place base outputs in (specific outputs will be placed in same folder as original file)", required=TRUE)
parser$add_argument("-c", "--class-variable", help="The name of the class we will be guessing", required=TRUE)
parser$add_argument("-t", "--training-proportion", help="proportion (between zero and one) to use for training", required=TRUE)
parser$add_argument("-s", "--seed", help="Seed number (to allow for reproducibility). Integer.", required=TRUE)
parser$add_argument("-p", "--positive-val", help="What the positive value is for the class variable", required=TRUE)
parser$add_argument("-n", "--negative-val", help="What the negative value is for the class variable", required=TRUE)
parser$add_argument("-i", "--input-files", help="Input files (comma separated)", required=TRUE)
parser$add_argument("-m", "--mapping-file", help="Mapping file", required=TRUE)

my.args <- parser$parse_args()

input_files <- unlist(strsplit(my.args$input_files,","))

if (length(input_files) == 0) {
stop('No input files found. Make sure you are inputting a string featuring a comma separated list')
}

map_fp <- my.args$mapping_file

reference_file <- my.args$reference_fp

train_prop <- my.args$training_proportion

input_seed <- as.integer(my.args$seed)

class_var <- my.args$class_variable

positive_val <- my.args$positive_val

negative_val <- my.args$negative_val

output_folder <- my.args$output_folder

set.seed(as.numeric(input_seed))

mapper <- read.delim(map_fp)

rare_ref <- read.delim(reference_file, row.names=1)

formula_ref <- as.formula(paste(class_var, '~', '.'))

boruta_ref <- Boruta(formula_ref, data = rare_ref, maxRuns = 500)

write.csv(as.matrix(attStats(boruta_ref)), paste(output_folder, '/','Boruta_results.csv', sep = ""))

smp_size <- floor(as.numeric(train_prop) * nrow(rare_ref))

train_names <- sample(seq_len(nrow(rare_ref)), size = smp_size)

train_set <- rare_ref[train_names, c(class_var, getSelectedAttributes(boruta_ref))]

test_set <- rare_ref[-train_names, c(class_var, getSelectedAttributes(boruta_ref))]

cvCtrl <- trainControl(method = "repeatedcv", number = 20, repeats = 20, classProbs = TRUE, summaryFunction = twoClassSummary)

rfClassifier <- train(formula_ref, data = train_set, trControl = cvCtrl, method = "rf", metric = "ROC")

predROC <- predict(rfClassifier, test_set, type = "prob")

myROC <- pROC::roc(test_set[,class_var], as.vector(predROC[,2]))

pdf(file=paste(output_folder, "/", "ROC.pdf", sep = ""), paper="USr", height=8, width=10.5)

plot(myROC, print.thres = "best")

dev.off()

threshold = coords(myROC, x = "best", best.method = "closest.topleft")[[1]]

predTest <- factor( ifelse(predROC[, positive_val] > threshold, positive_val, negative_val) )

confusionMx <- confusionMatrix(predTest, test_set[, class_var], positive = positive_val)

write.csv(as.table(confusionMx), paste(output_folder, "/", "ConfusionMatrix.csv", sep = ""))

holder <- matrix()

colnames(holder) <- 'PSN'

for (inp in input_files) {
print(paste('now working on',inp))
holder <- merge(holder, get.file.and.predict(inp, dirname(inp), positive_val, negative_val, rfClassifier, threshold, boruta_ref, mapper), on="PSN", all=TRUE)
}

write.csv(holder, 'out.csv')

holder <- holder[!(is.na(holder$PSN)),]

any_positives <- ifelse(apply(holder, 1, function(x) is.element(TRUE, x[2:length(x)] == positive_val)), positive_val, negative_val)

any_negatives <- ifelse(apply(holder, 1, function(x) is.element(TRUE, x[2:length(x)] == negative_val)), negative_val, positive_val)

prop_pos <- apply(holder, 1, function(x) as.double(length(which(x[2:length(x)]==positive_val))) / as.double(length(which(!is.na(x[2:length(x)])))))

holder$any_positives <- any_positives

holder$any_negatives <- any_negatives

holder$prop_pos <- prop_pos

holder$fifty_pos <- ifelse(holder$prop_pos > 0.50, positive_val, negative_val)

write.csv(holder, paste(output_folder,'/','final_table.csv',sep=''), row.names = FALSE)