exportFromCsv <- function(file) {

  data <- read.csv(file=file,header=TRUE)
  chrs <- c(1:22,c("X","Y"))
  
  # for each experiment and each chromosome of that experiment, download
  
  for(row in 1:nrow(data)) {
    e = data[row,]
    id = e$experiment_id
    name = e$filename
    format = e$format
    for(c in chrs) {
      query_id = deepblue_select_experiments(experiment_name = name, chromosome = c)
      request_id = deepblue_get_regions(query_id = query_id, output_format = format) # output_format required -> problem
      regions = deepblue_download_request_data(request_id)
      deepblue_export_tab(regions,file.name=name)
      deepblue_export_meta_data(id, file.name=paste(name,".",c))
    }
  }
}