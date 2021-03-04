#!/usr/bin/env Rscript
required_packages <- c("BiocManager","data.table","argparse")
install.packages(setdiff(required_packages,rownames(installed.packages())),repos="http://cran.us.r-project.org")
if(!"DeepBlueR" %in% installed.packages()) BiocManager::install("DeepBlueR")
library(argparse)
library(data.table)

parser <- ArgumentParser()

parser$add_argument("-i", "--input", type="character", default="linking_table.csv",
                    help="Input CSV file name with extension [default: \"%(default)s\"]")
parser$add_argument("-o", "--output", type="character", default="csv_exported",
                    help="Output directory name [default: \"%(default)s\"]")
parser$add_argument("-c", "--chunks", type="integer", default=10000000L,
                    help="Chunk size for ATAC/DNAse data [default: %(default)s]")

args <- parser$parse_args()

library(DeepBlueR)

# export_from_csv()
# Requires csv filename and output directory (with default values)
# Downloads all files listed in the csv that do not exist in the output dir yet

export_from_csv <- function(csv_file,out_dir,chunk_size) {
<<<<<<< Updated upstream:bin/scripts/export_from_csv.r

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

=======
  
>>>>>>> Stashed changes:scripts/export_from_csv.r
  if(!dir.exists(out_dir)) {
    dir.create(out_dir)
  }

  # This section creates a queue of files that need to be downloaded.
  # It starts as the filename column from the csv,
<<<<<<< Updated upstream:bin/scripts/export_from_csv.r

  data <- fread(file=csv_file,header=TRUE,sep=",",select=c("experiment_id","filename","format","technique","genome"))
=======
  
  data <- fread(file=csv_file,header=TRUE,sep=";",select=c("experiment_id","filename","format","technique","genome"))
>>>>>>> Stashed changes:scripts/export_from_csv.r
  all_csv_files <- data$filename

  # but the script checks whether there are files that have already been
  # downloaded in the output folder. Is this the case, then they are
  # subtracted from the queue.

  all_files <- dir(path=out_dir,pattern=".txt")
  meta_files <- dir(path=out_dir,pattern="meta.txt")
  downloaded_files <- all_files[!all_files %in% meta_files]
  downloaded_files <- gsub(".txt","",downloaded_files)

  queued_files <- all_csv_files[!all_csv_files %in% downloaded_files]

  if(length(queued_files) > 0) {

    # get chrom sizes for all genomes in the CSV
    genomes <- unique(data$genome)
    chrom_sizes <- vector("list")
    for(genome in genomes) {
      chroms <- deepblue_chromosomes(genome)
      #chroms = chroms$id
      chrom_sizes[[genome]] <- chroms
    }

    while(length(queued_files) > 0) {
      # will loop forever if one or more files repeatedly cause errors
      for(i in 1:nrow(data)) {
        row <- data[i,]
        filename <- row$filename
        if(filename %in% queued_files) {
          message(filename)
          chr <- sub(".*\\.(chr.*?)(\\..*|$)","\\1",filename)
          id <- row$experiment_id
          if(row$technique == "chip-seq") {
            query_id <- deepblue_select_experiments(experiment_name = id, chromosome = chr)
            message(paste("query id:",query_id))
            request_id <- deepblue_get_regions(query_id = query_id, output_format = row$format) # output_format required
            message(paste("request id:",request_id))
            # download data from Deepblue server, decompress and import as GRanges object
            regions <- try(deepblue_download_request_data(request_id))
            if(class(regions)=="GRanges") {
              message(paste("regions:",length(regions)))
              deepblue_export_tab(regions,target.directory=out_dir,file.name=filename)
              if(file.exists(paste(out_dir,"/",filename,".txt",sep=""))) {
                deepblue_export_meta_data(id,target.directory=out_dir,file.name=filename)
                queued_files <<- setdiff(queued_files,filename)
              }
            } else {
              warning(paste(filename,": download with request id ",request_id," failed",sep=""))
            }
          } else {
            no_errors <- TRUE
            genom <- row$genome
            this_chrom_size <- chrom_sizes[[genom]][chrom_sizes[[genom]]$id == chr]$name
            chunks <- seq(1,this_chrom_size,by=chunk_size)
<<<<<<< Updated upstream:bin/scripts/export_from_csv.r
            requests <- vapply(chunks,function(chunk) {
              query_id <- deepblue_select_experiments(experiment_name = id, chromosome = chr, start = chunk, end = chunk + chunk_size)
              return(deepblue_get_regions(query_id = query_id, output_format = row[3]))
            })
            request_data = try(deepblue_batch_export_results(requests=requests,prefix=filename,suffix="",target.directory=out_dir,bed.format=FALSE))
            if(class(request_data) != "try-error") {
=======
            for(chunk in chunks) {
              query_id <- deepblue_select_experiments(experiment_name = id, chromosome = chr, start = chunk, end = chunk + chunk_size)
              message(paste("query id:",query_id))
              filtered_query_id <- deepblue_filter_regions(query_id = query_id, field = "VALUE", operation = ">", value = "0", type = "number")
              message(paste("filtered query id:",filtered_query_id))
              request_id <- deepblue_get_regions(query_id = filtered_query_id, output_format = row$format)
              message(paste("request id:",request_id))
              regions <- try(deepblue_download_request_data(request_id))
              if(class(regions)=="GRanges") {
                message(paste("regions:",length(regions)))
                deepblue_export_tab(regions,target.directory=out_dir,file.name=paste(filename,"chunk",chunk,sep="_"))
              } else {
                no_errors <- FALSE
                warning(paste(filename,": download with request id ",request_id," failed (chunk ",chunk,")",sep=""))
              }
            }
            if(no_errors) {
>>>>>>> Stashed changes:scripts/export_from_csv.r
              queued_files <<- setdiff(queued_files,filename)
            }
          }
        }
<<<<<<< Updated upstream:bin/scripts/export_from_csv.r
      })
    }
=======
      }
    }    
>>>>>>> Stashed changes:scripts/export_from_csv.r
  } else {
    stop("No new files to download.")
  }

}

export_from_csv(args$input,args$output,as.integer(args$chunks))
