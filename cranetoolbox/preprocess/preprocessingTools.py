# Preprocessing functions
# Adapted from https://github.com/Deffro/text-preprocessing-techniques#0-remove-unicode-strings-and-noise


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
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'url', text)
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def replace_at_user(text):
    """ Replaces "@user" with "atUser" """
    text = re.sub('@[^\s]+', 'atUser', text)
    return text


def remove_hashtag_in_front_of_word(text):
    """ Removes hastag in front of a word """
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def remove_numbers(text):
    """ Removes integers """
    text = ''.join([i for i in text if not i.isdigit()])
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


def replace_contraction(text):
    """ Replaces contractions from a string to their equivalents """
    contraction_patterns = [(r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'), (r'(\w+)\'ll', '\g<1> will'), (r'(\w+)n\'t', '\g<1> not'),
                            (r'(\w+)\'ve', '\g<1> have'), (r'(\w+)\'s', '\g<1> is'), (r'(\w+)\'re', '\g<1> are'), (r'(\w+)\'d', '\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'), (r'wont', 'will not')]
    patterns = [(re.compile(regex), repl)
                for (regex, repl) in contraction_patterns]
    for (pattern, repl) in patterns:
        (text, count) = re.subn(pattern, repl, text)
    return text


def replace_new_line(text):
    """ Replaces new lines with spaces """
    text = re.sub(r"\n", " ", text)
    return text


def remove_punctuation(text):
    """ Removes punctuation symbols by a space, except hyphens"""
    text = re.sub(r"[^\w\s-]", "", text)
    return text


def remove_url(text):
    """ Removes url address"""
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text)
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def remove_at_user(text):
    """ Removes "@user" """
    text = re.sub('@[^\s]+', '', text)
    return text


def replace_numbers(text):
    """Replaces numbers with their text version"""
    text = re.sub(r"(\d+)", lambda x: num2words(int(x.group(0))), text)
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


def preprocessing(tweet, replace_or_remove_url, replace_or_remove_mentions, remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers):
    """Preprocess the text content of a tweet for analysis.

    :param tweet: Text content of a tweet.
    :type tweet: str
    :param replace_or_remove_url: True to replace URLs, False to remove them.
    :type replace_or_remove_url: bool
    :param replace_or_remove_mentions: True to replace mentions, False to remove them.
    :type replace_or_remove_mentions: bool
    :param remove_hashtag_or_segment: True to remove '#' in front of hashtags, False to segment hashtags.
    :type remove_hashtag_or_segment: bool
    :param replace_or_remove_punctuation: True to replace multiple punctuation, False to remove all punctuation.
    :type replace_or_remove_punctuation: bool
    :param replace_or_remove_numbers: True to replace numbers by their text version, False to remove them.
    :type replace_or_remove_numbers: bool
    :return: The clean version of the text.
    :rtype: str

    """

    # Lowercase
    lowercase_tweet = tweet.lower()

    # Remove unicode noise
    no_unicode_tweet = remove_unicode(lowercase_tweet)  # Technique 0

    if replace_or_remove_url:
        # Replace URLs
        no_link_tweet = replace_url(no_unicode_tweet)  # Technique 1
    else:
        # Remove URLs
        no_link_tweet = remove_url(no_unicode_tweet)

    if replace_or_remove_mentions:
        # Replace mentions by 'atUser'
        no_mention_tweet = replace_at_user(no_link_tweet)  # Technique 1
    else:
        # Remove mentions
        no_mention_tweet = remove_at_user(no_link_tweet)

    if remove_hashtag_or_segment:
        # Remove '#' character from hashtags
        no_hashtag_tweet = remove_hashtag_in_front_of_word(
            no_mention_tweet)  # Technique 1
    else:
        # Segment hashtags
        no_hashtag_tweet = replace_hashtags(no_mention_tweet)

    # Replace contractions
    # Technique 3: replaces contractions to their equivalents
    no_contraction_tweet = replace_contraction(no_hashtag_tweet)

    if replace_or_remove_punctuation:
        # Replace punctuation repetition by a descriptive tag
        # Technique 5: replaces repetitions of exlamation marks with the tag "multiExclamation"
        simple_punctuation_tweet = replace_multi_exclamation_mark(
            no_contraction_tweet)
        # Technique 5: replaces repetitions of question marks with the tag "multiQuestion"
        simple_punctuation_tweet = replace_multi_question_mark(
            simple_punctuation_tweet)
        # Technique 5: replaces repetitions of stop marks with the tag "multiStop"
        simple_punctuation_tweet = replace_multi_stop_mark(simple_punctuation_tweet)
        # Replace new line with space
        clean_punctuation_tweet = replace_new_line(simple_punctuation_tweet)
    else:
        clean_punctuation_tweet = remove_punctuation(no_contraction_tweet)

    if replace_or_remove_numbers:
        clean_tweet = replace_numbers(clean_punctuation_tweet)
    else:
        clean_tweet = remove_numbers(clean_punctuation_tweet)

    return clean_tweet
