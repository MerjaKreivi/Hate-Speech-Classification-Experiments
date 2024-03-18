# SentiStrength based Sentiment Analysis (SA)

SentiStrength based SA models use new and modified sentiment lists of word forms, word lemmas, emoticons, and emojis on original SentiStrength methods.

The scripts were created and published by Merja Kreivi-Kauppinen, and
scripts are part of research work carried in University of Oulu in 2020-2023.

The study is reported on (Master’s Thesis) research paper - 
Merja Kreivi-Kauppinen (2024) Signs of Paradigm Shift in Hate Speech Detection Methodology: Hate Speech Detection of Dialectal, Granular and Urban Finnish. 
University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis, 111 p.


## Original method and references

Original SentStrength methods have been published by Thewall et. all. - references:

- Thelwall, M., Buckley, K., Paltoglou, G. Cai, D., & Kappas, A. (2010). Sentiment strength detection in short informal text. Journal of the American Society for Information Science and Technology, 61(12), 2544–2558.

- Thelwall, M., Buckley, K., & Paltoglou, G. (2012). Sentiment strength detection for the social Web, Journal of the American Society for Information Science and Technology, 63(1), 163-173.

- Thelwall, M., Buckley, K., & Paltoglou, G. (2011). Sentiment in Twitter events. Journal of the American Society for Information Science and Technology, 62(2), 406-418.


The original versions of SentiStrength methods available at: 

    http://sentistrength.wlv.ac.uk/#Download



## Improvements, changes and modifications to the original SentiStrength methods

Python scripts on Jupyter Notebook -files use SentiStrength -models to classify the sentiment of each text sample (in pandas dataframe).


### Method of sentiment analysis (SA) with SentiStrength

Binary, trinary, and polarity (multilabel) sentiment classification of social media text samples with SentiStrength SA were carried on tokenized or lemmatized text samples, where words, emoticons and emojis were used to get sentiment scoring.

Emoticons and emojis were taken into account in sentiment scoring.

SA with SentiStrength was carried in three separate processes: 
- (1) binary SA, 
- (2) trinary SA, and 
- (3) (multilabel) polarity SA.

Scoring was carried for 'raw' or manually 'corrected' text samples on separate processes.

Samples were preprpcessed with two steps:

- (1) Text samples were lemmatized with experimental Finnish Voikko method designed for Spacy (Spacy version 3.5.0) using large Finnish language model 'fi_core_news_lg' the source of tokens. Text samples were further tokenized with NLTK casual tokenization method, and set to lower capitals before feeding to SentiStrength scoring process.

- (2) Emojis of text samples were changed to english word forms before SentiStrength scoring.

Results were analyzed with methods of scikit-learn library by calculating confusion matrix, and accuracy, F1, precision and recall scores for tested classifiers.


### Improved new lexicons for SentiStrength

The modified SentiStrength (for Finnish social media text samples) use new Finnish SentiStrength lexicon for sentiment classification. 

Finnish SentiStrength for classification of Finnish social media text uses lexicon which includes basic, pended, subword and lemma forms of words and their polarity labels.

All lexicons (words, emoticons, emojis) were provided on lexicographically descending order to enable more precise text, emoticon, symbol, and emoji matching.

- EmotionLookupTable - On (word based sentiment) emotion lexicon 'EmotionLookupTable.txt' each word is labeled with one sentiment label (between -5 and 5). New 'EmotionLookupTable' (for Finnish) includes 11512 word forms.

- EmoticonLookupTable - On emoticon and emoji lexicon 'EmoticonLookupTable.txt' each emoticon and emoji is labeled with one sentiment label (between -5 and 5). New 'EmoticonLookupTable' includes 527 emoticons and 613 emojis.

- IdiomLookupTable - On idiom lexicon 'IdiomLookupTable.txt' each idiom is labeled with one sentiment label (between -5 and 5). New 'IdiomLookupTable' (for Finnish) includes 353 entries.

- NegatingWordList - On negating word lexicon 'NegatingWordList.txt' each entry is labeled with one sentiment label (between -5 and 5). New 'NegatingWordList' (for Finnish) includes 37 entries.

- QuestionWords - On question words lexicon 'QuestionWords.txt' each entry is labeled with one sentiment label (between -5 and 5). New 'QuestionWords' (for Finnish) includes 19 entries.

