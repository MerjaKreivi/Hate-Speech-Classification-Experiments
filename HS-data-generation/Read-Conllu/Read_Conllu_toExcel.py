# read_Conllu_toExcelFile.py
""" 
Python script to read conllu data file and construct data to excel file. 

The script was used on the research work reported on research paper:
Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.
"""

import zipfile
import argparse
import sys
import re
import datetime
import os
from datetime import datetime
from openpyxl import Workbook

### conllu file positional attributes: index form lemma upos xpos morphological_features dephead deprel deps SpaceAfter=No

### Corresponding to the data structure of conllu columns -- 10 tabs
INDEX, FORM, LEMMA, UPOS, XPOS, MFEATS, HEAD, DEPREL, DEPS, SPACES = range(10) 


def read_conlluFile(conllu_file):

    index = ""        
    form = ""        
    lemma = ""        
    upos = ""        
    xpos = ""        
    mfeats = ""        
    head = ""        
    deprel = ""        
    deps = ""        
    spaces = ""        

    for line in conllu_file:
        try:
            line = line.decode("utf-8").strip()
        except:
            line = line.strip()
        if not line:
            continue

        # when new comment starts as "# newdoc"
        if line.startswith("# newdoc"):            
            if len(form) > 0:
                yield form, lemma, upos, xpos, mfeats

            index = ""        
            form = ""        
            lemma = ""        
            upos = ""        
            xpos = ""        
            mfeats = ""        
            head = ""        
            deprel = ""        
            deps = ""        
            spaces = ""              
            continue
                                  
        # when comment is in the end of paragraph, add \n\n in original text (as empty rows)
        if line.startswith("# sent_id"):
            sentence_counter = matchToSentenceNumber(line)
            if (sentence_counter) > 1:
                form += " "
                lemma += " "
                upos += " "
                xpos += " "
                mfeats += " "
            continue

        # #newpar and #text lines are not collected 
        if line.startswith("# newpar"):
            continue
        if line.startswith("# text"):
            continue
       
        # must be an actual token line for collection
        # if not skip conllu row
        cols = line.split("\t")        
        if len(cols) != 10: 
            print("Weird line, skipping...", line, file=sys.stderr)
            continue

        if cols[SPACES] == "SpaceAfter=No":
            form += cols[FORM]
            lemma += cols[LEMMA]
            upos += cols[UPOS]
            xpos += cols[XPOS]
            mfeats += cols[MFEATS]
        else:
            form += cols[FORM]+" "
            lemma += cols[LEMMA]+" "
            upos += cols[UPOS]+" "
            xpos += cols[XPOS]+" "
            mfeats += cols[MFEATS]+" "
    else:
        if len(form) > 0:
            yield form, lemma, upos, xpos, mfeats


# Matches # sent_id = ,get the digit, convert to integer and return
def matchToSentenceNumber(sentenceId):
    matchingString = ""
    match = re.search(r'# sent_id = (\d+)', sentenceId)
    if match:
        matchingString = match.group(1)                   
    return int(matchingString)


def print_conllu_data_to_excel(zipFileHandle, metadata_workbook):    
    counter = 0
    new_worksheet = metadata_workbook.active # insert at the end (default)
    new_worksheet.title = "HS_conllu_data_"
    openConlluFile(zipFileHandle, new_worksheet, counter)        
    dt_string = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    filename = str.join("_", [new_worksheet.title, dt_string])
    complete = filename + ".xlsx"
    metadata_workbook.save(complete)


def openConlluFile(conlluFile, new_worksheet, counter):    
    with open(conlluFile, encoding='utf8') as infile:
        # collect attribute, meta, text
        readInputFile(infile, new_worksheet, counter)        


def readInputFile(infile, new_worksheet, counter):
    for form, lemma, upos, xpos, mfeats in read_conlluFile(infile):
        counter += 1
        # count and print hit number
        print("#_hitnumber:", counter)
        # print opened input file
        #print("#_filename:", infile.name)
        # print data 
        #prependValues = [counter, infile.name, form, lemma, upos, xpos, deprel]
        prependValues = [counter, form, lemma, upos, xpos, mfeats]           
        new_worksheet.append(prependValues)    


def main(args):
    if len(args.zipFile) > 0:        
        print("Reading zip file...")
        wb = Workbook()
        print_conllu_data_to_excel(args.zipFile, wb)
    else:
        print("No input file given")

# ---------------------------------------------

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description='conllu reader for open conllu txt file')    
    argparser.add_argument('--zipFile', default="C:\\Users\\mhkreivi\\Desktop\\HSconlluTest.conllu", help='conllu data file as txt from TurkuParser')
    argparser.add_argument('--metaFilter', default="topic_name_top", help='Insert one filter from meta data ')    
    args = argparser.parse_args()
    main(args)

# ---------------------------------------------