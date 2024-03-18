# Modified version of original Afinn method

"""Base for AFINN sentiment analysis."""

from __future__ import absolute_import, division, print_function

"""
# ------------------------------------------------------------------------------------------------

This script was created and published by Merja Kreivi-Kauppinen.
This script is part of research work carried in University of Oulu
in 2020-2023.

Topic of research work and thesis:
'Signs of Paradigm Shift in Hate Speech Detection Methodology: 
Hate Speech Detection of Dialectal, Granular and Urban Finnish'

Original version of Afinn method available at GitHub: https://github.com/fnielsen/afinn 

Reference:
Finn Årup Nielsen, "A new ANEW: evaluation of a word list for sentiment analysis in microblogs", 
Proceedings of the ESWC2011 Workshop on 'Making Sense of Microposts': 
Big things come in small packages. Volume 718 in CEUR Workshop Proceedings: 93-98. 2011 May. 
Matthew Rowe, Milan Stankovic, Aba-Sah Dadzie, Mariann Hardey (editors)

# ------------------------------------------------------------------------------------------------

Improvements and changes to the original afinn method:

All lexicons (words, emoticons, emojis) were provided on lexicographically descending order
to enable more precise text, emoticon, symbol and emoji matching.

Text based emotion sentiment lexicons included labels for 9990 word forms.
    - fin_afinn_HS_binary_MerjasList_2023.txt
    - fin_afinn_trinary_MerjasList_2023.txt
    - fin_afinn_polarity_MerjasList_2023.txt

Emoticon sentiment lexicons included labels for 593 emoticons.
The emoticon ":D" and the corresponding emoticons and symbols written in capital letters 
is now matched as all emoticons can be found as corresponding lower cap forms
on emoticon sentiment lexicons:
    - afinn_emoticon_binary_MerjasList_2023.txt
    - afinn_emoticon_polarity_MerjasList_2023.txt

Emoji sentiment lexicons included labels for 613 emojis.
    - afinn_emoji_polarity_MerjasList_2023.txt
    - afinn_emoji_binary_MerjasList_2023.txt

Changes in original script.
The Original AFinn class was replacced with
    - AFinnEmoticons class,
    - AFinnWords class, and
    - AfinnEmojis class

The AFinnWords class was used with 'word_boundary=True' flag to enable more precise text matching.
The AFinnWords class includes small changes in script.

New flags were added to AFinnEmoticons and AFinnEmojos classes.
The AFinnEmoticons and AFinnEmojis classes can be used with 
'emoticons_only=True' or 'emoticons_only=True' flag 
to enable text sample matching with emoticons or emojis only.
     - AFinnEmoticons class has 'emoticons_only' flag
     - AFinnEmojis class has 'emojis only' flag

# ------------------------------------------------------------------------------------------------
"""

import codecs
import re
from os.path import dirname, join

LANGUAGE_TO_FILENAME = {
    #'emoticons': 'AFINN-emoticon-8.txt',
    #'emoticons': 'afinn_emoticon_binary_MerjasList_2023.txt',
    'emoticons': 'afinn_emoticon_polarity_MerjasList_2023.txt',

    #'fin': 'AFINN-fi-165.txt',
    #'fin': 'fin_afinn_HS_binary_MerjasList_2023.txt',
    #'fin': 'fin_afinn_binary_MerjasList_2023.txt',
    #'fin': 'fin_afinn_trinary_MerjasList_2023.txt',
    'fin': 'fin_afinn_polarity_MerjasList_2023.txt',
    
    #'emojis': 'afinn_emoji_binary_merja2023.txt',
    #'emojis': 'afinn_emoji_trinary_merja2023.txt',
    'emojis': 'afinn_emoji_polarity_merja2023.txt',
    }

class AfinnException(Exception):
    """Base for exceptions raised in this module."""

    pass

class WordListReadingError(AfinnException):
    """Exception for error when reading information form data files."""

    pass

