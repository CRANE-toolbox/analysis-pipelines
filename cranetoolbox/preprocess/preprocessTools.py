# Preprocessing functions
# Adapted from https://github.com/Deffro/text-preprocessing-techniques

import re

import wordsegment
from num2words import num2words


def remove_unicode(text: str) -> str:
    """ Removes unicode strings like "\u002c" and "x96" """
    text = re.sub(r'(\\u[0-9A-Fa-f]+)', r'', text)
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text


def replace_url(text: str) -> str:
    """ Replaces url address with "url" """
    text = re.sub(r'((http|ftp|https):\/\/)?(w{3}\.)?[\w\-\@?^=%&amp;/~\+#]+\.\w+', 'url', text)
    return text


def remove_url(text: str) -> str:
    """ Removes url address"""
    text = re.sub(r'((http|ftp|https):\/\/)?(w{3}\.)?[\w\-\@?^=%&amp;/~\+#]+\.\w+', '', text)
    return text


def replace_at_user(text: str) -> str:
    """ Replaces "@user" with "atUser" """
    text = re.sub(r'@[\w]+', 'atUser', text)
    return text


def remove_at_user(text: str) -> str:
    """ Removes "@user" """
    text = re.sub(r'@[\w]+', '', text)
    return text


def remove_hashtag_in_front_of_word(text: str) -> str:
    """ Removes hastag in front of a word """
    text = re.sub(r'#(\w+)', r'\1', text)
    return text


def segment_hashtag(text: str) -> str:
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = text[1:]
    wordsegment.load()
    segments = wordsegment.segment(text)
    if len(segments) > 1:
        text = " ".join(segments)
    return text


def replace_hashtags(text: str) -> str:
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = re.sub(r'#(\w+)', lambda x: segment_hashtag(x.group()), text)
    return text


def replace_contraction(text: str) -> str:
    """ Replaces contractions from a string to their equivalents """
    contraction_patterns = [(r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'),
                            (r'(\w+)\'ll', r'\g<1> will'), (r'(\w+)n\'t', r'\g<1> not'),
                            (r'(\w+)\'ve', r'\g<1> have'), (r'(\w+)\'s', r'\g<1> is'), (r'(\w+)\'re', r'\g<1> are'),
                            (r'(\w+)\'d', r'\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'),
                            (r'wont', 'will not')]
    patterns = [(re.compile(regex), repl)
                for (regex, repl) in contraction_patterns]
    for (pattern, repl) in patterns:
        (text, count) = re.subn(pattern, repl, text)
    return text


def replace_multi_exclamation_mark(text: str) -> str:
    """ Replaces repetitions of exlamation marks """
    text = re.sub(r"(\!)\1+", ' multiExclamation ', text)
    return text


def replace_multi_question_mark(text: str) -> str:
    """ Replaces repetitions of question marks """
    text = re.sub(r"(\?)\1+", ' multiQuestion ', text)
    return text


def replace_multi_stop_mark(text: str) -> str:
    """ Replaces repetitions of stop marks """
    text = re.sub(r"(\.)\1+", ' multiStop ', text)
    return text


def replace_new_line(text: str) -> str:
    """ Replaces new lines with spaces """
    text = re.sub(r"\n", " ", text)
    return text


def remove_punctuation(text: str) -> str:
    """ Removes punctuation symbols, except hyphens"""
    text = re.sub(r"[^\w\s-]|_", "", text)
    return text


def remove_numbers(text: str) -> str:
    """ Removes integers """
    text = ''.join([i for i in text if not i.isdigit()])
    return text


def replace_numbers(text: str) -> str:
    """Replaces numbers with their text version"""
    text = re.sub(r"(\d+)", lambda x: num2words(int(x.group(0))), text)
    return text
