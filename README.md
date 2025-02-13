# Description

This project aims to estimate vocal emotions during infant-caregiver interactions and to examine the prosody-based emotional alignment between two parties. For more details, see the [conference paper](https://ieeexplore.ieee.org/abstract/document/10364533):

> M. Li, J. Li, D. Zhang and Y. Nagai, "Prosody-Based Vocal Emotional Alignment in Infant-Caregiver Interaction," *2023 IEEE International Conference on Development and Learning (ICDL)* , Macau, China, 2023, pp. 361-366, doi: 10.1109/ICDL55364.2023.10364533.

# Requirements

## dataset - Edinburgh Corpus

[CHILDES Edinburgh Corpus](https://childes.talkbank.org/access/Eng-UK/Edinburgh.html) has been analyzed. Parts of the dataset are placed in `/corpus_Edinburgh/raw_data` folder, excluding the raw audio recordings (`.mp3` files). If you want to reproduce the entire protocol, please directly download the raw dataset from [the corpus&#39; webpage](https://childes.talkbank.org/access/Eng-UK/Edinburgh.html), and place all audio recordings into the raw data folder.

## prosodic-feature toolbox - Opensmile

The open-source toolbox used to extract prosodic features of audio recordings is `opensmile`. Here we provide a copy of both its win32 version and mac version for users' convenience.

## vocal-emotional model

This is the core idea of the project - using a deep contrastive model to estimate the vocal emotions (by means of its output embedding). The model is provided by the author of the paper "[Quantifying Emotional Similarity in Speech](https://ieeexplore.ieee.org/document/9612052)". Anyone wanting to use this code/model should get permission from the original author. The code provided on this page is only used to reproduce the analysis process of this project.

# Steps

## Feature extraction

Run the `.py` files in the `/Feature_Extraction` folder by order to obtain prosodic features and model embeddings of all utterence samples from the corpus. All output will be stored in the `/corpus_Edinburgh` folder.

## Data preprocessing

Run the `/Data_Analysis/Data_Preprocess.R` file to clean and reformat the new dataset output from the above step. The preprocessed data will be stored in the `/Data_analysis` folder.

## Data analysis

Follow the `/Data_Analysis/Analysis_Edinburgh.Rmd` file to reproduce all formal analysis and the figures. The results will be stored in the `/Data_analysis/Analysis_Edinburgh` folder.

# Contact

* Ming Li: [liming16@tsinghua.org.cn](liming16@tsinghua.org.cn)
