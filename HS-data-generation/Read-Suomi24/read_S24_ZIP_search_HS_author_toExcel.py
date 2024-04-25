# read_S24_ZIP_search_HS_author_toExcel.py
""" 
Python script to read Suomi24 data files (from Kielipankki ZIP VRT files) 
and construct data to xlsx files. 

The script was used on the research work reported on research paper:
Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.

Introduction
 * Try to construct original plain text back from Kielipankki VRT files.
 * Include metadata as '#metadata:' comment lines
 * Each post treated as a separate documents
 * paragraph boundaries (\n\n) inside a post are included (exracted from <paragraph> tags)
 * detokenized using SpaceAfter=No, but does not preserve other spacing (i.e. single new lines etc...)
 * documents are not guaranteed to be in any particular order

Corresponds to the structure of range(11)
 * WORD, REF, LEMMA, LEMMACOMP, UPOS, MSD, DEPHEAD, DEPREL, SPACES, INITID, LEX

Script creates print out:
 * hitnumber = doc id
 * VRT filename
 * metadata
 * (comment) text

Script saves to excel:
 * counter
 * infile.name
 * (comment) text
 * lemmas, lemmacomp, pos, msd, deprel, lex
"""

import zipfile
import argparse
import sys
import re
import ftfy
import datetime
import os
from datetime import datetime
from openpyxl import Workbook

### <!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel spaces initid lex/ -->
### Corresponding to the defined data structure of UD columns -- 11 tabs
WORD, REF, LEMMA, LEMMACOMP, POS, MSD, DEPHEAD, DEPREL, SPACES, INITID, LEX = range(11) 

# DEFINE SEARCH STRING LIST ----------------------------------------------------------------------------------------------------

#searchForStringList = ["xsara", "mantra"]                    #  MIKAN TESTI

################# tee koodi joka huomioi sekä isot että pienet kirjaimet

#searchForStringList = ["vittu", "vttu"]
#searchForStringList = ["vit.", "wit.", "vit_", "wit_", "vit-", "wit-", "vit..", "wit..", "vit__", "wit__", "vit--", "wit--"]       # 138 paljon muita
#searchForStringList = ["vi.tu", "wi.tu", "vi_du", "wi_du", "vi..u", "wi..u", "vi__u", "wi__u", "vi--u", "wi--u"]                    #  25 
#searchForStringList = ["vittu", "vttu"]        # runsaasti
#searchForStringList = ["Vittu", "Vttu", "VITTU", "VTTU"]            # runsaasti
#searchForStringList = ["viddu", "widdu", "wittu", "vidu", "widu", "witu", "vddu", "wddu", "wttu"]          # runsaasti
#searchForStringList = ["..ddu", "__ddu", "--ddu", ".ddu", "_ddu", "-ddu", "..ttu", "__ttu", "--ttu", ".ttu", "_ttu", "-ttu", ".idu", "_idu", "-idu", ".itu", "_itu", "-itu"]        # vähän 70
#searchForStringList = ["w.ttu", "w_ttu", "w-ttu", "w.ddu", "w_ddu", "w-ddu", "v.ddu", "v_ddu", "v-ddu", "w..u", "w__u", "w--u", "w...u", "w___u", "w---u", "w.u", "w_u", "w-u"]                         # vain yksi
#searchForStringList = ["v.ttu", "v_ttu", "v-ttu", "v..u", "v__u", "v--u", "v...u", "v___u", "v---u", "v.u", "v_u", "v-u"]       # runsaasti

# ----------------- hakee kaikki kerralla       # kaikki 4285

searchForStringList = ["vittu", "vttu", "vit.", "wit.", "vit_", "wit_", "vit-", "wit-", "vit..", "wit..", "vit__", "wit__", "vit--", "wit--",
                        "vi.tu", "wi.tu", "vi_du", "wi_du", "vi..u", "wi..u", "vi__u", "wi__u", "vi--u", "wi--u",                   
                        "viddu", "widdu", "wittu", "vidu", "widu", "witu", "vddu", "wddu", "wttu",
                        "..ddu", "__ddu", "--ddu", ".ddu", "_ddu", "-ddu", "..ttu", "__ttu", "--ttu", ".ttu", "_ttu", "-ttu", ".idu", "_idu", "-idu", ".itu", "_itu", "-itu",
                        "w.ttu", "w_ttu", "w-ttu", "w.ddu", "w_ddu", "w-ddu", "v.ddu", "v_ddu", "v-ddu", "w..u", "w__u", "w--u", "w...u", "w___u", "w---u", "w.u", "w_u", "w-u",
                        "v.ttu", "v_ttu", "v-ttu", "v..u", "v__u", "v--u", "v...u", "v___u", "v---u", "v.u", "v_u", "v-u"]