class AfinnEmoticons(object):
    """Sentiment analyzer. The text input should be in Unicode.
    """

    def __init__(self, language="en", emoticons=False, emoticons_only=False, word_boundary=True):
        """Setup dictionary from data file.
        The language parameter can be set to English (en) or Danish (da).
        Parameters
        ----------
        language : 'en' or 'da', optional
            Specify language dictionary.
        emoticons : bool, optional
            Includes emoticons in the token list
        word_boundary : bool, optional
            Use word boundary match in the regular expression.
        """

        filename = LANGUAGE_TO_FILENAME[language]
        full_filename = self.full_filename(filename)
        
        regex_words = ""
        regex_emoticons = ""        

        # Sanity check to make sure that if emoticons_only is True, then emoticons is set True
        if emoticons_only:
            if not emoticons:
                emoticons = True                

        if emoticons:
            # Words
            if not emoticons_only:
                self._dict = self.read_word_file(full_filename)
                regex_words = self.regex_from_tokens(
                    list(self._dict),
                    word_boundary=False, capture=False)            

            # Emoticons
            filename_emoticons = LANGUAGE_TO_FILENAME['emoticons']
            full_filename_emoticons = self.full_filename(filename_emoticons)
            emoticons_and_score = self.read_word_file(full_filename_emoticons)
            if not emoticons_only:
                self._dict.update(emoticons_and_score)
            else:
                self._dict = emoticons_and_score
            regex_emoticons = self.regex_from_tokens(
                list(emoticons_and_score), word_boundary=False, capture=False)

            # Combined words and emoticon regular expression
            if len(regex_words) > 0 and len(regex_emoticons) > 0:
                regex = '(' + regex_words + '|' + regex_emoticons + ')'
            elif len(regex_emoticons) > 0 and len(regex_words) == 0:
                regex = '(' + regex_emoticons + ')'
            self._setup_pattern_from_regex(regex)        
        else:
            self.setup_from_file(full_filename, word_boundary=word_boundary)

        self._word_pattern = re.compile('\w+', flags=re.UNICODE)
    
    def data_dir(self):
        """Return directory where the text files are.
        The sentiment wordlists are distributed in a subdirectory.
        This function returns the path to that subdirectory.
        Returns
        -------
        path : str
             Pathname to data files.
        Examples
        --------
        >>> afinn = Afinn()
        >>> path = afinn.data_dir()
        >>> from os.path import split
        >>> split(path)[-1]
        'data'
        """
        return join(dirname(__file__), 'data')

    def full_filename(self, filename):
        """Return filename with full with data directory.
        Prepending the path of the data directory to the filename.
        Parameters
        ----------
        filename : str
            Filename without path for data file.
        Returns
        -------
        full_filename : str
            Filename with path
        Examples
        --------
        >>> afinn = Afinn()
        >>> filename = afinn.full_filename('AFINN-111.txt')
        >>> from os.path import split
        >>> split(filename)[-1]
        'AFINN-111.txt'
        """
        return join(self.data_dir(), filename)

    def setup_from_file(self, filename, word_boundary=True):
        """Setup data from data file.
        Read the word file and setup the regular expression pattern for
        matching.
        Parameters
        ----------
        filename : str
            Full filename.
        """
        self._dict = self.read_word_file(filename)
        self._setup_pattern_from_dict(word_boundary=word_boundary)

    @staticmethod
    def read_word_file(filename):
        """Read data from tab-separated file.
        Parameters
        ----------
        filename : str
            Full filename for tab-separated data file.
        Returns
        -------
        word_dict : dict
            Dictionary with words from file
        """
        word_dict = {}
        with codecs.open(filename, encoding='UTF-8') as fid:
            for n, line in enumerate(fid):
                try:
                    word, score = line.strip().split('\t')
                except ValueError:
                    msg = 'Error in line %d of %s' % (n + 1, filename)
                    raise WordListReadingError(msg)
                word_dict[word] = int(score)
        return word_dict

    @staticmethod
    def regex_from_tokens(tokens, word_boundary=True, capture=True):
        r"""Return regular expression string from list of tokens.
        Parameters
        ----------
        tokens : List of str
            List of tokens/words to form a regex
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        capture : bool, optional
            Add capture characters
        Returns
        -------
        regex : str
            String with regular expression
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.regex_from_tokens(['good', 'bad'])
        '(\\b(?:good|bad)\\b)'
        >>> afinn.regex_from_tokens(['good', 'bad'], word_boundary=False,
        ...     capture=False)
        '(?:good|bad)'
        """
        tokens_ = tokens[:]

        # The longest tokens are first in the list
        tokens_.sort(key=lambda word: len(word), reverse=True)

        # Some tokens might contain parentheses or other problematic characters
        tokens_ = [re.escape(word) for word in tokens_]

        # Build regular expression
        regex = '(?:' + "|".join(tokens_) + ')'
        if word_boundary:
            regex = r"\b" + regex + r"\b"
        if capture:
            regex = '(' + regex + ')'

        return regex

    def _setup_pattern_from_regex(self, regex):
        """Set internal variable from regex string."""
        self._pattern = re.compile(regex, flags=re.UNICODE)

    def _setup_pattern_from_dict(self, word_boundary=True):
        """Pattern for identification of words from data files.
        Setup of regular expression pattern for matching phrases from the data
        files.
        Parameters
        ----------
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        """
        regex = self.regex_from_tokens(
            list(self._dict),
            word_boundary=word_boundary)
        self._setup_pattern_from_regex(regex)

    def find_all(self, text, clean_whitespace=True):
        """Find all tokens in a text matching the dictionary.
        Words that do not match the dictionary is not returned in the wordlist.
        The text is automatically lower-cased.
        A simple regular expression match is used.
        Parameters
        ----------
        text : str
            String with text where words are to be found.
        clean_whitespace : bool, optional
            Change multiple whitespaces to a single.
        Returns
        -------
        words : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.find_all('It is wonderful!')
        ['wonderful']
        >>> afinn = Afinn(emoticons=True)
        >>> afinn.find_all('It is wonderful :)')
        ['wonderful', ':)']
        """
        if clean_whitespace:
            text = re.sub(r"\s+", " ", text)
        words = self._pattern.findall(text.lower()) 
        return words

    def split(self, text):
        """Split a string into words.
        Parameters
        ----------
        text : str
            String with text that should be split
        Returns
        -------
        wordlist : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.split('Hello, world!')
        ['Hello', 'world']
        """
        wordlist = self._word_pattern.findall(text)
        return wordlist

    def score_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a float variable that if larger than zero indicates a
        positive sentiment and less than zero indicates negative sentiment.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        word_scores = self.scores_with_pattern(text)
        score = float(sum(word_scores))
        return score

    def scores_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a list of float variables for each matched word or
        phrase in the word list.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        scores : list of floats
            Sentiment analysis scores for text
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.scores_with_pattern('Good and bad')
        [3, -3]
        >>> afinn.scores_with_pattern('some kind of idiot')
        [0, -3]
        -------
        The emoticon ":D" is now matched as
        all emoticons can be found as corresponding lower cap forms
        on emoticon sentiment lexicon
        """
        words = self.find_all(text)
        scores = [self._dict[word] for word in words]
        return scores

    def score_with_wordlist(self, text):
        """Score text based on initial word split.
        Performs the actual sentiment analysis on a text.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        words = self.split(text)
        word_scores = (self._dict.get(word.lower(), 0.0) for word in words)
        score = float(sum(word_scores))
        return score

    score = score_with_pattern

    scores = scores_with_pattern

