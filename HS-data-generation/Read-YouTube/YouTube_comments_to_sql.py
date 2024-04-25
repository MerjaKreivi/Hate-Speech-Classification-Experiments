# Collect YouTube comments
# created 6.10.2019 - checked 25.4.2024 - by Merja Kreivi-Kauppinen
# YouTube_comments_to_sql.py
# in json and python
"""
Python script to read publicly available YouTube open data files
and construct data to SQL or xlsx files. 

The script was used on the research work reported on research paper:
Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master Thesis.

Introduction
 * Search and collect of original plain text back from YouTube API files
 * Each post treated as a separate documents
 * Documents are not guaranteed to be in any particular order
 * Collect data as comment lines: 
   - snippet,
   - topLevelComment,
   - snippet, and
   - original text as 'textOriginal'

Script needs YouTube developer keys
 * private developer keys not provided on script
 * code instead of key - 'abcdefghijklmnopqrstuvxyzåäö0123456789'
 * change code above to your own developer keys

Script creates print out:
 * videos
 * video ids
 * HTTP error messages
 * the amount of HTTP error messages
 * SQL checking and testing

Script saves to SQL databse:
 * the table name of YouTube results
 * textual comments

Please check in this code (before use or run) 
 - python search.py / --q = surfing / --max-results = 10 / totalResults

"""
# --------------  Import python libraries ------------------

import re, sys, os
import argparse
import json
import string
import math

import sqlite3
from sqlite3 import Error

from googleapiclient import discovery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ------------------- YouTube Search -------------------------

# NOTE: To use the sample, you must provide a developer key obtained in the Google APIs Console. 
# Search for DEVELOPER_KEY in this code to find the correct place to provide that key.
# Please ensure that you have enabled the YouTube Data API for your project from your Google account.

DEVELOPER_KEY = 'abcdefghijklmnopqrstuvxyzåäö0123456789'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# -------------------------------------------------------------
# list of query keywords or keystrings (or keysymbols) as search items

# Query_Items = [QueryItems]
# Query_Items = 'Donald Trump', 'funny puppy', 'Greta Thunberg', 'Keanu Reeves', 'Trump impeachment', 'cute kitten'
Query_Items = "Tytöt tykkää"

# -------------------------------------------------------------

video_ids = []
collected_comments = []
comment_count = 0

#dkey = Accessories_and_keys.DEVELOPER_KEY
#print(dkey)

# This code collects only ids and snippets of videos 
# (as chennels and playlists didn't include any suitable information for us)

def youtube_search(searchItem, maxResults):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified query term (at the end of the code).
    search_response = youtube.search().list(q=searchItem, part='id,snippet', maxResults=maxResults).execute()

# maxResults, unsigned integer, specifies the maximum number of items that should be returned in the result set.
# Note: This parameter is not supported for use in conjunction with the id parameter. 
# Acceptable values are 1 to 100, inclusive. The default value is 20.

# textFormat, string, indicates whether the API should return comments formatted as HTML or as plain text. 
# The default value is html. Acceptable values are:
# html – Returns the comments in HTML format. This is the default value.
# plainText – Returns the comments in plain text format.

    videos = []     #  channels = []  #  playlists = []

    # Add each result to the appropriate list, and then display the lists of matching videos. (channels, and playlists)
    
#print(str(search_response.get('pageInfo')), '\n\n')
#print(search_response)
    
    info = search_response.get('pageInfo', [])
    total = info.get('totalResults')
    print(total)
    for search_result in search_response.get("items", []):
        if search_result['id']['kind'] == 'youtube#video':
              videos.append('%s' % (search_result['snippet']['title']))

    # search for videoId
    info = search_response.get('items', [])
    
    for search_result in search_response.get("items", []):
        video_ids.append('%s' % (search_result['id']['videoId']))

    print ('Videos:\n', '\n'.join(videos), '\n')
    print ('Video ids:\n', '\n'.join(video_ids), '\n')
         #   print ('Channels:\n', '\n'.join(channels), '\n')
         #   print ('Playlists:\n', '\n'.join(playlists), '\n')

def comments_search(videoid, maxResults):
    youtubeComments = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    comments_response = youtubeComments.commentThreads().list(videoId=videoid, part='id, snippet', maxResults=maxResults).execute()

    #print ('Comments search raw data:\n', (comments_response))

    comments_items = comments_response.get("items", [])
    
    #print (comments_items)

    for comment_item in comments_response.get("items", []):        
        collected_comments.append('%s' % (comment_item['snippet']['topLevelComment']['snippet']['textOriginal']))            

# ----------------------------------------------------------------------
# provide error message if search did not provide result(s)
#  - usually because comments are blocked on video
#  - maxResults between 1 -100

HTTP_error = []

# provide error message if search did not provide result(s)
# on youtube docs
for youtube_doc in Query_Items:
    try:
        maxResults = 10
        youtube_search(youtube_doc, maxResults)

    except HttpError as e:
        #print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
        HTTP_error.append('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

# provide error message if search did not provide result(s)
# on video ids
for vid in video_ids:
    try:
        maxResults = 10
        comments_search(vid, maxResults)

    except HttpError as e:
        #print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
        HTTP_error.append('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))


#------------------- check HTTP error messages --------------------------
# print HTTP error messages
print('\nHTTP error messages:', '\n')
print(HTTP_error)
print('\nAmount of HTTP error messages: ', len(HTTP_error), '\n')

#------------------- check collected comments ---------------------------
# print collected comments
print('\nCollected comments:', '\n')
print(collected_comments)
print('\nAmount of Collected Comments: ', len(collected_comments), '\n')


# ------------------------------------------------------------------------
# --------- Create SQL database and table, and SQL testing ---------------
# --------- Open SQLite connection and create table ----------------------

# create or connect, and open database
conn = sqlite3.connect('new_database_files.db')

print('Opened database successfully')

c = conn.cursor()

# create or connect, and open table
newTable = """CREATE TABLE IF NOT EXISTS YouTubeTableV1
                    (COMMENT TEXT)"""

conn.execute(newTable)
conn.commit()
print("SQL table created successfully")

conn.close()

# ---------- Execute list to SQL as rows ----------------------------------

conn = sqlite3.connect('new_database_files.db')
print("\nOpened database successfully")

c = conn.cursor()

# define list as items
def insert_list_contents_into_db(list):
    for item in list:
        insert_string_into_db(item)
    
# execute list of items to SQL as separate rows
def insert_string_into_db(input_row):
    c.execute("INSERT INTO YouTubeTableV1"\
                " (COMMENT) VALUES"\
                " (?)", (input_row,)) 

insert_list_contents_into_db(collected_comments)
conn.commit()

print("SQL values transferd successfully")
conn.close()

# -- Connect, open, read, and print out new created database ---------------
# ----------- Print SQL table as rows  -------------------------------------

conn = sqlite3.connect('new_database_files.db')
print('\nOpened SQL database successfully')
c = conn.cursor()

print('\nPrint SQL table as rows\n')

def sql_fetch(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM YouTubeTableV1')
    rows = c.fetchall()
    for row in rows:
        print(row)
sql_fetch(conn)

print("\nSQL table printed successfully\n")

conn.close()