# ---------------- kaikki haukkuma sanat        # kaikki yli 10000

#searchForStringList = ["matu", "mamu", "ähläm", "ryss",
#                        "kuolla", "kuole", "tappa", "hirttä", "hirtto"
#                        "idioot", "tyhm", "ruma", "läsk", 
#                        "nussi", "homo", "lesb",
#                        "persu", "perse", 
#                        "vassa", "vasuk", "suvak"]

# ---------------- haukkuma sanat 

#searchForStringList = ["kuolla", "kuole", "tappa", "tappo", "hirttä", "hirtto"]            # yli 2000
#searchForStringList = ["idioot", "tyhm", "ruma", "läsk"]                                   # yli 4000
#searchForStringList = ["matu", "mamu", "ähläm", "ryss"]                                    # yli 6000

# -------------------------------------------------------------------------------------------------------------------------------------

author_list = []

def fix_encoding(text):
    return ftfy.fix_text(text, uncurl_quotes=False)

# define metadata paragraphs read style
meta_regex = re.compile('([a-z_]+)="([^"]+)"', re.UNICODE)


def extract_meta(line, metafilter):
    # below example of new (2020) metadata style
    # <text comment_id="0" date="2001-01-01" datetime="2001-01-01 01:30:00" author="Honda" parent_comment_id="0" quoted_comment_id="0" author_logged_in="n" nick_type="anonymous" thread_id="19455" time="01:30:00" title="Hyvää uutta vuotta kaikille Hondailijoille" topic_nums="3258,1109,6254,2" msg_type="thread_start" topic_name_leaf="Honda" topic_name_top="Ajoneuvot ja liikenne" topic_names="Ajoneuvot ja liikenne &gt; Autot &gt; Automerkit &gt; Honda" topic_names_set="|Ajoneuvot ja liikenne|Automerkit|Autot|Honda|" topic_nums_set="|1109|2|3258|6254|" topic_adultonly="n" datefrom="20010101" dateto="20010101" timefrom="013000" timeto="013000" id="19455:0" author_v1="Honda" author_name_type="user_nickname" author_nick_registered="n" author_signed_status="0" thread_start_datetime="2001-01-01 01:30:00" filename_vrt="s24_2001_01.vrt" parent_datetime="" datetime_approximated="n" empty="n" filename_orig="threads2003a.vrt" origfile_textnum="17841">
    attribute = ""        
    meta_lines = []
    key_value_pair_list = []
    metadata_fields = meta_regex.findall(line)
    meta_copy_if_author_match = metadata_fields

    for key, value in metadata_fields:
        if key == metafilter:
            regularized = value.lower()
            if any(word in regularized for word in searchForStringList):
                if value not in author_list:
                    author_list.append(value)
                    attribute, meta_lines, key_value_pair_list = fix_encoding_for_meta(meta_copy_if_author_match)
            break
    return attribute, meta_lines, key_value_pair_list


def fix_encoding_for_meta(fields):
    meta_lines = []
    meta_key_value_pair_list =[]
    attribute = "" 
    for key, value in fields:
        if key == "attribute":
            attribute = fix_encoding(value)
            meta_lines.append(key + " = " + attribute)
            meta_key_value_pair_list.append(value)
            continue
        meta_lines.append(key + " = " + value)
        meta_key_value_pair_list.append(value)
    return attribute, meta_lines, meta_key_value_pair_list


def extract_meta_for_header(line):
    # below example of new (2020) metadata style
    # <text comment_id="0" date="2001-01-01" datetime="2001-01-01 01:30:00" author="Honda" parent_comment_id="0" quoted_comment_id="0" author_logged_in="n" nick_type="anonymous" thread_id="19455" time="01:30:00" title="Hyvää uutta vuotta kaikille Hondailijoille" topic_nums="3258,1109,6254,2" msg_type="thread_start" topic_name_leaf="Honda" topic_name_top="Ajoneuvot ja liikenne" topic_names="Ajoneuvot ja liikenne &gt; Autot &gt; Automerkit &gt; Honda" topic_names_set="|Ajoneuvot ja liikenne|Automerkit|Autot|Honda|" topic_nums_set="|1109|2|3258|6254|" topic_adultonly="n" datefrom="20010101" dateto="20010101" timefrom="013000" timeto="013000" id="19455:0" author_v1="Honda" author_name_type="user_nickname" author_nick_registered="n" author_signed_status="0" thread_start_datetime="2001-01-01 01:30:00" filename_vrt="s24_2001_01.vrt" parent_datetime="" datetime_approximated="n" empty="n" filename_orig="threads2003a.vrt" origfile_textnum="17841">
    keys_for_column_headers = []
    metadata_fields = meta_regex.findall(line)
    for key, value in metadata_fields:
        keys_for_column_headers.append(key)
    return keys_for_column_headers


