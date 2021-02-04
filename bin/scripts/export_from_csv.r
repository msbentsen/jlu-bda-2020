#!/usr/bin/env Rscript
if(!"DeepBlueR" %in% installed.packages()) {
  install.packages("BiocManager")
  BiocManager::install("DeepBlueR")
}
library(DeepBlueR)

# export_from_csv()
# Requires csv filename and output directory (with default values)
# Downloads all files listed in the csv that do not exist in the output dir yet

export_from_csv <- function(csv_file="linking_table.csv",out_dir="csv_exported") {

  # extract_chromosome()
  # Expects a single filename string
  # Splits the string by periods and returns second-to-last substring for names with extensions, otherwise the last one
  # Example:
  # input:    filename="MS034301.CM.signal_reverse.chr14.bedgraph"
  # output:   "chr14"
    
  extract_chromosome <- function(filename) {
    mystr <- strsplit(filename,split=".",fixed=TRUE)[[1]]
    mylen <- length(mystr)
    if(mylen > 2) {
      return(mystr[mylen-1])
    } else if(mylen == 2) {
      return(mystr[mylen])
    } else {
      stop(paste("file",filename,"does not contain \".\" separator"))
    }
  }
  
  if(!dir.exists(out_dir)) {
    dir.create(out_dir)
  }
  
  # This section creates a queue of files that need to be downloaded.
  # It starts as the filename column from the csv,
  
  data <- fread(file=csv_file,header=TRUE,sep=",",select=c("experiment_id","filename","format"))
  all_csv_files <- data$filename
  
  # but the script checks whether there are files that have already been
  # downloaded in the output folder. Is this the case, then they are
  # subtracted from the queue.
  
  all_files <- dir(path=out_dir,pattern=".txt")
  meta_files <- dir(path=out_dir,pattern="meta.txt")
  downloaded_files <- all_files[!all_files %in% meta_files]
  downloaded_files <- gsub(".txt","",downloaded_files)
  
  queued_files <- all_csv_files[!all_csv_files %in% downloaded_files]
  
  apply(data[1:5],1,function(row) {
    filename <- row[2]
    if(filename %in% queued_files) {
      id = row[1]
      query_id = deepblue_select_experiments(experiment_name = id, chromosome = extract_chromosome(filename))
      request_id = deepblue_get_regions(query_id = query_id, output_format = row[3]) # output_format required
      regions = try(deepblue_download_request_data(request_id),silent=TRUE) # ignore errors when no regions found for this chromosome (this is not unusual)
      if(class(regions)=="GRanges") {
        deepblue_export_tab(regions,target.directory=out_dir,file.name=filename)
        deepblue_export_meta_data(id,target.directory=out_dir,file.name=filename)
      }
      if(file.exists(paste(out_dir,"/",filename,".txt",sep=""))) {
        queued_files <<- setdiff(queued_files,filename)
      }
    }
  })
}

export_from_csv()
