#!/usr/bin/env Rscript
required_packages <- c("BiocManager","data.table","argparse")
install.packages(setdiff(required_packages,rownames(installed.packages())),repos="http://cran.us.r-project.org")
if(!"DeepBlueR" %in% installed.packages()) BiocManager::install("DeepBlueR")
library(argparse)

chrs <- paste("chr",c(1:22,"X","Y"),sep="")

parser <- ArgumentParser()

parser$add_argument("-g", "--genomes", nargs="+", type="character", default=c("hg19","GRCh38"),
                    help="(List of) genomes to include [default: \"%(default)s\"]")
parser$add_argument("-c", "--chromosomes", nargs="+", type="character", default=chrs, choices=chrs,
                    help="(List of) chromosomes to include (requires chr prefix) [default: all]")
parser$add_argument("-b", "--biosources", nargs="+", type="character", default=NULL,
                    help="(List of) biosources to include [default: all] (Refer to: https://deepblue.mpi-inf.mpg.de/)")
parser$add_argument("-t", "--type", nargs="+", type="character", default="peaks", choices=c("peaks","signal"),
                    help="Experiment file types allowed for CHiP-Seq data [default: \"%(default)s\"]")
parser$add_argument("-a", "--atactype", nargs="+", type="character", default=c("peaks","signal"), choices=c("peaks","signal"),
                    help="Experiment file types allowed for ATAC/DNAse-Seq data [default: \"%(default)s\"]")
parser$add_argument("-m", "--marks", nargs="+", type="character", default=NULL,
                    help="(List of) epigenetic marks (i.e. transcription factors) to include [default: all] (Refer to: https://deepblue.mpi-inf.mpg.de/)")
parser$add_argument("-o", "--output", type="character", default="linking_table",
                    help="Output file name without extension [default: \"%(default)s\"]")

args <- parser$parse_args()

library(data.table)
library(DeepBlueR)

# create_linking_table()
# Takes optional arguments (see above)
# Creates a csv file built from specific Deepblue data