class AfinnWords(object):
    """Sentiment analyzer. The text input should be in Unicode.
       ----------
       Changes in flags and script. 
       
       The word boundary is used, therefore flag 
       word_boundary=True (instead of 'false') as in original afinn version.
       
       Original script is maintained in 'if' clause.
       The use of word boundary is located in 'else' clause.

    """

    def __init__(self, language="en", word_boundary=True):
        """Setup dictionary from data file.
        The language parameter can be set to English (en) or Danish (da).
        Parameters
        ----------
        language : 'en' or 'da', optional
            Specify language dictionary.
        emoticons : bool, optional
            Includes emoticons in the token list
        word_boundary : bool, optional
            Use word boundary match in the regular expression.
        """
        filename = LANGUAGE_TO_FILENAME[language]
        full_filename = self.full_filename(filename)
        # ------------------------------------------------------------------
        # changes in original method
        if not word_boundary:
            
            self._dict = self.read_word_file(full_filename)
            regex_words = self.regex_from_tokens(
                    list(self._dict),
                    word_boundary=False, capture=False) 
            regex = '(' + regex_words + ')'
            self._setup_pattern_from_regex(regex) 
        else:
            self.setup_from_file(full_filename, word_boundary=word_boundary)
        # ------------------------------------------------------------------

        self._word_pattern = re.compile('\w+', flags=re.UNICODE)
     
    def data_dir(self):
        """Return directory where the text files are.
        The sentiment wordlists are distributed in a subdirectory.
        This function returns the path to that subdirectory.
        Returns
        -------
        path : str
             Pathname to data files.
        Examples
        --------
        >>> afinn = Afinn()
        >>> path = afinn.data_dir()
        >>> from os.path import split
        >>> split(path)[-1]
        'data'
        """
        return join(dirname(__file__), 'data')

    def full_filename(self, filename):
        """Return filename with full with data directory.
        Prepending the path of the data directory to the filename.
        Parameters
        ----------
        filename : str
            Filename without path for data file.
        Returns
        -------
        full_filename : str
            Filename with path
        Examples
        --------
        >>> afinn = Afinn()
        >>> filename = afinn.full_filename('AFINN-111.txt')
        >>> from os.path import split
        >>> split(filename)[-1]
        'AFINN-111.txt'
        """
        return join(self.data_dir(), filename)

    def setup_from_file(self, filename, word_boundary=True):
        """Setup data from data file.
        Read the word file and setup the regular expression pattern for
        matching.
        Parameters
        ----------
        filename : str
            Full filename.
        """
        self._dict = self.read_word_file(filename)
        self._setup_pattern_from_dict(word_boundary=word_boundary)

    @staticmethod
    def read_word_file(filename):
        """Read data from tab-separated file.
        Parameters
        ----------
        filename : str
            Full filename for tab-separated data file.
        Returns
        -------
        word_dict : dict
            Dictionary with words from file
        """
        word_dict = {}
        with codecs.open(filename, encoding='UTF-8') as fid:
            for n, line in enumerate(fid):
                try:
                    word, score = line.strip().split('\t')
                except ValueError:
                    msg = 'Error in line %d of %s' % (n + 1, filename)
                    raise WordListReadingError(msg)
                word_dict[word] = int(score)
        return word_dict

    @staticmethod
    def regex_from_tokens(tokens, word_boundary=True, capture=True):
        r"""Return regular expression string from list of tokens.
        Parameters
        ----------
        tokens : List of str
            List of tokens/words to form a regex
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        capture : bool, optional
            Add capture characters
        Returns
        -------
        regex : str
            String with regular expression
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.regex_from_tokens(['good', 'bad'])
        '(\\b(?:good|bad)\\b)'
        >>> afinn.regex_from_tokens(['good', 'bad'], word_boundary=False,
        ...     capture=False)
        '(?:good|bad)'
        """
        tokens_ = tokens[:]

        # The longest tokens are first in the list
        tokens_.sort(key=lambda word: len(word), reverse=True)

        # Some tokens might contain parentheses or other problematic characters
        tokens_ = [re.escape(word) for word in tokens_]

        # Build regular expression
        regex = '(?:' + "|".join(tokens_) + ')'
        if word_boundary:
            regex = r"\b" + regex + r"\b"
        if capture:
            regex = '(' + regex + ')'

        return regex

    def _setup_pattern_from_regex(self, regex):
        """Set internal variable from regex string."""
        self._pattern = re.compile(regex, flags=re.UNICODE)

    def _setup_pattern_from_dict(self, word_boundary=True):
        """Pattern for identification of words from data files.
        Setup of regular expression pattern for matching phrases from the data
        files.
        Parameters
        ----------
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        """
        regex = self.regex_from_tokens(
            list(self._dict),
            word_boundary=word_boundary)
        self._setup_pattern_from_regex(regex)

    def find_all(self, text, clean_whitespace=True):
        """Find all tokens in a text matching the dictionary.
        Words that do not match the dictionary is not returned in the wordlist.
        The text is automatically lower-cased.
        A simple regular expression match is used.
        Parameters
        ----------
        text : str
            String with text where words are to be found.
        clean_whitespace : bool, optional
            Change multiple whitespaces to a single.
        Returns
        -------
        words : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.find_all('It is wonderful!')
        ['wonderful']
        >>> afinn = Afinn(emoticons=True)
        >>> afinn.find_all('It is wonderful :)')
        ['wonderful', ':)']
        """
        if clean_whitespace:
            text = re.sub(r"\s+", " ", text)
        words = self._pattern.findall(text.lower()) 
        return words

    def split(self, text):
        """Split a string into words.
        Parameters
        ----------
        text : str
            String with text that should be split
        Returns
        -------
        wordlist : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.split('Hello, world!')
        ['Hello', 'world']
        """
        wordlist = self._word_pattern.findall(text)
        return wordlist

    def score_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a float variable that if larger than zero indicates a
        positive sentiment and less than zero indicates negative sentiment.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        word_scores = self.scores_with_pattern(text)
        score = float(sum(word_scores))
        return score

    def scores_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a list of float variables for each matched word or
        phrase in the word list.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        scores : list of floats
            Sentiment analysis scores for text
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.scores_with_pattern('Good and bad')
        [3, -3]
        >>> afinn.scores_with_pattern('some kind of idiot')
        [0, -3]
        """
        # TODO: ":D" is not matched
        words = self.find_all(text)
        scores = [self._dict[word] for word in words]
        return scores

    def score_with_wordlist(self, text):
        """Score text based on initial word split.
        Performs the actual sentiment analysis on a text.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        words = self.split(text)
        word_scores = (self._dict.get(word.lower(), 0.0) for word in words)
        score = float(sum(word_scores))
        return score

    score = score_with_pattern

    scores = scores_with_pattern

