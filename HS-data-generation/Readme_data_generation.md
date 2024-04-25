# Hate Speech (HS) Data Generation

This folder includes python scripts to read and collect social media textual data 
to construct HS and sentiment data to SQL databases, txt files and excel files. 


## Introduction

The scripts were used on the research work reported on research paper:
Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.

The goal of data generation process was to collect and label about 10 000 samples of the social media textual data including comments, headlines, and nicknames. 

The main goal was that the data would be diverse and would contain plenty of examples of different forms of HS. 

The HS and sentiment data set was gathered by various data mining methods which focused to include only social media originated content.

As the aim was to design and test HS and cyberbullying analysis and classification methods for children and adolescents, 
the data creation phase included attempts to collect data posted by users aged between 7 – 18 years.

Data was collected both from publicly available open data sources (Suomi24 corpus) 
and social media sites (YouTube, Suomi24, Ylilauta) commonly used by children, teenagers, and young adults.

Data was created by using keyword (KW) data mining methods for Suomi24 open data frames, and keyword (KW) web-crawling methods for open data of YouTube API. 

Small set of data was collected by copying samples from public social media sites like Suomi24, YouTube, and Ylilauta.


## Dataset

The final dataset of generated research data was not shared or published.


## Read Conllu -folder 

Read Conllu -folder includes both example scripts and used scripts to collect 
textual, annotation, and metadata from conllu constructed data files.


## Read Suomi24 -folder 

Read Suomi24 -folder includes both example scripts and used scripts to collect 
textual, annotation, and metadata from conllu constructed ZIP VRT data files of Suomi24 dataset.

Scripts use KW and 'key string' data mining methods to search and find data.

Includes scripts to read, collect, and save textual data from 'raw' comments, lemmas, headlines, and author 'nicks'.

Collected data is printed out, saved to txt file(s), or saved to xlsx -file(s).

Reference - The Suomi24 sentences corpus 2001–2017. (2019). Aller Media Ltd., Korp version 1.1. URL:  http://urn.fi/urn:nbn:fi:lb-2020021803 


## Read YouTube -folder 

Read YouTube -folder includes both example scripts and used scripts to collect 
textual data and metadata from YouTube with YouTube API.

Scripts use KW and 'key string' web-crawling methods for open data of YouTube API to search and find HS data.

Includes scripts to read, collect, and save textual data from YouTube comments and headlines.

Collected data is printed out, and saved as SQL databases.