create_linking_table <- function(genomes,chrs,filter_biosources,chip_type,atac_type,chip_marks,outfile) {
  
  # chrom_in_filename()
  # Expects a vector of filenames (strings) and a vector of chromosomes (strings)
  # Returns a vector of filenames with the given chromosomes inserted at the end but (if available) before the last extension
  # Example:
  # input:    filenames=c("MS034301.CM.signal_reverse.bedgraph","ENCFF001VOQ"), chroms=c("chr4","chr5")
  # output:   "MS034301.CM.signal_reverse.chr4.bedgraph,"MS034301.CM.signal_reverse.chr5.bedgraph",
  #           "ENCFF001VOQ.chr4","ENCFF001VOQ.chr5"
  
  chrom_in_filename <- function(filenames,chroms) {
    output <- matrix(data=NA,nrow=length(filenames),ncol=length(chroms))
    for(i in 1:length(filenames)) {
      for(j in 1:length(chroms)) {
        dots <- strsplit(filenames[i],".",fixed=TRUE)[[1]]
        mylen <- length(dots)
        if(mylen > 1) {
          tmp <- dots[mylen]
          dots[mylen] = chroms[j]
          dots[mylen+1] = tmp
          output[i,j] = paste(dots,collapse=".")
        } else {
          output[i,j] = paste(filenames[i],chroms[j],sep=".")
        }
      }
    }
    return(as.vector(t(output)))
  }
  
  new_row <- function(metadata,filename) {
    print(filename)
    e <- metadata$`_id`
    # This function retrieves the metadata for a DeepBlue experiment and converts it into a data.table object
    sample_info <- metadata$sample_info
    extra <- metadata$extra_metadata
    meta <- data.table(
      experiment_id=e,
      genome=metadata$genome,
      biosource=metadata$sample_info$biosource_name,
      technique=tolower(metadata$technique),
      epigenetic_mark=metadata$epigenetic_mark,
      filename,
      data_type=metadata$data_type,
      format=metadata$format,
      sample_id=metadata$sample_id,
      project=metadata$project,
      total_size=metadata$upload_info$total_size,
      as.data.table(sample_info),
      as.data.table(extra)
    )
    return(meta)
  }
  
  all_genomes <- deepblue_list_genomes()$name
  genomes <- genomes[genomes %in% all_genomes]
  if(length(genomes) == 0) {
    stop(paste("No valid genomes provided by user. Available genomes:",paste(all_genomes,collapse=", ")))
  }
  
  if(!is.null(filter_biosources)) {
    # check whether biosources given by the user are valid
    all_biosources <- deepblue_list_biosources()$name
    removed_biosources <- filter_biosources[!filter_biosources %in% all_biosources]
    n_removed <- length(removed_biosources)
    if(n_removed>0) warning(paste("dropped",n_removed,"biosource(s):",paste(removed_biosources,collapse=", ")))
    filter_biosources <- filter_biosources[!filter_biosources %in% removed_biosources]
    if(length(filter_biosources)==0) {
      stop("No biosources given by user could be found in Deepblue database")
    }
    rm(all_biosources)
  }

  tf_marks <- deepblue_list_epigenetic_marks(extra_metadata = list(category="Transcription Factor Binding Sites"))$name
  
  if(!is.null(chip_marks)) {
    removed_marks <- chip_marks[!chip_marks %in% tf_marks]
    n_removed <- length(removed_marks)
    if(n_removed>0) warning(paste("dropped",n_removed,"tf(s):",paste(removed_marks,collapse=", ")))
    chip_marks <- chip_marks[!chip_marks %in% removed_marks]
    if(length(chip_marks)==0) {
      stop("No transcription factors given by user could be found in Deepblue database")
    }
  } else {
    chip_marks <- tf_marks
  }
  
  # ATAC-Seq: signals (mark: DNA Accessibility)
  # DNAse-Seq: signals and peaks (marks: DNA Accessibility, DNAseI)
  
  # 1st Step: Collect biosources for ATAC
  
  csv_data = NULL
  
  for(genome in genomes) {
    atac <- deepblue_list_experiments(genome=genome, technique="ATAC-Seq", biosource=filter_biosources, type=atac_type)
    dnase <- deepblue_list_experiments(genome=genome, technique="DNAse-Seq", biosource=filter_biosources, type=atac_type)
    # Deepblue returns "\n" if no data is matched, otherwise data.frames
    if(class(atac)[1] != "character") atac = atac$id else atac = NULL
    if(class(dnase)[1] != "character") dnase = dnase$id else dnase = NULL
    
    access_experiments <- c(atac,dnase)
    
    if(is.null(access_experiments)) {
      warning(paste(genome,"No ATAC-seq data available for given arguments",sep=": "))
    } else {
      atac_metadata <- lapply(access_experiments,function(x){ deepblue_info(x) })
      atac_biosources <- unique(sapply(atac_metadata,function(x) { x$sample_info$biosource_name }))
      
      # 2nd Step: Collect ChiP experiments and add to csv list if biosource has available ATAC data
      
      chips <- deepblue_list_experiments(genome=genome, technique="ChiP-Seq", biosource=atac_biosources, type=chip_type, epigenetic_mark=chip_marks)
      
      if(class(chips)[1] != "character") {
        
        chips = chips$id  
        chip_list <- lapply(chips,function(c) {
          metadata <- deepblue_info(c)
          return_list <- vector("list",length(chrs))
          filenames <- chrom_in_filename(metadata$name,chrs)
          return_list <- lapply(filenames,function(f) { new_row(metadata,f) })
          return(return_list)
        })
        
        # before: List of lists of data.tables
        chip_list <- unlist(chip_list[!is.na(chip_list)],recursive=FALSE)
        # after:  List of data.tables
        
        chip_biosources <- unique(sapply(chip_list,function(x){ x$biosource }))
        
        # 3rd Step: Add ATAC experiments to csv if biosource has available ChiP data
        
        atac_list <- lapply(atac_metadata,function(m) {
          if(m$sample_info$biosource_name %in% chip_biosources) {
            return_list <- vector("list",length(chrs))
            filenames <- chrom_in_filename(m$name,chrs)
            return_list <- lapply(filenames,function(f) { new_row(m,f) })
            return(return_list)
          } else {
            return(NA)
          }
        })
        atac_list <- unlist(atac_list[!is.na(atac_list)],recursive=FALSE)
        
        csv_data[[which(genomes==genome)]] <- rbindlist(c(chip_list,atac_list),fill=TRUE)
          
      } else {
        warning(paste(genome,"No CHIP-seq data available for given arguments",sep=": "))
      }
    }
  }
  output_file <- paste(outfile,"csv",sep=".")
  
  if(is.null(csv_data)) {
    stop("No data available for CSV")
  } else {
    csv_data <- unlist(csv_data,recursive=FALSE) # flatten genome lists into one list
    write.csv(csv_data,file=output_file,na="",row.names=FALSE)
    # remove newline characters
    t <- read.csv(file=output_file,na.strings = "\n")
    write.csv(t,file=output_file,na="",row.names=FALSE)
  }
}

create_linking_table(args$genomes,args$chromosomes,args$biosources,args$type,args$atactype,args$marks,args$output)