class AfinnEmojis(object):
    """Sentiment analyzer. The text input should be in Unicode.
    """

    def __init__(self, language="en", emojis=False, emojis_only=False, word_boundary=True):
        """Setup dictionary from data file.
        The language parameter can be set to English (en) or Danish (da).
        Parameters
        ----------
        language : 'en' or 'da', optional
            Specify language dictionary.
        emoticons : bool, optional
            Includes emoticons in the token list
        word_boundary : bool, optional
            Use word boundary match in the regular expression.
        """

        filename = LANGUAGE_TO_FILENAME[language]
        full_filename = self.full_filename(filename)
        
        regex_words = ""
        regex_emojis = ""        

        # Sanity check to make sure that if emojis_only is True
        if emojis_only:
            if not emojis:
                emojis = True                

        if emojis:
            # Words
            if not emojis_only:
                self._dict = self.read_word_file(full_filename)
                regex_words = self.regex_from_tokens(
                    list(self._dict),
                    word_boundary=True, capture=False)            

            # Emoticons
            filename_emojis = LANGUAGE_TO_FILENAME['emojis']
            full_filename_emojis = self.full_filename(filename_emojis)
            emojis_and_score = self.read_word_file(full_filename_emojis)
            if not emojis_only:
                self._dict.update(emojis_and_score)
            else:
                self._dict = emojis_and_score
            regex_emojis = self.regex_from_tokens(
                list(emojis_and_score), word_boundary=False,
                capture=False)

            # Combined words and emoticon regular expression
            if len(regex_words) > 0 and len(regex_emojis) > 0:
                regex = '(' + regex_words + '|' + regex_emojis + ')'
            elif len(regex_emojis) > 0 and len(regex_words) == 0:
                regex = '(' + regex_emojis + ')'
            self._setup_pattern_from_regex(regex)        
        else:
            self.setup_from_file(full_filename, word_boundary=word_boundary)

        self._word_pattern = re.compile('\w+', flags=re.UNICODE)

    def data_dir(self):
        """Return directory where the text files are.
        The sentiment wordlists are distributed in a subdirectory.
        This function returns the path to that subdirectory.
        Returns
        -------
        path : str
             Pathname to data files.
        Examples
        --------
        >>> afinn = Afinn()
        >>> path = afinn.data_dir()
        >>> from os.path import split
        >>> split(path)[-1]
        'data'
        """
        return join(dirname(__file__), 'data')

    def full_filename(self, filename):
        """Return filename with full with data directory.
        Prepending the path of the data directory to the filename.
        Parameters
        ----------
        filename : str
            Filename without path for data file.
        Returns
        -------
        full_filename : str
            Filename with path
        Examples
        --------
        >>> afinn = Afinn()
        >>> filename = afinn.full_filename('AFINN-111.txt')
        >>> from os.path import split
        >>> split(filename)[-1]
        'AFINN-111.txt'
        """
        return join(self.data_dir(), filename)

    def setup_from_file(self, filename, word_boundary=True):
        """Setup data from data file.
        Read the word file and setup the regular expression pattern for
        matching.
        Parameters
        ----------
        filename : str
            Full filename.
        """
        self._dict = self.read_word_file(filename)
        self._setup_pattern_from_dict(word_boundary=word_boundary)

    @staticmethod
    def read_word_file(filename):
        """Read data from tab-separated file.
        Parameters
        ----------
        filename : str
            Full filename for tab-separated data file.
        Returns
        -------
        word_dict : dict
            Dictionary with words from file
        """
        word_dict = {}
        with codecs.open(filename, encoding='UTF-8') as fid:
            for n, line in enumerate(fid):
                try:
                    word, score = line.strip().split('\t')
                except ValueError:
                    msg = 'Error in line %d of %s' % (n + 1, filename)
                    raise WordListReadingError(msg)
                word_dict[word] = int(score)
        return word_dict

    @staticmethod
    def regex_from_tokens(tokens, word_boundary=True, capture=True):
        r"""Return regular expression string from list of tokens.
        Parameters
        ----------
        tokens : List of str
            List of tokens/words to form a regex
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        capture : bool, optional
            Add capture characters
        Returns
        -------
        regex : str
            String with regular expression
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.regex_from_tokens(['good', 'bad'])
        '(\\b(?:good|bad)\\b)'
        >>> afinn.regex_from_tokens(['good', 'bad'], word_boundary=False,
        ...     capture=False)
        '(?:good|bad)'
        """
        tokens_ = tokens[:]

        # The longest tokens are first in the list
        tokens_.sort(key=lambda word: len(word), reverse=True)

        # Some tokens might contain parentheses or other problematic characters
        tokens_ = [re.escape(word) for word in tokens_]

        # Build regular expression
        regex = '(?:' + "|".join(tokens_) + ')'
        if word_boundary:
            regex = r"\b" + regex + r"\b"
        if capture:
            regex = '(' + regex + ')'

        return regex

    def _setup_pattern_from_regex(self, regex):
        """Set internal variable from regex string."""
        self._pattern = re.compile(regex, flags=re.UNICODE)

    def _setup_pattern_from_dict(self, word_boundary=True):
        """Pattern for identification of words from data files.
        Setup of regular expression pattern for matching phrases from the data
        files.
        Parameters
        ----------
        word_boundary : bool, optional
            Add word boundary match to the regular expression
        """
        regex = self.regex_from_tokens(
            list(self._dict),
            word_boundary=word_boundary)
        self._setup_pattern_from_regex(regex)

    def find_all(self, text, clean_whitespace=True):
        """Find all tokens in a text matching the dictionary.
        Words that do not match the dictionary is not returned in the wordlist.
        The text is automatically lower-cased.
        A simple regular expression match is used.
        Parameters
        ----------
        text : str
            String with text where words are to be found.
        clean_whitespace : bool, optional
            Change multiple whitespaces to a single.
        Returns
        -------
        words : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.find_all('It is wonderful!')
        ['wonderful']
        >>> afinn = Afinn(emoticons=True)
        >>> afinn.find_all('It is wonderful :)')
        ['wonderful', ':)']
        """
        if clean_whitespace:
            text = re.sub(r"\s+", " ", text)
        words = self._pattern.findall(text.lower()) 
        return words

    def split(self, text):
        """Split a string into words.
        Parameters
        ----------
        text : str
            String with text that should be split
        Returns
        -------
        wordlist : list of str
            List of words
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.split('Hello, world!')
        ['Hello', 'world']
        """
        wordlist = self._word_pattern.findall(text)
        return wordlist

    def score_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a float variable that if larger than zero indicates a
        positive sentiment and less than zero indicates negative sentiment.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        word_scores = self.scores_with_pattern(text)
        score = float(sum(word_scores))
        return score

    def scores_with_pattern(self, text):
        """Score text based on pattern matching.
        Performs the actual sentiment analysis on a text. It uses a regular
        expression match against the word list.
        The output is a list of float variables for each matched word or
        phrase in the word list.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        scores : list of floats
            Sentiment analysis scores for text
        Examples
        --------
        >>> afinn = Afinn()
        >>> afinn.scores_with_pattern('Good and bad')
        [3, -3]
        >>> afinn.scores_with_pattern('some kind of idiot')
        [0, -3]
        """
        # TODO: ":D" is not matched
        words = self.find_all(text)
        scores = [self._dict[word] for word in words]
        return scores

    def score_with_wordlist(self, text):
        """Score text based on initial word split.
        Performs the actual sentiment analysis on a text.
        Parameters
        ----------
        text : str
            Text to be analyzed for sentiment.
        Returns
        -------
        score : float
            Sentiment analysis score for text
        """
        words = self.split(text)
        word_scores = (self._dict.get(word.lower(), 0.0) for word in words)
        score = float(sum(word_scores))
        return score

    score = score_with_pattern

    scores = scores_with_pattern

