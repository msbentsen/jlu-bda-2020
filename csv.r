# Options (could turn this into a function)
similar_biosources <- TRUE
chip_signals <- FALSE
if(chip_signals) {
  chip_type <- c("signal","peaks")
} else {
  chip_type <- "peaks" # default
}
genomes <- c("hg19","GRCh38","hs37d5") # homo sapiens only

collect_metadata <- function(e,metadata) {
  filename <- metadata$name
  if(grepl(".",filename,fixed=T)) {
    ext <- strsplit(filename,".",fixed=T)[[1]]
    fileext <- ext[length(ext)]
  } else {
    fileext <- ""
  }
  meta <- data.frame(
    experiment_id=e,
    genome=metadata$genome,
    biosource=metadata$sample_info$biosource_name,
    technique=metadata$technique,
    epigenetic_mark=metadata$epigenetic_mark,
    filename=metadata$name,
    data_type=metadata$data_type,
    extension=fileext,
    format=metadata$format,
    total_size=metadata$upload_info$total_size)
  return(meta)
}

# ChIP Data Type "only peaks for this workflow, but make it variable" (custom marks)
# ATAC-Seq: signals (mark: DNA Accessibility)
# DNAse-Seq: signals and peaks (marks: DNA Accessibility, DNAseI)

# 1. Step: Retrieve ATAC+DNAse metadata, extract list of biosources

# filter epigenetic marks, types...
chip_marks <- deepblue_list_epigenetic_marks(extra_metadata = {"category":"Transcription Factor Binding Sites"})
# list required experiments
atac <- deepblue_list_experiments(genome=genomes, technique="ATAC-Seq", type=("signal"), epigenetic_mark="DNA Accessibility")
dnase <- deepblue_list_experiments(genome=genomes, technique="DNAse-Seq", epigenetic_mark=c("DNA Accessibility","DNaseI"))
access_experiments <- rbind(atac,dnase)
atac_csv <- data.frame(stringsAsFactors = FALSE)
for(e in access_experiments$id) {
  # get required metadata
  metadata <- deepblue_info(e)
  # add new row to data frame
  atac_csv <- rbind(atac_csv,collect_metadata(e,metadata))
}
atac_biosources <- unique(atac_csv$biosource)

# 2. Step: Retrieve ChiP-Seq metadata (peaks only), add to data frame if biosources match

chips <- deepblue_list_experiments(genome=genomes,technique="ChiP-Seq", type=chip_type, epigenetic_mark=chip_marks)
chip_csv <- data.frame(stringsAsFactors = FALSE)
for(ce in chips$id) {
  metadata <- deepblue_info(ce)
  biosource <- metadata$sample_info$biosource_name
  if(biosource %in% atac_biosources) {
    # add new row to data frame
    chip_csv <- rbind(chip_csv,collect_metadata(ce,metadata))
  } else {
    if(similar_biosources) {
      print(biosource)
      similars <- deepblue_list_similar_biosources(biosource)
      print(similars)
      for(s in similars$name) {
        if(s %in% atac_biosources) {
          metadata$sample_info$biosource_name <- s
          print(s)
          chip_csv <- rbind(chip_csv,collect_metadata(ce,metadata))
          break
        }
      }
    }
  }
}
chip_biosources <- unique(chip_csv$biosource)
csv <- rbind(atac_csv,chip_csv)
write.csv(csv,file="output.csv",row.names=FALSE)