def get_header_names_from_meta_data(S24file):
    key_list_for_header = []
    for line in S24file:
        try:
            line = line.decode("utf-8").strip()
        except:
            line = line.strip()
        if not line:
            continue
        # when new comment starts as "<text comment"
        if line.startswith("<text comment"):            
            key_list_for_header = extract_meta_for_header(line)
            if key_list_for_header:                
                return key_list_for_header

# -----------------------------------------------------------------------------------------

def read_S24(S24file, metaFilter):
    
    attribute = ""
    meta = []
    key_value_pair_list = []
    text = ""
    lemmas = ""
    lemmacomp = ""
    pos = ""
    msd = ""
    deprel = ""
    lex = ""
    
    skipTextComment = False

    for line in S24file:
        try:
            line = line.decode("utf-8").strip()
        except:
            line = line.strip()
        if not line:
            continue

        # when new comment starts as "<text comment"
        if line.startswith("<text comment"):
            skipTextComment = False
            if len(text) > 0:
                yield attribute, meta, key_value_pair_list, text, lemmas, lemmacomp, pos, msd, deprel, lex
            
            attribute = ""
            meta = []
            text = ""
            lemmas = ""
            lemmacomp = ""
            pos = ""
            msd = ""
            deprel = ""
            lex = ""
            
            attribute, meta, key_value_pair_list = extract_meta(line, metaFilter)
            if attribute == "" and not meta:
                skipTextComment = True
            continue

        # when comment is in the end of paragraph, add \n\n in original text (as empty rows)
        if line == "</paragraph>": 
            if not skipTextComment:
                text += "\n"
                lemmas += "\n"
                lemmacomp += "\n"
                pos += "\n"
                msd += "\n"
                deprel += "\n"
                lex += "\n\n"
            continue

        # paragraph / sentence / text lines are not collected because the aim is compile original raw words (text) back
        if line.startswith("<paragraph") or line.startswith("</paragraph") or line.startswith("<sentence") or line.startswith("</sentence") or line.startswith("<!--") or line.startswith("</text"):
            continue

        # must be an actual token line
        if not skipTextComment:
            cols = line.split("\t")
            ## uudessa 2020 tiedostorakenteessa tiedot jaettu 11 tabin mukaan, esimerkki koodin alussa
            if len(cols) != 11: 
                print("Weird line, skipping...", line, file=sys.stderr)
                continue
            if cols[SPACES] == "SpaceAfter=No":
                text += cols[WORD]
                lemmas += cols[LEMMA]
                lemmacomp += cols[LEMMACOMP]
                pos += cols[POS]
                msd += cols[MSD]
                deprel += cols[DEPREL]
                lex += cols[LEX]
            else:
                text += cols[WORD]+" "
                lemmas += cols[LEMMA]+" "
                lemmacomp += cols[LEMMACOMP]+" "
                pos += cols[POS]+" "
                msd += cols[MSD]+" "
                deprel += cols[DEPREL]+" "
                lex += cols[LEX]+" "
    else:
        if len(text) > 0:
            yield attribute, meta, key_value_pair_list, text, lemmas, lemmacomp, pos, msd, deprel, lex

# -----------------------------------------------------------------------------------------

def print_S24data(zipFileHandle, vrtFile, metaFilter, author_worksheet):    
    counter = 0
    #author_worksheet = metadata_workbook.active # insert at the end (default)
    #author_worksheet.title = "HSAuthorFuck"
    #author_worksheet.title = "HSAuthorBully"
    #author_worksheet.title = "HSvcoded"
    if (zipFileHandle is None):
        openVrtFile(vrtFile, metaFilter, author_worksheet, counter)        
    else:
        openZipFile(zipFileHandle, vrtFile, metaFilter, author_worksheet, counter)        
    #dt_string = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    #filename = str.join("_", [author_worksheet.title, dt_string])
    #complete = filename + ".xlsx"
    #metadata_workbook.save(complete)


