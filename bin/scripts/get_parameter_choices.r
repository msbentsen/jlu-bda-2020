#!/usr/bin/env Rscript

if(!"DeepBlueR" %in% installed.packages()) BiocManager::install("DeepBlueR")

library(DeepBlueR)

get_parameters <- function(){
  genomes=deepblue_list_genomes()
  biosources=deepblue_list_biosources()
  tfs=deepblue_list_epigenetic_marks()
  
  return(c(genomes$name,";",biosources$name,";",tfs$name)) 
}


get_parameters()
