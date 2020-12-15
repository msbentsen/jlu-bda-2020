# altered from https://bioconductor.org/packages/release/bioc/vignettes/DeepBlueR/inst/doc/DeepBlueR.html#data-export
experiments = deepblue_list_experiments(technique = "ATAC-seq")
experiment_names = deepblue_extract_names(experiments)
request_ids = c()
for(name in experiment_names) {
  query_id = deepblue_select_experiments(experiment_name = name, chromosome = "chr1")
  request_id = deepblue_get_regions(query_id = query_id, output_format = "CHROMOSOME,START,END,VALUE") # output_format required -> problem
  request_ids = c(request_ids,c(name,request_id))
}
request_mat = matrix(request_ids,nrow=2)
for(i in c(1:length(request_mat[1,]))) {
  regions = deepblue_download_request_data(request_mat[2,i])
  deepblue_export_tab(regions,file.name=request_mat[1,i])
}