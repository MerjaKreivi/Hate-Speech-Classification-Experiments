# read_S24_openVRT_search_emojis_lemmas_neg_pos.py
""" 
Python script to read Suomi24 data file and construct data to txt and zip files. 

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

"""

import zipfile
import argparse
import sys
import re
import ftfy

### <!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel spaces initid lex/ -->
### Corresponding to the defined data structure of UD columns -- 11 tabs
WORD, REF, LEMMA, LEMMACOMP, POS, MSD, DEPHEAD, DEPREL, SPACES, INITID, LEX = range(11) 

# DEFINE SEARCH STRING LIST --------------------------------------------

#searchForStringList = ["Sipilä", "pitä", "tappaa"]
#searchForStringList = ["🖕", "👎", "🐵"]
#searchForStringList = ["🖕", "🐵"]
searchForStringList = ["🖕"]


def fix_encoding(text):
    return ftfy.fix_text(text, uncurl_quotes=False)

# define metadata paragraphs read style
meta_regex = re.compile('([a-z_]+)="([^"]+)"', re.UNICODE)


def extract_meta(line):
    # below example of new (2020) metadata style
    # <text comment_id="0" date="2001-01-01" datetime="2001-01-01 01:30:00" author="Honda" parent_comment_id="0" quoted_comment_id="0" author_logged_in="n" nick_type="anonymous" thread_id="19455" time="01:30:00" title="Hyvää uutta vuotta kaikille Hondailijoille" topic_nums="3258,1109,6254,2" msg_type="thread_start" topic_name_leaf="Honda" topic_name_top="Ajoneuvot ja liikenne" topic_names="Ajoneuvot ja liikenne &gt; Autot &gt; Automerkit &gt; Honda" topic_names_set="|Ajoneuvot ja liikenne|Automerkit|Autot|Honda|" topic_nums_set="|1109|2|3258|6254|" topic_adultonly="n" datefrom="20010101" dateto="20010101" timefrom="013000" timeto="013000" id="19455:0" author_v1="Honda" author_name_type="user_nickname" author_nick_registered="n" author_signed_status="0" thread_start_datetime="2001-01-01 01:30:00" filename_vrt="s24_2001_01.vrt" parent_datetime="" datetime_approximated="n" empty="n" filename_orig="threads2003a.vrt" origfile_textnum="17841">
    
    attribute = ""
    meta_lines = []
    metadata_fields = meta_regex.findall(line)
    
    for key, value in metadata_fields:
        if key == "attribute":
            attribute = fix_encoding(value)
            meta_lines.append(key + " = " + attribute)
            continue
        meta_lines.append(key + " = " + value)
    return attribute, meta_lines


def read_S24(S24file):
    attribute = ""
    meta = []
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
                yield attribute, meta, text, lemmas, lemmacomp, pos, msd, deprel, lex
            
            attribute = ""
            meta = []
            text = ""
            lemmas = ""
            lemmacomp = ""
            pos = ""
            msd = ""
            deprel = ""
            lex = ""
            
            attribute, meta = extract_meta(line)
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
            yield attribute, meta, text, lemmas, lemmacomp, pos, msd, deprel, lex


def print_S24data(vrtFile):    
    counter = 0
    with open(vrtFile, encoding='utf8') as infile:
        # collect attribute, meta, text
        for attribute, meta, text, lemmas, lemmacomp, pos, msd, deprel, lex in read_S24(infile):
            # if any/all matching with words of string list
            if any(word in text for word in searchForStringList):
            # if all(word in text for word in searchForStringList):
                counter += 1
                # count and print search hits
                print("#_hitnumber:", counter)
                # print opened VRT file
                print("#_filename:", vrtFile)
                # print metadata
                for m in meta:
                    print("#_metadata:", m)
                
                print("#_comment_text:")
                print(fix_encoding(text))
                print("#_lemmas:")
                print(fix_encoding(lemmas))
                print("#_lemmacomp:")
                print(fix_encoding(lemmacomp))
                print("#_pos:")
                print(fix_encoding(pos))
                print("#_msd:")
                print(fix_encoding(msd))
                print("#_deprel:")
                print(fix_encoding(deprel))
                print("#_lex:")
                print(fix_encoding(lex))
            
                print("")


def main(args):
    vrt = ""
    try:
        vrt =  args.vrtFile
    except:
        print("No vrt file given")
    if len(vrt) > 0:
        print("Reading vrt file...")
        print_S24data(args.vrtFile)
    else:
        print("No input file given")


if __name__=="__main__":
    argparser = argparse.ArgumentParser(description='Suomi24 reader for open VRT file')
    argparser.add_argument('--vrtFile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\S24_2017.vrt", help='vrt File downloaded from kielipankki')
    args = argparser.parse_args()
    main(args)
    