# AFINN based Sentiment Analysis (SA) and Hate Speech (HS) Detection

AFINN based SA and HSD models use modified version of original Afinn method.

The scripts were created and published by Merja Kreivi-Kauppinen, and are part of research work carried in University of Oulu in 2020-2023. 

The study is reported on (Master’s Thesis) research paper - Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.


## Original method and reference

Original AFINN method has been published by Nielsen - reference:

Finn Årup Nielsen, "A new ANEW: evaluation of a word list for sentiment analysis in microblogs", 
Proceedings of the ESWC2011 Workshop on 'Making Sense of Microposts': 
Big things come in small packages. Volume 718 in CEUR Workshop Proceedings: 93-98. 2011 May. 
Matthew Rowe, Milan Stankovic, Aba-Sah Dadzie, Mariann Hardey (editors)

<li>   Original version of AFINN method available at GitHub: https://github.com/fnielsen/afinn 


## Improvements, changes and modifications to the original AFINN method

### Improved new lexicons

The modified AFINN (for Finnish text samples) use newly created lexicons.

All lexicons (words, emoticons, emojis) were provided on lexicographically descending order
to enable more precise text, emoticon, symbol and emoji matching.

Text based emotion sentiment lexicons included labels for 9990 word forms.

- fin_afinn_binary_MerjasList_2023.txt
- fin_afinn_trinary_MerjasList_2023.txt
- fin_afinn_polarity_MerjasList_2023.txt
- fin_afinn_HS_binary_MerjasList_2023.txt

Emoticon sentiment lexicons included labels for 593 emoticons.
The emoticon ":D" and the corresponding emoticons and symbols written in capital letters 
is now matched as all emoticons can be found as corresponding lower cap forms
on emoticon sentiment lexicons:

- afinn_emoticon_binary_MerjasList_2023.txt
- afinn_emoticon_polarity_MerjasList_2023.txt

Emoji sentiment lexicons included labels for 613 emojis.

- afinn_emoji_binary_MerjasList_2023.txt
- afinn_emoji_trinary_MerjasList_2023.txt
- afinn_emoji_polarity_MerjasList_2023.txt


### Changes and modifications in original AFINN script

The Original AFinn class was replaced with

- AFinnEmoticons class,
- AFinnWords class, and
- AfinnEmojis class

The AFinnWords class includes small changes in script. For example, the AFinnWords class was used with 'word_boundary=True' flag to enable more precise text matching.

New flags were added to AFinnEmoticons and AFinnEmojis classes. The AFinnEmoticons and AFinnEmojis classes can be used with 'emoticons_only=True' or 'emoticons_only=True' flag to enable text sample matching with emoticons or emojis only.

- AFinnEmoticons class has 'emoticons_only' flag
- AFinnEmojis class has 'emojis only' flag
