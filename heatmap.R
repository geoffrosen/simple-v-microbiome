#!/usr/bin/Rscript --default-packages=vegan,methods,RColorBrewer,gplots,utils,stats,grDevices,graphics,argparse,proto

# This script will be used to make heatmaps
# It is based on: http://www.molecularecologist.com/2013/08/making-heatmaps-with-r-for-microbiome-analysis/

get.file.and.output.heatmap <- function(input_file, output_folder, column_name, xlab, minimum_abundances) {

  transposed.dataset <- read.delim(input_file)

  transposed.dataset <- transposed.dataset[order(transposed.dataset[,column_name]),]

  col.status <- as.matrix(transposed.dataset[,column_name])
  data.prop <- transposed.dataset[, -c(1,2)]
  row.names(data.prop) <- transposed.dataset[,1]

  max.abundance <- apply(data.prop, 2, max)

  colorSet <- rep(c("red","yellow","purple","blue","orange","green"),10)
  
  label.variable <- col.status
  
  labels.colors <- matrix()
  
  labels.names <- matrix()
  
  i = 0
  
  for (lev in levels(as.factor(col.status))) {
    i = i + 1
	if (i == 1) {
	  labels.colors <- colorSet[i]
	  labels.names <- lev
	}
	else {
	  labels.colors <- c(labels.colors, colorSet[i])
	  labels.names <- c(labels.names, lev)
	}
	label.variable <- replace(label.variable, which(label.variable == lev), colorSet[i])
  }
  # Thanks: http://r.789695.n4.nabble.com/Extracting-File-Basename-without-Extension-td878817.html
  base.filename <- paste(output_folder,"/",sub("^([^.]*).*", "\\1", input_file),"_",column_name,sep="")
  
  for (i in 1:length(minimum_abundances)) {
    lev <- minimum_abundances[i]
    d <- get.necessary.data(data.prop, lev, max.abundance)
	fp <- paste(base.filename,"_",lev,".pdf",sep="")
	write.pdf(fp, d, label.variable, labels.names, labels.colors, xlab, lev, column_name)
  }
}

write.pdf <- function(file_path, data.prop, label.variable, labels.names, labels.colors, xlab, min_abundance_label, column_name) {

  lmat <- rbind( c(3,4), c(1,2), c(0,5) )
  lhei <- c(.75, 4.5, .75)
  lwid <- c(.1, 4)
  
  colorPalate <- colorRampPalette(c("white","green","green4","violet","purple"))(100)
  
  pdf(file=file_path, paper="USr", height=8, width=10.5)
  
  title_this <- paste("Heatmap by", column_name, "for", xlab, "with\nmaximum abundance of at least", min_abundance_label)
  
  heatmap.2(as.matrix(data.prop),
		col=colorPalate, 
		Rowv=NA, dendrogram='none', 
		RowSideColors=label.variable, trace="none", 
		density.info="none",  
		ylab="Sample", main=title_this,
		key.xlab="Color Key",
		lmat=lmat, lhei=lhei, lwid=lwid,
		key.par=list(mgp=c(0, 0.5, 0), mar=c(1.5, .75, 3, 3.0)), 
		margins=c(7,5),
		srtCol=70, xlab=xlab,
		keysize = 0.5, key.title=""
		)
  legend(x=.82,y=.85, legend=labels.names, fill=labels.colors,bty="n", xjust=0,yjust=0,ncol=1)
  
  dev.off()

}

get.necessary.data <- function(data.prop, level, max.abundance) {
  n <- names(which(max.abundance < as.double(level)))
  data.prop.this <- data.prop[, -which(names(data.prop) %in% n)]
  return(data.prop.this)
}

parser <- ArgumentParser()

parser$add_argument("-i", "--input-files", help="Input files to use to make heatmaps (comma separated)", required=TRUE)
parser$add_argument("-o", "--output-folder", help="Output folder to place heatmaps in", required=TRUE)
parser$add_argument("-c", "--column-name", help="Column to use for class", required=TRUE)
parser$add_argument("-x", "--xlab", help="X label", required=TRUE)
parser$add_argument("-m", "--minimum-abundances", help="Minimum abundances as fraction. (comma separated)", required=TRUE)

my.args <- parser$parse_args()

my.args$minimum_abundances <- unlist(strsplit(my.args$minimum_abundances,","))
my.args$input_files <- unlist(strsplit(my.args$input_files,","))

for (i in my.args$input_files) {
  get.file.and.output.heatmap(i, my.args$output_folder, my.args$column_name, my.args$xlab, my.args$minimum_abundances)

}
