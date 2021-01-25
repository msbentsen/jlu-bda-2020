#!/usr/bin/env Rscript
library(DeepBlueR)
library(dplyr)
create_linking_table <- function(use_similar_bsources=TRUE,use_chip_signals=FALSE,homo_only=TRUE) {
  
  new_row <- function(e,metadata) {
    # This function retrieves the metadata for a DeepBlue experiment and converts it into a data.frame object
    sample_info <- metadata$sample_info
    extra <- metadata$extra_metadata
    meta <- data.frame(
      experiment_id=e,
      genome=metadata$genome,
      biosource=metadata$sample_info$biosource_name,
      technique=tolower(metadata$technique),
      epigenetic_mark=metadata$epigenetic_mark,
      filename=metadata$name,
      data_type=metadata$data_type,
      format=metadata$format,
      total_size=metadata$upload_info$total_size,
      sample_info,
      extra
      )
    return(meta)
  }
  
  # function arguments
  if(use_chip_signals) {
    chip_type <- c("signal","peaks")
  } else {
    chip_type <- "peaks" # default
  }
  if(homo_only) {
    genomes <- c("hg19","GRCh38","hs37d5") # homo sapiens only
  } else {
    available_genomes <- deepblue_list_genomes()
    genomes <- available_genomes$name
  }
  
  # ATAC-Seq: signals (mark: DNA Accessibility)
  # DNAse-Seq: signals and peaks (marks: DNA Accessibility, DNAseI)
  
  # 1st Step: Collect biosources for ATAC
  
  req_biosources <- c()
  csv <- data.frame(stringsAsFactors = FALSE)
  
  atac_biosources <- c()
  atac <- deepblue_list_experiments(genome=genomes, technique="ATAC-Seq", type=("signal"), epigenetic_mark="DNA Accessibility")
  dnase <- deepblue_list_experiments(genome=genomes, technique="DNAse-Seq", epigenetic_mark=c("DNA Accessibility","DNaseI"))
  access_experiments <- rbind(atac,dnase)
  for(e in access_experiments$id) {
    metadata <- deepblue_info(e)
    atac_biosources <- c(atac_biosources,metadata$sample_info$biosource_name)
  }
  atac_biosources <- unique(atac_biosources)
  
  # 2nd Step: Collect ChiP experiments and add to csv if biosource has available ATAC data
  
  chip_marks <- deepblue_list_epigenetic_marks(extra_metadata = list(category="Transcription Factor Binding Sites"))
  chips <- deepblue_list_experiments(genome=genomes, technique="ChiP-Seq", type=chip_type, epigenetic_mark=chip_marks$name)
  for(e in chips$id) {
    metadata <- deepblue_info(e)
    biosource <- metadata$sample_info$biosource_name
    if(biosource %in% atac_biosources) {
      # add new row to data frame
      req_biosources <- c(req_biosources,biosource)
      csv <- rbind(csv,new_row(e,metadata))
    } else {
      if(use_similar_bsources) {
        similars <- deepblue_list_similar_biosources(biosource)
        for(s in similars$name) {
          if(s %in% atac_biosources) {
            metadata$sample_info$biosource_name <- s
            csv <- rbind(csv,new_row(e,metadata))
            req_biosources <- c(req_biosources,s)
            break
          }
        }
      }
    }
  }
  
  # 3rd Step: Add ATAC experiments to csv if biosource has available ChiP data
  
  for(e in access_experiments$id) {
    metadata <- deepblue_info(e)
    if(metadata$sample_info$biosource_name %in% req_biosources) {
      csv <- rbind(csv,new_row(e,metadata))
    }
  }
  
  if(nrow(csv) > 0) {
    write.csv(csv,file="linking_table.csv",row.names=FALSE)
    # remove newline characters
    t <- read.csv("linking_table.csv",na.strings = "\n")
    write.csv(t,file="linking_table.csv",na="",row.names=FALSE)
  }
}

create_linking_table()
