odds.ratio <- function( two_by_two ) {
  this <- environment()
  this$table <- two_by_two
  this$fisher <- fisher.test(two_by_two)
  a <- two_by_two[1,1]
  b <- two_by_two[1,2]
  c <- two_by_two[2,1]
  d <- two_by_two[2,2]
  this$Sensitivity <- (a)/(a + c)
  this$Specificity <- (d)/(d + b)
  this$OR <- (a * d)/(b * c)
  siglog <- sqrt( ( 1/a ) + ( 1/b ) + ( 1/c )  + ( 1/d ) )
  zalph <- qnorm( 0.975 )
  logOR <- log( OR )
  loglo <- logOR - zalph * siglog
  loghi <- logOR + zalph * siglog
  this$OR_low <- exp( loglo )
  this$OR_high <- exp( loghi )
  df.two_by_two <- as.data.frame( two_by_two )
  exposure.pos <- paste( colnames( df.two_by_two )[1], as.character( df.two_by_two[1,1] ) )
  exposure.neg <- paste( colnames( df.two_by_two )[1], as.character( df.two_by_two[2,1] ) )
  outcome <- paste( colnames( df.two_by_two )[2], as.character( df.two_by_two[1,2] ) )
  stmt1 <- 'The odds of'
  stmt2 <- outcome
  stmt3 <- 'is'
  stmt4 <- paste(this$OR, '(', this$OR_low, '-', this$OR_high, ')')
  stmt5 <- 'given'
  stmt6 <- exposure.pos
  stmt7 <- 'compared to'
  stmt8 <- exposure.neg
  stmt8.5 <- paste('(Fisher\'s test p-value:', this$fisher$p.value, ')')
  stmt9 <- '. the sensitivity and specificity are'
  stmt10 <- this$Sensitivity
  stmt10.5 <- 'and'
  stmt11 <- this$Specificity
  stmt12 <- 'respectively for'
  stmt13 <- exposure.pos
  stmt14 <- 'on'
  stmt15 <- outcome
  this$Statement <- paste( stmt1, stmt2, stmt3, stmt4, stmt5, stmt6, stmt7, stmt8, stmt8.5, stmt9, stmt10, stmt10.5, stmt11, stmt12, stmt13, stmt14, stmt15)
  return(this)
  
}

runner <- function(data, possible_vars, constant_var) {
  for (i in attributes(d.split)$names) {
    for (poss_var in possible_vars) {
      tab <- table(data[[i]][,poss_var],data[[i]][,constant_var])
      ft <- fisher.test(tab)
      o <- odds.ratio(tab)
      writeLines(c('Table for',i,'Looking at', poss_var))
      print(tab)
      writeLines(c('Fisher test p-value:',ft$p.value))
      writeLines(c('Odds ratio:', o$this$Statement))
    }
  }
  
}


guess_status <- function(guess_col, cutoff = 0.0000001) {
  ver <- as.numeric(as.character(guess_col))
  ver[which(ver > cutoff)] <- 1
  ver[which(ver <= cutoff)] <- 0
  ver <- as.character(ver)
  ver[which(ver == "1")] <- "pos"
  ver[which(ver == "0")] <- "neg"
  return(as.factor(ver))
  
}

double_positive <- function(col1, col2) {
  t <- cbind.data.frame(col1, col2)
  ot <- rep("neg",length(col1))
  ot[which(t[,1] == "pos" & t[,2] == "pos")] <- "pos"
  return(as.factor(ot))
}

pick_dominant_add_total <- function(df, cutoff = 0.5) {
  for (i in 1:length(colnames(df))) {
    df[,i] <- as.numeric(as.character(df[,i]))
  }
  row.totals <- rowSums(df)
  max.abund <- c()
  max.abund.name <- c()
  doms <- c()
  for (i in 1:length(df[,1])) {
    thisrow <- df[i,]
    thismax <- max(thisrow)
    thismaxname <- colnames(thisrow[which(thisrow == thismax)])[1]
    max.abund <- c(max.abund, thismax)
    max.abund.name <- c(max.abund.name, thismaxname)
    thisprop <- thismax/row.totals[i]
    if (thisprop >= cutoff) {
      doms <- c(doms, thismaxname)
    }
    else {
      doms <- c(doms, 'None')
    }
    
  }
  df$total_seqs <- row.totals
  df$max_abund <- max.abund
  df$max_abund_name <- max.abund.name
  df$dominant <- as.factor(doms)
  return(df)
  
  
}