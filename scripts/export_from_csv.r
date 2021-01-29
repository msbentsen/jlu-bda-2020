#!/usr/bin/env Rscript
if(!"DeepBlueR" %in% installed.packages()) {
  install.packages("BiocManager")
  BiocManager::install("DeepBlueR")
}
library(DeepBlueR)

exportFromCsv <- function(csv_file) {
  
  out_dir <- "csv_exported"

  # How this works: For each experiment and each chromosome, download all regions as a tab-separated text file.
  # The hg19 and Grch38 genomes contain more than 24 chromosomes, but we only use the common ones.
  
  # chrom_in_filename
  # arguments: filename -> the deepblue filename, chrom -> the current chromosome no. ("chr1")
  # returns:   filename string where the chromosome no. is inserted at the end but before the file extension (if one is available)
  
  chrom_in_filename <- function(filename,chrom) {
    output <- matrix(data=NA,nrow=length(filename),ncol=length(chrom))
    for(i in 1:length(filename)) {
      for(j in 1:length(chrom)) {
        dots <- strsplit(filename[i],".",fixed=TRUE)[[1]]
        mylen <- length(dots)
        if(mylen > 1) {
          tmp <- dots[mylen]
          dots[mylen] = chrom[j]
          dots[mylen+1] = tmp
          output[i,j] = paste(dots,collapse=".")
        } else {
          output[i,j] = paste(filename[i],chrom[j],sep=".")
        }
      }
    }
    return(as.vector(t(output)))
  }
  
  if(!dir.exists(out_dir)) {
    dir.create(out_dir)
  }
  
  # This section creates a queue of files that need to be downloaded.
  # It starts as the filename column from the csv,
  
  chrs <- paste("chr",c(1:22,"X","Y"),sep="")
  data <- read.csv(file=csv_file,header=TRUE)
  all_csv_files <- chrom_in_filename(data$filename,chrs)
  
  # but the script checks whether there are files that have already been
  # downloaded in the output folder. Is this the case, then they are
  # subtracted from the queue.
  
  all_files <- dir(path=out_dir,pattern=".txt")
  meta_files <- dir(path=out_dir,pattern="meta.txt")
  downloaded_files <- all_files[!downloaded_files %in% meta_files]
  downloaded_files <- gsub(".txt","",downloaded_files)
  
  queued_files <- all_csv_files[!all_csv_files %in% downloaded_files]
  
  for(row in 1:nrow(data)) {
    e = data[row,]
    name = e$filename
    for(c in chrs) {
      filename = chrom_in_filename(name,c)
      if(filename %in% queued_files) {
        print(filename)
        id = e$experiment_id
        format = e$format
        query_id = deepblue_select_experiments(experiment_name = name, chromosome = c)
        request_id = deepblue_get_regions(query_id = query_id, output_format = format) # output_format required
        regions = try(deepblue_download_request_data(request_id),silent=TRUE) # ignore errors when no regions found for this chromosome (this is not unusual)
        if(class(regions)=="GRanges") {
          deepblue_export_tab(regions,target.directory=out_dir,file.name=filename)
          deepblue_export_meta_data(id,target.directory=out_dir,file.name=filename)
        }
        if(file.exists(paste(out_dir,"/",filename,".txt",sep=""))) {
          queued_files <- setdiff(queued_files,filename)
        }
      }
    }
  }
}

exportFromCsv("linking_table.csv")
