#!/usr/bin/env Rscript
library(DeepBlueR)
library(dplyr)
create_linking_table <- function(chip_marks,use_similar_bsources=TRUE,use_chip_signals=FALSE,homo_only=TRUE) {
  
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
  
  chip_marks <- deepblue_list_epigenetic_marks(extra_metadata = {"category":"Transcription Factor Binding Sites"})
  chips <- deepblue_list_experiments(genome=genomes, technique="ChiP-Seq", type=chip_type, epigenetic_mark=chip_marks)
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
  }
}

# chip_marks <- deepblue_list_epigenetic_marks(extra_metadata = {"category":"Transcription Factor Binding Sites"})
chip_marks <- c("rabbit-IgG-control","DDX52","Non-specific target control","UCHL5","TFIP11","SERBP1","RRP9","PRPF8","EFTUD2","FAM120A","DDX27","BCLAF1","UPF2","TROVE2","RCC2","PSIP1","PKM","NUSAP1","METAP2","NIP7","CCAR2","GRWD1","GNB2L1","SMNDC1","ZRANB2","SRSF5","SUB1","GTF2F1","HLTF","IGF2BP1","PCBP2","FASTKD2","AGO1","AATF","SSB","SRSF4","TAF15","SRSF9","SRSF7","SRSF1","NELFE","RECQL","PTBP1","PCBP1","NCBP2","PABPC4","MATR3","IGF2BP3","IGF2BP2","KHSRP","HNRNPK","DDX6","DDX3X","CIRBP","AKAP1","EIF4A3","TARDBP","RBM22","TBRG4","U2AF1","RBM15","FXR2","CELF1","HNRNPU","SF1","CNOT8","BRF2","GTF3C2","BRF1","SIRT6","BDP1","eGFP-JUNB","ZZZ3","SUPT20H","KAT2A","eGFP-HDAC8","TFBS","NFYA","eGFP-NR4A1","SMARCB1","RAD21","EBF1","RCOR1","BRCA1","SMC3","NRF1","CHD2","SOX17","POLR2A","TAL1","EP300","TBP","CEBPB","STAT1","mouse-IgG-control","POLR2AphosphoS2","SMARCA4","MAX","TCF7L2","MXI1","GATA1","MAFK","BHLHE40","UBTF","JUN","MAZ","ZNF143","ZNF384","ZC3H11A","ZMIZ1","CBX7","HCFC1","SREBF1","WRNIP1","IRF3","SIN3A","YY1","ZBTB4","SETDB1","NR2C2","ZNF263","RELA","PPARGC1A","HNF4A","NR3C1","ESRRA","SKI","PRDM4","goat-IgG-control","CEBPZ","IKZF1","TBL1XR1","MYC","BACH1","HA-E2F1","ZBTB33","POLR2AphosphoS5","TEAD4","SP1","EGR1","USF1","REST","ESR1","TCF7L1","SUZ12","VDR","E2F1","SMARCC2","SMARCC1","PRDM1","ZKSCAN1","PML","NR2F2","TCF12","GABPA","FOXM1","FOSL2","HDAC2","GMEB2","SP4","ATF2","BCL3","TAF1","ETS1","POU5F1","NANOG","TAF7","BCL11A","FOXP2","PHF8","CHD7","EZH2","RNF2","HDAC1","WHSC1","KDM5B","RBBP5","KAT2B","NCOR1","CREBBP","KDM4A","KDM1A","CBX8","CREB3L1","HDAC6","CBX2","KDM5A","ZBTB7A","NFIC","TCF3","T7-control","ELAVL1","PABPC1","CTCFL","ATF7","CEBPD","NFATC1","ZEB1","MEF2C","RUNX3","STAT5A","SPI1","JARID2","MYBL2","IRF4","GRHL3","HNRNPM","HNRNPA1","MEN1","RBFOX2","EIF4G1","EIF4G2","FOXH1","GATA4","rat-IgG-control","MYB","FLI1","MYOG","MYOD1","H3ac","HNRNPAB","HNRNPD","HNRNPA0","MBD3","ILF3","WWTR1","MEF2B","EIF3A","DNAJC21","DNAJC2","DHX30","YBX3","CCAR1","ADAR","XPO5","IRF5","UBE2L3","SART3","RPS3A","LYL1","PUM2","PUM1","PUF60","JUNB","NIPBL","HNRNPA2B1","OVOL2","FASTKD1","APOBEC3C","DDX55","SUPV3L1","EIF3D","PA2G4","DDX28","BCCIP","RBM27","PHF6","MARK2","LIN28B","LARP7","FKBP4","DDX59","RTF1","U2AF2","RAVER1","SND1","XRCC5","PRPF6","XRCC6","RBM34","EXOSC9","EIF3G","CSTF2T","RPS3","SF3B4","RBM25","MAGOH","G3BP2","G3BP1","ASCC1","EIF2S1","FUBP3","CPSF6","POLR2G","PAPOLA","AGO3","AGO2","HMGN3","GTF2B","NFYB","eGFP-GATA2","GATA2","STAT3","CBX3","FOSL1","FOXA1","ZNF217","CTBP2","FOXA2","HNF4G","MTA3","BATF","SAFB2","TRIM56","KHDRBS1","HNRNPF")
chip_marks <- c(chip_marks,"PNPT1","CNOT7","DGCR8","EIF2S2","CBX1","ZBED1","SMAD5","eGFP-ILK","eGFP-DDX20","eGFP-ID3","eGFP-ZNF24","eGFP-TEAD2","eGFP-TSC22D4","eGFP-KLF13","eGFP-PYGO2","eGFP-NFE2L1","eGFP-IRF1","eGFP-HINFP","eGFP-ETV1","eGFP-DIDO1","eGFP-CREB3","eGFP-TAF7","eGFP-MAFG","eGFP-PTTG1","eGFP-IRF9","eGFP-PTRF","eGFP-KLF1","eGFP-RELA","eGFP-CEBPB","DPF2","ARNT","eGFP-ATF1","FOXK2","CTBP1","HMBOX1","DEAF1","MYNN","DDX20","ZNF24","TCF7","ZBTB11","TFAP4","KDM4B","RUNX1","YTHDC2","TRIP6","SUPT6H","SSRP1","SUGP2","STAU1","SNRNP200","SFPQ","RBM17","RBM39","PPP1R8","NPM1","PABPN1","LARP4","HSPD1","HNRNPUL1","FIP1L1","DROSHA","ABCF1","ESF1","PUS1","NUFIP2","NAA15","NKRF","KIF1C","KRR1","HDGF","DKC1","DDX19B","CALR","ATP5C1","AKAP8L","AKAP8","ACO1","DEK","BMI1","TFDP1","CREM","ETV6","ZHX2","MITF","UPF1","ZNF622","MTPAP","AGGF1","TNRC6A","GNL3","SF3A3","HNRNPH1","DNMT1","CBX3phospho","EEF2","SRP68","RPS19","NONO","GEMIN5","DDX51","CSTF2","RPS2","RPLP0","RPL23A","LSM11","RPS10","SLTM","TRA2A","FUS","DDX24","DDX21","DAZAP1","NFX1","TIA1","QKI","EIF4B","FXR1","EWSR1","PPIL4","HNRNPC","DDX47","RBM3","CCNT2","ATF1","eGFP-JUND","eGFP-FOS","POLR3G","USF2","ARID3A","E2F4","E2F6","ZNF274","HSF1","MAFF","ELK4","FOS","IRF1","SRF","GATA3","CREB1","SP2","RXRA","H2AFZ","SAP30","CHD4","MBD4","XRCC4","POU2F2","PAX5","SLBP","FMR1","DDX42","AUH","TIAL1","SRFBP1","PARN","CPSF7","SMN1","STIP1","SUCLG1","SBDS","RBM47","NOL12","ILF2","GRSF1","EED","PPIG","MSI2","BUD13","CKAP4","SIN3B","CBX5","RPS11","YWHAG","WDR5","NUP98","STAG2","KMT2A","FOXP1","RAD51","TP53","BRD4","CEBPE","MED1","CEBPA","POU2F1","KLF4","RARA","RB1","TP73","ZNF711","KAT8","KAT5","HDAC3","TFAP2C","TP63","PPARG","ESR2","ATRX","AR","ERG","PRDM14","ETV1","GATAD1","GLYR1","CDX2","DDX5","TRIM24","HMGN1","EOMES","BCL6","NCOA1","DOT1L","NR1H3","NR2F1","L3MBTL2","NKX3-1","CBFB","SMAD2","SMAD3","SMAD4","RBPJ","NFKBIA","AFF4","ETV4","NCOR2","NR4A1","HDAC8","TBX21","THAP11","EGR2","CTNNB1","TCF4","SMAD1","NCOA3","CARM1","HEY1","TEAD1","MLLT3","FOXO1","PGR","CDK9","WRN","ATF4","ARNTL","HIF1A","SETD1A","ASCL1","NEUROD1","RAG1","BACH2","ARID1A","ARID1B","ARID2","NR3C2","IRF2","ORC2","LMO2","RUNX2","PAF1","CLOCK","TFAP2A","GRHL2","HOXC9","KDM5C","CBFA2T2","PCGF6","KDM3B","EPAS1","VEZF1","MYCN","SMARCA5","SMARCA1","SMARCA2","LEF1","AFF1","ASH1L","LMNB1","EP400","MED26","BCOR","KLF6","ELF3","MLLT1","CXXC1","POU3F2","SNAPC4","ZBTB16","NFE2L2","POLR2B","SNAPC5","HOXA9","SOX9","SON","NR1H2","FOXK1","ZNF76","BRD9","TRIM25","NKX2-1","FOXR2","LMNA","KMT2C","E2F7","SUMO1","ZSCAN5B","ZSCAN5A","EHF","AHR","UBE2I")
chip_marks <- c(chip_marks,"FOXP3","ZFX","CDKN1B","KLF1","PAX6","CBFA2T3","NR5A1","ZBTB17","ERCC3","PITX3","FOXD3","KMT2D","FAM208A","ZBTB48","SMARCE1","ZNF516","RING1","NR5A2","PAX7","HOXB7","ING5","MECP2","ZC3H8","TFAM","SPDEF","BCL10","BATF3","CAMTA1","FERD3L","FOSB","FOXF1","FOXQ1","HES5","HES7","HESX1","HIC2","HIVEP3","HNF1A","HNF1B","HOXA11","HOXB1","HOXB2","HOXB5","HOXD11","HOXD13","HOXD4","HOXD9","ID4","IKZF5","IRF8","IRX5","ISL2","KLF13","FOXO4","LHX4","LHX6","MAFB","MAFG","MIXL1","MSC","MYF6","NEUROD2","NFKB1","NHLH1","NKX2-8","NKX6-1","NR2F6","NR4A2","ARNT2","ATF6","DR1","ETV5","GLI2","HES4","HEYL","HHEX","HOXA13","HOXA4","HOXA5","HOXA6","HOXB4","KLF11","KLF15","NFAT5","NR1I2","NR2E3","PPARA","RELB","AHCTF1","CASP8AP2","E2F2","E2F8","ELF2","HOXB6","HOXB8","HOXC8","ID1","ID2","ID3","JAZF1","MXD3","NFYC","NR1D1","SALL4","TERF1","TERF2","TLX1","PBX2","STAT6","UBP1","ZBTB10","ZNF281","ZNF3","ZNF639","ADNP2","ARNTL2","BBX","CDC5L","CREBL2","DDIT3","DRAP1","ELF4","FOXC1","FOXF2","FOXJ2","GZF1","HAND1","HOXD1","IRF9","KCMF1","LCOR","LCORL","MEOX2","NFE2L1","GRHL1","HOXC11","HOXC13","MYBL1","NFE2L3","NFIB","NKX2-3","PLAG1","RFX7","RLF","TCFL5","TFCP2","THAP4","TSHZ1","YBX1","ZBTB2","ZBTB24","ZBTB39","ZBTB44","ZNF12","ZNF266","ZNF280D","ZNF395","ZNF581","ZNF83","ZNF84","KLF5","ASXL1","ZFHX4","LDB1","XBP1","SUPT5H","CBX4","KDM4C","PDX1","MBD2","SNAI2","DICER1","APOBEC3B","NR1H4","ZNF750","EZH1","DMC1","ZNF92","ELK3","ASH2L","TCF21","ZFP42","HAND2","SOX10","KDM3A","EHMT2","ZNF644","WIZ","NFKB2","LHX2","CCNT1","ZNF165","XRN2","PES1","RPS5","AARS","ATF3","POLR3A","CTCF","RFX5","JUND","ELK1","SREBF2","CHD1","CUX1","NFE2","TRIM28","ELF1","PBX3","SIX5","THAP1","STAT2","MEF2A","DDX1","TUFM","HNRNPL","KAT7","POU2AF1","BHLHE41","RFX2","ZNF486","T","GTF2I","ARID3B","SOX2","TDRD3","GATA6","MEIS1","STAT4","STAT5B","YAP1","PROX1","CHD3","SATB1","SIX2","SIX1","RPA2","SRPK2","TOP1","PAX8","MCM3","PBX1","HSF2","BARX1","EVX1","LHX5","MTF1","E2F3","CDX1","DMRT2","IRX2","TOE1","SOX11","GFI1B","OTX2","KDM6A")
# ^don't do this

create_linking_table(chip_marks)
