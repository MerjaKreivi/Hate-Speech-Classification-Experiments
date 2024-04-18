# Data Analysis for Merja's Hate Speech (HS) Datasets

<li> class / category analysis of labeled data
<li> category analysis for 'raw' HS Samples
<li> for 'original' HS dataset
<li> for 'balanced' HS Dataset
<li> BoC and BoE analysis
- bag of characters (BoC) analysis for full Merja's HS dataset
- bag of emojis (BoE) analysis for full Merja's HS dataset

## INTRODUCTION 

The scripts were created and published by Merja Kreivi-Kauppinen, and are part of research work carried in University of Oulu in 2020-2023. The study is reported on (Master’s Thesis) research paper - Merja Kreivi-Kauppinen (2024) Hate Speech Detection of Dialectal, Granular and Urban Finnish. University of Oulu, Degree Programme in Computer Science and Engineering. Master’s Thesis.


## DATA ANALYSIS

Created datasets were evaluated by sample string length analysis and label categories distribution analysis.

### BoC and BoE analysis
<li> bag of characters (BoC) analysis for full Merja's HS dataset
<li> bag of emojis (BoE) analysis for full Merja's HS dataset

Created dataset was evaluated by BoC and BoE analysis. BoC and BoE analysis was done for 'raw' HS samples.
Data samples were pre-processed with lowercasing transformation. Characters and special characters of ‘raw’ text samples were analysed by feature extraction count vectorizer of sklearn 'feature_extraction' library. Result shows all character features found in created dataset. BoC analysis revealed Bag-of-Emojis (BoE) presented in data. 


## DATASET

The dataset of collected and generated research data is not shared or published.


## Manually labeled HS dataset

Every sample in dataset were labelled manually with trinary sentiment, multilabel polarity, and binary HS subcategory. 

- SA trinary - trinary sentiment
- SA polarity - multilabel polarity sentiment
- HSbinary - binary HS

Polarity and sentiment subcategories summed up the individual components or sentiments of content. The presence or absence of HS in sample was labelled with HS binary categoriy - ‘not including hate speech’ (not HS) or ‘hate speech’ (HS). 

Data samples belonging to the HS (‘HS’) subcategory (of HSbinary main category) were manually labelled with HS related subcategorylabels of HS target, topic, form, and strength categories.

- HS target
- HS topic
- HS form, and 
- HS strength


## SA sentiment

Every sample in dataset is labelled into ‘positive’, ‘neutral’, or ‘negative’ sentiment analysis subcategory on ‘sentiment’ main category.

- trinary sentiment subcategory: ‘positive’, ‘neutral’ or ‘negative’
- binary sentiment subcategory: ‘positive’ (incl. postive and neutral) or ‘negative’


## SA polarity

Every sample in dataset is labelled into sentiment polarization main category ‘polarity’, that is used to manual labelling of an estimate of overall sentiment polarity level into one of eleven polarity subcategory between -5 and 5.

- polarity subcategory: ‘-5’, ‘-4’,‘-3’, ‘-2’, ‘-1’, ‘0’, ‘1’, ‘2’, ‘3’, ‘4’ or ‘5’


## HSbinary

On the main hate speech category ‘HSbinary’ every sample in dataset is labelled into HS subcategory - ‘HS’ or ‘not HS’ (as ‘not including hate speech’) by binary classification.

- HSbinary subcategory: ‘HS’ or ‘not HS’


## HStarget

On the HS target category ‘HStarget’, the HS sample was labeled into one HStarget subcategory.

‘HStarget’ subcategories labeled the target, object, or victim of the HS into one of five following subcategories:

- ‘person’ (individual, person or his/her closed ones), 
- (small) ‘group’, 
- (large) ‘community’,  
- ‘self-hate’ (hateful speech against him/her-self), or 
- ‘self-harm’ (violent or harmful speech against him/her-self). 
- ‘none’ (not identified or included)- In ‘none’-subcategory the target is not mentioned, or HS is presented as trolling, where clear target does not exist.


## HStopic

HS topic category ‘HStopic’ was used to label every HS sample in dataset according to content into one or several topic subcategories.

‘HStopic’ category included eighteen (18) different subcategories:
- national, ethnic, foreign, immigration, religion, politics, opinion, work, sexual, gender, women, appearance, health, status, social media, family, trolling, and other


## HSform

HS form category ‘HSform’ was used to label every HS sample in dataset according to content into one or several form, type, or style describing subcategories. 

'HSform' category included fourteen (14) different subcategories:
- threat, insult, discrimination, harassment, incitement, disinformation, targeting, joke, idiom, swearing, violence, bully, granulated, and undefined. 

The undefined subcategory is available for complex cases to smooth manual labelling process.


## HSstrength

HS strength category ‘HSstrength’ was used to label every HS sample in dataset to dimension of HS according to rising hatefulness levels,  where subcategories provide an estimate of how hateful, hostile, violent, aggressive, harassing, harmful, abusive, and intentional a sample content is. 

– ‘0’, ‘1’, ‘2’, ‘3’, ‘4’, or ‘5’

- '1' - mild (lievä)
- '2' - weak (heikko)
- '3' - moderate (kohtalainen)
- '4' - strong (vahva)
- '5' - very strong	(erittäin vahva)

‘HSstrength’ subcategories (or HS strength levels) define how hateful or violent HS is, or how illegal HS is. 'HSstrength' level of HS sample is given according to most hateful content or feature. For example, if content includes swear words, one swear word gives strength level ‘1’, two swear words level ‘2’, and ‘3’ (or more) gives level ‘3’. If a comment includes verbal violence, such as content that includes a threat or incitement to kill, rape, or assault, strength level is ‘5’. 
