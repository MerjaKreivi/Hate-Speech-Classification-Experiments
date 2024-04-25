# read_s24_TESTING.py
""" 
Python script to read Suomi24 data file and construct data to txt and zip files. 

The script was used on the research work reported on research paper:
Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.

Introduction
 * Try to construct original plain text back from Kielipankki VRT files.
 * Include metadata as '###C:' comment lines
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

# corresponding UD columns 
# note - old format
# FORM, LEMMA, UPOS, FEATS, ID, HEAD, DEPREL, MISC, _ = range(9) 

### <!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel spaces initid lex/ -->
### Corresponds to the structure defined - note - new format
### corresponding UD columns
WORD, REF, LEMMA, LEMMACOMP, UPOS, MSD, DEPHEAD, DEPREL, SPACES, INITID, LEX = range(11)

# string list for search
negativeStringList = ["Sipilä", "pitä", "tappaa"]


def fix_encoding(text):
    return ftfy.fix_text(text, uncurl_quotes=False)


# define metadata paragraphs read style
meta_regex = re.compile('([a-z]+)="([^"]+)"', re.UNICODE)


# extract and collect metadata lines or cells
def extract_meta(line, fromYear, toYear):
    # data example below
    # <text comment="1520" date="2001-06-27" datetime="2001-06-27 13:51:00" nick="pois pois" parent="1456" quote="1519" signed="0" thread="173" time="13:51:00" title="taxiautoilijan keskisormi" topics="3220,10,2" type="comment">

    title = ""
    meta_lines = []
    metadata_fields = meta_regex.findall(line)
    validTime = False

    for key, value in metadata_fields:
        if key == "date":
            dateYMD = value.split('-')
            try:
                if int(dateYMD[0]) >= fromYear and int(dateYMD[0]) <= toYear:
                    validTime = True
                    break
            except:
                print("Invalid date, miving on...")
    if validTime:
        for key, value in metadata_fields:
            if key == "title":
                title = fix_encoding(value)
                meta_lines.append(key + " = " + title)
                continue
            meta_lines.append(key + " = " + value)
        
        #if key == "title":
        #    title = fix_encoding(value)
        #    meta_lines.append(key + " = " + title)
        #    continue
        #meta_lines.append(key + " = " + value)

    return title, meta_lines


def read_s24(f, fromYear, toYear):
    meta = []
    text = ""
    title = ""

    skipTextComment = False

    for line in f:
        
        try:
            line=line.decode("utf-8").strip()
        except:
            #line = line.encode('latin1').decode('cp1252')
            line=line.strip()

        if not line:
            continue
        if line.startswith("<text comment"): # new post starts
            skipTextComment = False
            if len(text) > 0:
                yield title, meta, text
            meta = []
            text = ""
            title = ""
            title, meta = extract_meta(line, fromYear, toYear)
            if title == "" and not meta:
                skipTextComment = True
            continue
        if line == "</paragraph>": # end of paragraph, means \n\n in original text
            if not skipTextComment:
                text += "\n\n"
            continue
        if line.startswith("<paragraph") or line.startswith("</paragraph") or line.startswith("<sentence") or line.startswith("</sentence") or line.startswith("<!--") or line.startswith("</text"):
            # these I don't care because I want to compile original raw text back
            continue
        # must be an actual token line
        # if challenges in data structure, skip one data point
        if not skipTextComment:
            cols = line.split("\t")
            ##if len(cols) != 9: vanhassa rakenteessa oli jaettu 9 tabin mukaan
            if len(cols) != 11: ## uudessa rakenteessa 11 tabin mukaan
                print("Weird line, skipping...", line, file=sys.stderr)
                continue
            if cols[SPACES] == "SpaceAfter=No":
                text += cols[WORD]
            else:
                text += cols[WORD]+" "

    else:
        if len(text) > 0:
            yield title, meta, text


def matchYearFromFileName(filename):
    matchingString = ""
    
    match = re.search(r's24_(\d+)', filename)
    if match:
        matchingString = match.group(1)
        print (match.group(1))

    match = re.search(r'comments(\d+)', filename)
    if match:
        matchingString = match.group(1)
        print (match.group(1))

    match = re.search(r'threads(\d+)', filename)
    if match:
        matchingString = match.group(1)
        print (match.group(1))

    return matchingString        


def matchYearToArguments(yearFromFileName, fromYear, toYear):
    returnValue = False
    if int(yearFromFileName) >= fromYear and int(yearFromFileName) <= toYear:
        returnValue  = True
    return returnValue


def readNewFormat(vrtFile):    
    fromYear = 0
    toYear = 0
    try:
        fromYear = int(args.fromYear)
    except:
        print("Invalid from Year param given : " + args.fromYear + " : Default to 2010")
    try:
        toYear = int(args.toYear)
    except:
        print("Invalid to Year param given : " + args.toYear + " : Default to 2010")    
    
    counter = 0

    with open(vrtFile, encoding='utf8') as infile:
        for title, meta, text in read_s24(infile, fromYear, toYear):
            # if any(word in text for word in negativeStringList):
            if all(word in text for word in negativeStringList):
                counter += 1
                print("###C: doc_id =", counter)
                print("###C: filename =", vrtFile)
                for m in meta:
                    print("###C:", m)
                print(fix_encoding(text))
                print("")


def main(args):
    vrt = ""
    zip = ""

    try:
        vrt =  args.vrtFile
    except:
        print("No vrt file given")
    try:
        zip = args.zipfile
    except:
        print("No zip file given")                
    inputRead = False

    if len(vrt) > 0:
        print("Reading vrt file...")
        readNewFormat(args.vrtFile)
        inputRead = True
    elif len(zip) > 0:
        if not inputRead:
            print("Reading zip file...")
            readZipFile(args.zipfile)
    else:
        print("No input file given")


def readZipFile(zipSource):
    zip_=zipfile.ZipFile(zipSource)
    fromYear = 0
    toYear = 0
    try:
        fromYear = int(args.fromYear)
    except:
        print("Invalid from Year param given : " + args.fromYear + " : Default to 2010")
    try:
        toYear = int(args.toYear)
    except:
        print("Invalid to Year param given : " + args.toYear + " : Default to 2010")    
    fnames = zip_.namelist()
    counter = 0
    for fname in fnames:
        print(fname, file=sys.stderr)
        yearFromFilename = matchYearFromFileName(fname)
        if len(yearFromFilename) > 0:
            if matchYearToArguments(yearFromFilename, fromYear, toYear):
                with zip_.open(fname) as f:
                    for title, meta, text in read_s24(f, fromYear, toYear):
                        # if any search string found, do print out defind items
                        if any(word in text for word in negativeStringList):
                            counter += 1
                            print("###C: doc_id =", counter)
                            print("###C: filename =", fname)
                            for m in meta:
                                print("###C:", m)
                            print(fix_encoding(text))
                            print("")
            else:
                print("Skipping file : " + fname)
                continue
        else:
            print("Skipping file : " + fname)
            continue

     
if __name__=="__main__":

    argparser = argparse.ArgumentParser(description='Suomi24 VRT reader')
    #argparser.add_argument('--zipfile', default="C:\\users\\MerjaKK\\Downloads\\testing_suomi24_comments2015.zip", help='zipfile downloaded from kielipankki')
    #argparser.add_argument('--zipfile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\testing_suomi24_comments2001.zip", help='zipfile downloaded from kielipankki')
    argparser.add_argument('--vrtFile', default="C:\\Users\\mhkreivi\\Desktop\\s24_testi\\s24_2017.vrt", help='VRT file downloaded from kielipankki')
    argparser.add_argument('--fromYear', default="2000", help='Parse comments/threads from this year onwards (default is 2010)')
    argparser.add_argument('--toYear', default="2017", help='Parse comments/threads up to this year (default is 2017)')
    args = argparser.parse_args()

    main(args)