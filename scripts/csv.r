#!/usr/bin/env Rscript
required_packages <- c("BiocManager","data.table","argparse")
install.packages(setdiff(required_packages,rownames(installed.packages())))
if(!"DeepBlueR" %in% installed.packages()) BiocManager::install("DeepBlueR")
library(argparse)
library(DeepBlueR)
library(data.table)

parser <- ArgumentParser()

parser$add_argument("-g", "--genomes", nargs="+", type="character", default=c("hg19","GRCh38"),
                    choices= suppressMessages(deepblue_list_genomes()$name),
                    help="(List of) genomes to include [default: \"%(default)s\"]")
parser$add_argument("-t", "--type", nargs="+", type="character", default="peaks", choices=c("peaks","signal"),
                    help="Experiment file types allowed for CHiP-Seq data [default: \"%(default)s\"]")
parser$add_argument("-m", "--marks", nargs="+", type="character", default=NULL,
                    help="(List of) epigenetic marks (i.e. transcription factors) to include [default: all]")

args <- parser$parse_args()

# create_linking_table()
# Takes optional arguments (to be expanded)
# Creates a csv file built from specific Deepblue data

create_linking_table <- function(genomes,chip_type,chip_marks) {
  
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
    e <- metadata$`_id`
    print(e)
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
  
  # ATAC-Seq: signals (mark: DNA Accessibility)
  # DNAse-Seq: signals and peaks (marks: DNA Accessibility, DNAseI)
  
  # 1st Step: Collect biosources for ATAC
  
  chrs <- paste("chr",c(1:22,"X","Y"),sep="")

  atac <- deepblue_list_experiments(genome=genomes, technique="ATAC-Seq", type=("signal"), epigenetic_mark="DNA Accessibility")$id
  dnase <- deepblue_list_experiments(genome=genomes, technique="DNAse-Seq", epigenetic_mark=c("DNA Accessibility","DNaseI"))$id
  access_experiments <- c(atac,dnase)
  
  atac_metadata <- lapply(access_experiments,function(x){ deepblue_info(x) })
  atac_biosources <- unique(sapply(atac_metadata,function(x) { x$sample_info$biosource_name }))
  
  # 2nd Step: Collect ChiP experiments and add to csv list if biosource has available ATAC data
  
  if(is.null(chip_marks)) {
    chip_marks <- deepblue_list_epigenetic_marks(extra_metadata = list(category="Transcription Factor Binding Sites"))$name
  }
  chips <- deepblue_list_experiments(genome=genomes, technique="ChiP-Seq", type=chip_type, epigenetic_mark=chip_marks)$id

  chip_list <- lapply(chips,function(c) {
    metadata <- deepblue_info(c)
    biosource <- metadata$sample_info$biosource_name
    if(biosource %in% atac_biosources) {
      filenames <- chrom_in_filename(metadata$name,chrs)
      for(f in filenames) {
        return(new_row(metadata,f))
      }
    } else {
      return(NA)
    }
  })
  
  chip_list <- chip_list[!is.na(chip_list)]
  
  chip_biosources <- sapply(chip_list,function(x){ x$biosource })
  req_biosources <- intersect(atac_biosources,chip_biosources)
  
  # 3rd Step: Add ATAC experiments to csv if biosource has available ChiP data
  
  atac_list <- lapply(atac_metadata,function(m) {
    if(m$sample_info$biosource_name %in% req_biosources) {
      filenames <- chrom_in_filename(m$name,chrs)
      for(f in filenames) {
        return(new_row(m,f))
      }
    }
  })
  
  csv_data <- rbindlist(c(chip_list,atac_list),fill=TRUE)
  
  if(nrow(csv_data) > 0) {
    write.csv(csv_data,file="linking_table.csv",na="",row.names=FALSE)
    # remove newline characters
    t <- read.csv("linking_table.csv",na.strings = "\n")
    write.csv(t,file="linking_table.csv",na="",row.names=FALSE)
  }
}

create_linking_table(args$genomes,args$type,args$marks)
