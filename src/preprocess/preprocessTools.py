# Preprocessing functions
# Adapted from https://github.com/Deffro/text-preprocessing-techniques

import re
import wordsegment
from num2words import num2words


def remove_unicode(text):
    """ Removes unicode strings like "\u002c" and "x96" """
    text = re.sub(r'(\\u[0-9A-Fa-f]+)', r'', text)
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text


def replace_url(text):
    """ Replaces url address with "url" """
    text = re.sub(r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', 'url', text)
    return text


def remove_url(text):
    """ Removes url address"""
    text = re.sub(r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', '', text)
    return text


def replace_at_user(text):
    """ Replaces "@user" with "atUser" """
    text = re.sub(r'@[^\s]+', 'atUser', text)
    return text


def remove_at_user(text):
    """ Removes "@user" """
    text = re.sub(r'@[^\s]+', '', text)
    return text


def remove_hashtag_in_front_of_word(text):
    """ Removes hastag in front of a word """
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def segment_hashtag(text):
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = text[1:]
    segments = wordsegment.segment(text)
    if len(segments) > 1:
        text = " ".join(segments)
    return text


def replace_hashtags(text):
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = re.sub(r'#([^\s]+)', segment_hashtag(r'\1'), text)
    return text


def replace_contraction(text):
    """ Replaces contractions from a string to their equivalents """
    contraction_patterns = [(r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'), (r'(\w+)\'ll', r'\g<1> will'), (r'(\w+)n\'t', r'\g<1> not'),
                            (r'(\w+)\'ve', r'\g<1> have'), (r'(\w+)\'s', r'\g<1> is'), (r'(\w+)\'re', r'\g<1> are'), (r'(\w+)\'d', r'\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'), (r'wont', 'will not')]
    patterns = [(re.compile(regex), repl)
                for (regex, repl) in contraction_patterns]
    for (pattern, repl) in patterns:
        (text, count) = re.subn(pattern, repl, text)
    return text


def replace_multi_exclamation_mark(text):
    """ Replaces repetitions of exlamation marks """
    text = re.sub(r"(\!)\1+", ' multiExclamation ', text)
    return text


def replace_multi_question_mark(text):
    """ Replaces repetitions of question marks """
    text = re.sub(r"(\?)\1+", ' multiQuestion ', text)
    return text


def replace_multi_stop_mark(text):
    """ Replaces repetitions of stop marks """
    text = re.sub(r"(\.)\1+", ' multiStop ', text)
    return text


def replace_new_line(text):
    """ Replaces new lines with spaces """
    text = re.sub(r"\n", " ", text)
    return text


def remove_punctuation(text):
    """ Removes punctuation symbols, except hyphens"""
    text = re.sub(r"[^\w\s-]|_", "", text)
    return text


def remove_numbers(text):
    """ Removes integers """
    text = ''.join([i for i in text if not i.isdigit()])
    return text


def replace_numbers(text):
    """Replaces numbers with their text version"""
    text = re.sub(r"(\d+)", lambda x: num2words(int(x.group(0))), text)
    return text
