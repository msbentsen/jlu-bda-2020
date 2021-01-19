exportFromCsv <- function(file) {

  # How this works: For each experiment and each chromosome, download all regions as a tab-separated text file.
  # The hg19 and Grch38 genomes contain more than 24 chromosomes, but we only use the common ones.
  
  data <- read.csv(file=file,header=TRUE)
  chrs <- paste("chr",c(1:22,"X","Y"),sep="")
  
  for(row in 1:nrow(data)) {
    e = data[row,]
    id = e$experiment_id
    name = e$filename
    format = e$format
    for(c in chrs) {
      query_id = deepblue_select_experiments(experiment_name = name, chromosome = c)
      request_id = deepblue_get_regions(query_id = query_id, output_format = format) # output_format required
      regions = try(deepblue_download_request_data(request_id),silent=TRUE) # ignore errors when no regions found for this chromosome (this is not unusual)
      if(class(regions)=="GRanges") {
        filename = paste(name,".",c,sep="") 
        deepblue_export_tab(regions,file.name=filename)
        deepblue_export_meta_data(id, file.name=filename)
      }
    }
  }
}