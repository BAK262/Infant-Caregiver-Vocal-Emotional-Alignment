# This is for reformatting and cleaning data before further analysis.
# 
# author: Ming Li
# date: 2023-01-30

library(bruceR)
corpus = c("corpus_Edinburgh")#"corpus_Nelson","corpus_Sachs"

# import model embedding and prosody feature of samples from .csv files
sample.embedding = list()
for (model in c(1:5)) {
  embedding.temp = list()
  for (c in c(1:length(corpus))) {
    import(paste0(corpus[c],"/embedding/model_",model,".csv"),as="data.table") %>%
      .[,c(5:516)] -> embedding.temp[[c]]
  }
  embedding.temp %>%
    rbindlist() -> sample.embedding[[model]]
}
rm(embedding.temp)
sample.prosody = list()
for (c in c(1:length(corpus))) {
  import(paste0(corpus[c],"/audio_feature/feature_data.csv"),as="data.table") %>%
    .[,c(5:6377)] -> sample.prosody[[c]]
}
rbindlist(sample.prosody) -> sample.prosody


# import sample information from arbitrary .csv file
sample.label = list()
for (c in c(1:length(corpus))) {
  import(paste0(corpus[c],"/embedding/model_1.csv"),as="data.table") %>%
    .[,c(1:4)] %>%
    .[,Dataset:=corpus[c]] -> sample.label[[c]]
}
sample.label %>%
  rbindlist() -> sample.label

# import index of samples without voice, which is pre-checked on audio files by computing the fundamental frequency
noise.index = list()
for (c in c(1:length(corpus))) {
  import(paste0(corpus[c],"/segments_without_voice.txt"),as="data.table",header = F) %>%
    .[,1] -> noise.index[[c]]
}
noise.index %>%
  rbindlist() %>%
  .[,c("file_id","participant","start_time","end_time"):=tstrsplit(V1,"_",fixed = T)] %>%
  .[,start_time:=as.integer(start_time)] %>%
  .[,end_time:=as.integer(end_time)] %>%
  .[,V1:=NULL] -> noise.index
sample.label[, noise := FALSE][noise.index, noise := TRUE, on = .(file_id,
                                                                  participant,
                                                                  start_time,
                                                                  end_time)]

# function to extract child's name and age
name_age <- function(file_string) {
  child_name = str_extract(file_string, "^[a-zA-Z]+")
  age_string = str_extract(file_string, "[0-9]+")
  if (as.numeric(age_string) > 99999) {
    stop("age > 10 years")
  }
  if (nchar(age_string) == 6) {
    age_string = substr(age_string,2,6)
  } else if (nchar(age_string) == 4){
    age_string = paste0("0",age_string)
  }
  age_year = as.numeric(substr(age_string,1,1))
  age_month = as.numeric(substr(age_string,1,1))*12 + as.numeric(substr(age_string,2,3))
  return(data.frame(result1 = child_name, result2 = age_year, result3 = age_month))
}

# function to determine whether a sample is in a conversation block & is overlapped with other samples
determine_block <- function(data){
  # sort the data by start time
  sorted_data <- copy(data[order(data$start_time),])
  # create a new column to store the block number and overlap state
  sorted_data[,"block":=1]
  sorted_data[,"overlap":=F]
  # initialize the block number
  block_num <- 1
  # loop through each row and determine the block number
  # A block is composed of sequence utterances that were consecutively produced
  # with pause shorter than 3seconds. The pause between blocks should be greater
  # than 3 seconds.
  for (i in 2:nrow(sorted_data)){
    if ((sorted_data[i,start_time]-sorted_data[i-1,end_time]) <= 3000){
      sorted_data[i,block:=block_num]
      # in addition, determine whether a utterance is overlapped with last one
      if ((sorted_data[i,start_time]-sorted_data[i-1,end_time]) < 0){
        sorted_data[i-1,overlap:=T]
        sorted_data[i,overlap:=T]
      }
    } else {
      block_num <- block_num + 1
      sorted_data[i,block:=block_num]
    }
  }
  # create a new column to store the block type
  # type1: conversation
  # type2: monologue
  sorted_data[,"block_type":=""]
  # loop through each block and determine the block type
  for (i in 1:max(sorted_data$block)){
    speakers <- unique(sorted_data[block == i,speaker])
    if (length(speakers) > 1){
      sorted_data[block == i,block_type:="conversation"]
    } else {
      sorted_data[block == i,block_type:="monologue"]
    }
  }
  # recover the original row order
  original_order <- order(match(data$start_time,sorted_data$start_time))
  final_data <- sorted_data[original_order,]
  
  return(final_data)
}

# reformat data
sample.label %>%
  .[,c("child","age_year","age_month"):=name_age(file_id), by=file_id] %>%
  .[participant=="CHI", participant:="Children"] %>%
  .[(participant=="MOT" | participant=="MOM"), participant:="Mother"] %>%
  .[(participant=="FAT" | participant=="DAD"), participant:="Father"] %>%
  .[(participant!="Mother" & participant!="Father" & participant !="Children"), participant:="Other Adult"] %>%
  setnames(.,"participant", "speaker") %>%
  .[speaker=="Children",speaker_type:="Children"] %>%
  .[speaker!="Children",speaker_type:="Adult"] %>%
  split(., .$file_id) %>%
  lapply(., determine_block) %>%
  rbindlist() -> sample.label

# remove all noise samples
delete.index = sample.label[,which(noise==T)]
for (m in 1:5) {
  sample.embedding[[m]] <- sample.embedding[[m]][-delete.index]
}
sample.prosody <- sample.prosody[-delete.index]
sample.label <- sample.label[-delete.index]

# remove all overlapped samples
delete.index = sample.label[,which(overlap==T)]
for (m in 1:5) {
  sample.embedding[[m]] <- sample.embedding[[m]][-delete.index]
}
sample.prosody <- sample.prosody[-delete.index]
sample.label <- sample.label[-delete.index]

# for corpus "Edinburgh", remove all monologue samples (89/26963 in total)
# reason: the main aim of this corpus is providing mother-infant interaction data
delete.index = sample.label[,which(Dataset=="corpus_Edinburgh" &
                                     block_type=="monologue")]
for (m in 1:5) {
  sample.embedding[[m]] <- sample.embedding[[m]][-delete.index]
}
sample.prosody <- sample.prosody[-delete.index]
sample.label <- sample.label[-delete.index]

# # for corpus "Nelson", remove all adult monologue samples (10/4593 in total)
# # reason: the main aim of this corpus is providing child bedtime monologue data
# delete.index = sample.label[,which(Dataset=="corpus_Nelson" &
#                                      block_type=="monologue" &
#                                      speaker_type=="Adult")]
# for (m in 1:5) {
#   sample.embedding[[m]] <- sample.embedding[[m]][-delete.index]
# }
# sample.prosody <- sample.prosody[-delete.index]
# sample.label <- sample.label[-delete.index]

# combine sample embedding and label
export(sample.embedding[[1]],"Data_Analysis/sample_embedding1.csv")
export(sample.embedding[[2]],"Data_Analysis/sample_embedding2.csv")
export(sample.embedding[[3]],"Data_Analysis/sample_embedding3.csv")
export(sample.embedding[[4]],"Data_Analysis/sample_embedding4.csv")
export(sample.embedding[[5]],"Data_Analysis/sample_embedding5.csv")
export(sample.prosody,"Data_Analysis/sample_prosody.csv")
export(sample.label,"Data_Analysis/sample_label.csv")

