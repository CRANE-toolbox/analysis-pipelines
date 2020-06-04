# Preprocessing functions
# Adapted from https://github.com/Deffro/text-preprocessing-techniques#0-remove-unicode-strings-and-noise


import re
import wordsegment
from num2words import num2words


def removeUnicode(text):
    """ Removes unicode strings like "\u002c" and "x96" """
    text = re.sub(r'(\\u[0-9A-Fa-f]+)', r'', text)
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text


def replaceURL(text):
    """ Replaces url address with "url" """
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'url', text)
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def replaceAtUser(text):
    """ Replaces "@user" with "atUser" """
    text = re.sub('@[^\s]+', 'atUser', text)
    return text


def removeHashtagInFrontOfWord(text):
    """ Removes hastag in front of a word """
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def removeNumbers(text):
    """ Removes integers """
    text = ''.join([i for i in text if not i.isdigit()])
    return text


def replaceMultiExclamationMark(text):
    """ Replaces repetitions of exlamation marks """
    text = re.sub(r"(\!)\1+", ' multiExclamation ', text)
    return text


def replaceMultiQuestionMark(text):
    """ Replaces repetitions of question marks """
    text = re.sub(r"(\?)\1+", ' multiQuestion ', text)
    return text


def replaceMultiStopMark(text):
    """ Replaces repetitions of stop marks """
    text = re.sub(r"(\.)\1+", ' multiStop ', text)
    return text


def replaceContraction(text):
    """ Replaces contractions from a string to their equivalents """
    contraction_patterns = [(r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'), (r'(\w+)\'ll', '\g<1> will'), (r'(\w+)n\'t', '\g<1> not'),
                            (r'(\w+)\'ve', '\g<1> have'), (r'(\w+)\'s', '\g<1> is'), (r'(\w+)\'re', '\g<1> are'), (r'(\w+)\'d', '\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'), (r'wont', 'will not')]
    patterns = [(re.compile(regex), repl)
                for (regex, repl) in contraction_patterns]
    for (pattern, repl) in patterns:
        (text, count) = re.subn(pattern, repl, text)
    return text


def replaceNewLine(text):
    """ Replaces new lines with spaces """
    text = re.sub(r"\n", " ", text)
    return text


def removePunctuation(text):
    """ Removes punctuation symbols by a space, except hyphens"""
    text = re.sub(r"[^\w\s-]", "", text)
    return text


def removeURL(text):
    """ Removes url address"""
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text)
    text = re.sub(r'#([^\s]+)', r'\1', text)
    return text


def removeAtUser(text):
    """ Removes "@user" """
    text = re.sub('@[^\s]+', '', text)
    return text


def replaceNumbers(text):
    """Replaces numbers with their text version"""
    text = re.sub(r"(\d+)", lambda x: num2words(int(x.group(0))), text)
    return text


def segmentHashtag(text):
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = text[1:]
    segments = wordsegment.segment(text)
    if len(segments) > 1:
        text = " ".join(segments)
    return text


def replaceHashtags(text):
    """ Removes hastag in front of a word and add hashtag segmentation """
    text = re.sub(r'#([^\s]+)', segmentHashtag(r'\1'), text)
    return text


def preprocessing(tweet, replaceOrRemoveUrl, replaceOrRemoveMentions, removeHashtagOrSegment, replaceOrRemovePunctuation, replaceOrRemoveNumbers):
    """Preprocess the text content of a tweet for analysis.

    :param str tweet: Text content of a tweet.
    :param bool replaceOrRemoveUrl: True to replace URLs, False to remove them.
    :param bool replaceOrRemoveMentions: True to replace mentions, False to remove them.
    :param bool removeHashtagOrSegment: True to remove '#' in front of hashtags, False to segment hashtags.
    :param bool replaceOrRemovePunctuation: True to replace multiple punctuation, False to remove all punctuation.
    :param bool replaceOrRemoveNumbers: True to replace numbers by their text version, False to remove them.
    :return: The clean version of the text.
    :rtype: str

    """

    # Lowercase
    lowercaseTweet = tweet.lower()

    # Remove unicode noise
    noUnicodeTweet = removeUnicode(lowercaseTweet)  # Technique 0

    if replaceOrRemoveUrl:
        # Replace URLs
        noLinkTweet = replaceURL(noUnicodeTweet)  # Technique 1
    else:
        # Remove URLs
        noLinkTweet = removeURL(noUnicodeTweet)

    if replaceOrRemoveMentions:
        # Replace mentions by 'atUser'
        noMentionsTweet = replaceAtUser(noLinkTweet)  # Technique 1
    else:
        # Remove mentions
        noMentionsTweet = removeAtUser(noLinkTweet)

    if removeHashtagOrSegment:
        # Remove '#' character from hashtags
        noHashtagTweet = removeHashtagInFrontOfWord(
            noMentionsTweet)  # Technique 1
    else:
        # Segment hashtags
        noHashtagTweet = replaceHashtags(noMentionsTweet)

    # Replace contractions
    # Technique 3: replaces contractions to their equivalents
    noContractionTweet = replaceContraction(noHashtagTweet)

    if replaceOrRemovePunctuation:
        # Replace punctuation repetition by a descriptive tag
        # Technique 5: replaces repetitions of exlamation marks with the tag "multiExclamation"
        simplePunctuationTweet = replaceMultiExclamationMark(
            noContractionTweet)
        # Technique 5: replaces repetitions of question marks with the tag "multiQuestion"
        simplePunctuationTweet = replaceMultiQuestionMark(
            simplePunctuationTweet)
        # Technique 5: replaces repetitions of stop marks with the tag "multiStop"
        simplePunctuationTweet = replaceMultiStopMark(simplePunctuationTweet)
        # Replace new line with space
        cleanPunctuationTweet = replaceNewLine(simplePunctuationTweet)
    else:
        cleanPunctuationTweet = removePunctuation(noContractionTweet)

    if replaceOrRemoveNumbers:
        cleanTweet = replaceNumbers(cleanPunctuationTweet)
    else:
        cleanTweet = removeNumbers(cleanPunctuationTweet)

    return cleanTweet