def openVrtFile(vrtFile, metaFilter, author_worksheet, counter):    
    with open(vrtFile, encoding='utf8') as infile:
        # collect attribute, meta, text
        readInputFile(infile, author_worksheet, metaFilter, counter)        

def openZipFile(zipFileHandle, vrtFile, metaFilter, author_worksheet, counter):    
    with zipFileHandle.open(vrtFile) as infile:
        # collect attribute, meta, text
        readInputFile(infile, author_worksheet, metaFilter, counter)       

# -----------------------------------------------------------------------------------------

def readInputFile(infile, author_worksheet, metaFilter, counter):
    headers = get_header_names_from_meta_data(infile)
    author_worksheet.append(headers)
    for attribute, meta, key_value_pair_list, text, lemmas, lemmacomp, pos, msd, deprel, lex in read_S24(infile, metaFilter):
        # if any/all matching with words of string list
        # testing ---------------------
        counter += 1
        # count and print search hits
        print("#_hitnumber:", counter)
        # print opened VRT file
        print("#_filename:", infile.name)
        # print metadata            
        author_worksheet.append(key_value_pair_list)
        for m in meta:
            print("#_metadata:", m)                                
        print("")
        # testing ---------------------                    
    print(author_list)

# -----------------------------------------------------------------------------------------

def main(args):
    vrt = ""
    zip = ""
    
    try:
        vrt =  args.vrtFile
    except:
        print("No vrt file given")
    try:
        zip = args.zipFile
    except:
        print("No zip file given")                
    inputRead = False

    if len(vrt) > 0:
        print("Reading vrt file...")
        # add data to excel file 
        wb = Workbook()
        print_S24data(None, args.vrtFile, args.metaFilter, wb)
        #readNewFormat(args.vrtFile)
        inputRead = True
    elif len(zip) > 0:
        if not inputRead:
            print("Reading zip file...")
            wb = Workbook()
            traverseZipfile(args.zipFile, args.metaFilter, wb)
    else:
        print("No input file given")

# -----------------------------------------------------------------------------------------

def matchYearFromFileName(filename):
    matchingString = ""
    match = re.search(r's24_(\d+)', filename)
    if match:
        matchingString = match.group(1)
        print (match.group(1))    
    return matchingString     

# -----------------------------------------------------------------------------------------
# go trough ZIP files, read 24 files and create xlsx worksheets

def traverseZipfile(zipSource, metaFilter, metadata_workbook):
    
    fileNameList = []
    author_worksheet = metadata_workbook.active # insert at the end (default)
    #author_worksheet.title = "HSAuthorFuck"
    #author_worksheet.title = "HSAuthorBully"
    author_worksheet.title = "HSvcoded"

    with zipfile.ZipFile(zipSource) as z:
        for filename in z.namelist():
            if not os.path.isdir(filename):
                # read the file
                yearFromFilename = matchYearFromFileName(filename)
                if len(yearFromFilename) > 0:
                    print(filename)
                    fileNameList.append(filename)
                    print_S24data(z, filename, metaFilter, author_worksheet)
                    print(fileNameList)
                    #with z.open(filename) as f:
                    #    for line in f:
                    #        print (line)
    dt_string = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    filename = str.join("_", [author_worksheet.title, dt_string])
    complete = filename + ".xlsx"
    metadata_workbook.save(complete)

# -------------------------------------------------------------------------------------------

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description='Suomi24 reader for open VRT file')
    #argparser.add_argument('--vrtFile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\s24_2001_Testi.vrt", help='vrt File downloaded from kielipankki')
    #argparser.add_argument('--vrtFile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\s24_2017.vrt", help='vrt File downloaded from kielipankki')
    argparser.add_argument('--zipFile', default="C:\\Users\\mhkreivi\\Desktop\\Suomi24dumpNew\\suomi24-2001-2017-vrt-v1-1.zip", help='ZIP File downloaded from kielipankki')
    #argparser.add_argument('--zipFile', default="C:\\Users\\mhkreivi\\Desktop\\Suomi24dumpNew\\suomi24-2001-2017-vrt-TEST.zip", help='ZIP File downloaded from kielipankki')    
    argparser.add_argument('--fromYear', default="2001", help='Parse comments/threads from this year onwards (default is 2001)')
    argparser.add_argument('--toYear', default="2017", help='Parse comments/threads up to this year (default is 2017)')
    argparser.add_argument('--metaFilter', default="author", help='Insert one filter from meta data ')    
    args = argparser.parse_args()
    main(args)