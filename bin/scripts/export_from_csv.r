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
  
  failed_warning <- function(filename,request_id,message) {
    warning(paste(
      filename,": download with request id",request_id,"failed:",message
    ))
  }
  
  if(!dir.exists(out_dir)) {
    dir.create(out_dir)
  }
  
  # This section creates a queue of files that need to be downloaded.
  # It starts as the filename column from the csv,
  
  data <- fread(
    file=csv_file,
    header=TRUE,
    sep=";",
    select=c("experiment_id","filename","format","technique","genome")
  )
  
  # but the script checks whether there are files that have already been
  # downloaded in the output folder. Is this the case, then they are
  # subtracted from the queue.
  
  all_files <- dir(path=out_dir)
  meta_files <- dir(path=out_dir, pattern="meta.txt")
  downloaded_files <- all_files[!all_files %in% meta_files]
  downloaded_files <- gsub(".txt","",downloaded_files)
  
  queued_files <- data[!data$filename %in% downloaded_files]
  
  if(nrow(queued_files) > 0) {
    
    # get chrom sizes for all genomes in the CSV
    genomes <- unique(queued_files$genome)
    chrom_sizes <- vector("list")
    for(genome in genomes) {
      chroms <- deepblue_chromosomes(genome)
      chroms$id <- tolower(chroms$id)
      chrom_sizes[[genome]] <- chroms
    }
    
    failed_rows <- queued_files
    
    for(i in 1:nrow(queued_files)) {
      
      row <- queued_files[i,]
      filename <- row$filename
      chr <- sub(".*\\.(chr.*?)(\\..*|$)","\\1",filename)
      id <- row$experiment_id
      
      if(row$technique == "chip-seq") {
        message(filename)
        
        query_id <- deepblue_select_experiments(experiment_name = id, chromosome = chr)
        message(paste("query id:",query_id))
        
        request_id <- deepblue_get_regions(query_id = query_id, output_format = row$format) # output_format required
        message(paste("request id:",request_id))
        
        req_status <- deepblue_info(request_id)$state
        
        if(req_status == "done") {
          
          # NEW: download data as character vector
          regions <- try(deepblue_download_request_data(request_id))
          
          if(class(regions) != "GRanges") {
            
            if(class(regions) == "try-error") {
              
              err_msg <- regions[1]
              
            } else {
              
              err_msg <- paste("received",class(regions),"class object when calling deepblue_download_request_data")
              
            }
            
            failed_warning(filename,request_id,err_msg)
            
          } else {
            
            output_length <- length(regions)
            output_file <- paste(out_dir,"/",filename,".txt",sep="")
            
            if(output_length > 0) {
              
              message(paste("regions:",output_length))
              
              deepblue_export_tab(regions,target.directory = out_dir,file.name = filename)
              
              if(file.exists(output_file)) {
                
                deepblue_export_meta_data(id,target.directory = out_dir,file.name = filename)
                failed_rows[i,] <- NA
                
              } else {
                
                err_msg <- paste("file was downloaded but not exported. data had length",output_length)
                failed_warning(filename,request_id,err_msg)
                
              }
              
            } else {
              
              failed_warning(filename,request_id,"returned empty file")
              
            }
            
          }
          
        } else {
          
          failed_warning(filename,request_id,paste("request status was:",req_status))
          
        }
        
      } else {
        
        no_errors <- TRUE
        genom <- row$genome
        this_chrom_size <- chrom_sizes[[genom]][chrom_sizes[[genom]]$id == chr]$name
        chunks <- seq(1,this_chrom_size,by=chunk_size)
        
        for(chunk in chunks) {
          
          output_length <- 0
          
          chunked_filename <- paste(filename,"chunk",chunk,sep="_")
          message(chunked_filename)
          
          query_id <- deepblue_select_experiments(experiment_name = id, chromosome = chr, start = chunk, end = chunk + chunk_size)
          message(paste("query id:",query_id))
          
          filtered_query_id <- deepblue_filter_regions(query_id = query_id, field = "VALUE", operation = ">", value = "0", type = "number")
          message(paste("filtered query id:",filtered_query_id))
          
          request_id <- deepblue_get_regions(query_id = filtered_query_id, output_format = row$format)
          message(paste("request id:",request_id))
          
          req_status <- deepblue_info(request_id)$state
          
          if(req_status == "done") {
            
            regions <- try(deepblue_download_request_data(request_id))
            
            if(class(regions) != "GRanges") {
              
              no_errors <- FALSE
              
              if(class(regions) == "try-error") {
                
                err_msg <- regions[1]
                
              } else {
                
                err_msg <- paste("received",class(regions),"class object when calling deepblue_download_request_data")
                
              }
              
              failed_warning(chunked_filename,request_id,err_msg)
              
            } else {
              
              output_length <- length(regions)
              
              if(output_length > 0) {
                
                message(paste("regions:",output_length))
                output_file <- paste(out_dir,"/",chunked_filename,".txt",sep="")
                
                deepblue_export_tab(regions,target.directory = out_dir,file.name = chunked_filename)
                
                if(!file.exists(output_file)) {
                  
                  no_errors <- FALSE
                  err_msg <- paste("file was downloaded but not exported. data had length",output_length)
                  failed_warning(chunked_filename,request_id,err_msg)
                  
                }
                
              } else {
                
                failed_warning(chunked_filename,request_id,"returned empty file")
                
              }
              
            }
            
          } else {
            
            no_errors <- FALSE
            failed_warning(chunked_filename,request_id,paste("request status was:",req_status))
            
          }
          
        }
        
        if(no_errors) {
          failed_rows[i,] <- NA
          deepblue_export_meta_data(id,target.directory=out_dir,file.name=filename)
        }
        
      }
      
    }
    
    failed_files <- failed_rows[!is.na(failed_rows$filename)]$filename
    n_failed <- length(failed_files)
    
    if(n_failed > 0) {
      
      warning(paste(n_failed,"file(s) could not be downloaded:",paste(failed_files,collapse=", ")))
      
    }
    
    message(paste(nrow(queued_files)-n_failed,"file(s) downloaded to",normalizePath(out_dir)))
    
  } else {
    
    stop("No new files to download.")
    
  }
  
}

export_from_csv(args$input,args$output,as.integer(args$chunks))
