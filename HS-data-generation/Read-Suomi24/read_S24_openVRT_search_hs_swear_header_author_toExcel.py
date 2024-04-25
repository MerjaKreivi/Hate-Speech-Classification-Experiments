# read_S24_openVRT_search_hs_swear_header_author_toExcel.py
# 
# Python code to construct original plain text back from Kielipankki VRT files. 
# Include metadata as '#metadata:' comment lines.
#
# Comment:
# each post treated as a separate documents, paragraph boundaries (\n\n) inside a post are included (exracted from <paragraph> tags), 
# detokenized using SpaceAfter=No, 
# but does not preserve other spacing (i.e. single new lines etc...)
# documents are not guaranteed to be in any particular order

import zipfile
import argparse
import sys
import re
import ftfy
import datetime
from datetime import datetime
from openpyxl import Workbook

### <!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel spaces initid lex/ -->
### Corresponding to the defined data structure of UD columns -- 11 tabs
WORD, REF, LEMMA, LEMMACOMP, POS, MSD, DEPHEAD, DEPREL, SPACES, INITID, LEX = range(11) 

### DEFINE SEARCH STRING LIST
#searchForStringList = ["Sipilä", "pitä", "tappaa"]
#searchForStringList = ["🖕", "👎", "🐵"]
#searchForStringList = ["🖕", "🐵"]

#searchForStringList = ["@", "!", "?", "(", "#", "&"]        # ei mitään

################# tee koodi joka huomioi sekä isot että pienet kirjaimet

#searchForStringList = ["vittu", "vttu"]
#searchForStringList = ["vit.", "wit.", "vit_", "wit_", "vit-", "wit-", "vit..", "wit..", "vit__", "wit__", "vit--", "wit--"]       # 138 paljon muita
### searchForStringList = ["vi.tu", "wi.tu", "vi_du", "wi_du", "vi..u", "wi..u", "vi__u", "wi__u", "vi--u", "wi--u"]                    #  25 
searchForStringList = ["xsara", "mantra"]                    #  MIKAN TESTI

#searchForStringList = ["vittu", "vttu"]        # runsaasti
#searchForStringList = ["Vittu", "Vttu", "VITTU", "VTTU"]            # runsaasti
#searchForStringList = ["viddu", "widdu", "wittu", "vidu", "widu", "witu", "vddu", "wddu", "wttu"]          # runsaasti
#searchForStringList = ["..ddu", "__ddu", "--ddu", ".ddu", "_ddu", "-ddu", "..ttu", "__ttu", "--ttu", ".ttu", "_ttu", "-ttu", ".idu", "_idu", "-idu", ".itu", "_itu", "-itu"]        # vähän 70
#searchForStringList = ["w.ttu", "w_ttu", "w-ttu", "w.ddu", "w_ddu", "w-ddu", "v.ddu", "v_ddu", "v-ddu", "w..u", "w__u", "w--u", "w...u", "w___u", "w---u", "w.u", "w_u", "w-u"]                         # vain yksi
#searchForStringList = ["v.ttu", "v_ttu", "v-ttu", "v..u", "v__u", "v--u", "v...u", "v___u", "v---u", "v.u", "v_u", "v-u"]       # runsaasti

#searchForStringList = ["matu", "mamu", "ähläm"]
#searchForStringList = ["hasan", "hassan", "hassam", "hasam"] # vain muutamia
#searchForStringList = ["kuole", "tapa", "tappaa", "kuol", "hirttä"] # paljon jonka seassa viha nickejä
#searchForStringList = ["idiootti", "tyhmä", "ruma", "läsk", "ryss"]
#searchForStringList = ["suvak", "nuss", "vassa", "vasuk", "homo", "lesb"]
#searchForStringList = ["persu", "perse", "perus"]

# set empty author list
author_list = []

def fix_encoding(text):
    return ftfy.fix_text(text, uncurl_quotes=False)

# define metadata paragraphs read style
meta_regex = re.compile('([a-z_]+)="([^"]+)"', re.UNICODE)


# extract metadata
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


# extract header
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


# print data out and save to excel
def print_S24data(vrtFile, metaFilter, metadata_workbook):    
    counter = 0
    # create xlsx worksheet
    author_worksheet = metadata_workbook.active # insert at the end (default)
    author_worksheet.title = "HS_author_list"
    
    with open(vrtFile, encoding='utf8') as infile:
        
        # collect attribute, meta, text
        headers = get_header_names_from_meta_data(infile)
        author_worksheet.append(headers)
        
        for attribute, meta, key_value_pair_list, text, lemmas, lemmacomp, pos, msd, deprel, lex in read_S24(infile, metaFilter):
            # if any/all matching with words of string list
            ### just testing -----------------------------
            counter += 1
            # count and print search hits
            print("#_hitnumber:", counter)
            # print opened VRT file
            print("#_filename:", vrtFile)
            # print metadata            
            author_worksheet.append(key_value_pair_list)
            for m in meta:
                print("#_metadata:", m)                                
            print("")
            ### just testing -----------------------------   
        print(author_list)

    # save xlsx worksheet
    dt_string = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    filename = str.join("_", [author_worksheet.title, dt_string])
    complete = filename + ".xlsx"
    metadata_workbook.save(complete)


def main(args):
    vrt = ""
    try:
        vrt =  args.vrtFile
    except:
        print("No vrt file given")            
    if len(vrt) > 0:
        print("Reading vrt file...")
        wb = Workbook()
        print_S24data(args.vrtFile, args.metaFilter, wb)
    else:
        print("No input file given")


if __name__=="__main__":
    argparser = argparse.ArgumentParser(description='Suomi24 reader for open VRT file')
    argparser.add_argument('--vrtFile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\s24_2001_Testi.vrt", help='vrt File downloaded from kielipankki')
    argparser.add_argument('--metaFilter', default="author", help='vrt File downloaded from kielipankki')    
    args = argparser.parse_args()
    main(args)