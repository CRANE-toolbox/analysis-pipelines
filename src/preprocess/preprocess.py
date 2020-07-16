# Main preprocessing module

import argparse
import src.preprocess.preprocessTools


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
    no_unicode_tweet = preprocessTools.remove_unicode(lowercase_tweet)  # Technique 0

    if replace_or_remove_url:
        # Replace URLs
        no_link_tweet = preprocessTools.replace_url(no_unicode_tweet)  # Technique 1
    else:
        # Remove URLs
        no_link_tweet = preprocessTools.remove_url(no_unicode_tweet)

    if replace_or_remove_mentions:
        # Replace mentions by 'atUser'
        no_mention_tweet = preprocessTools.replace_at_user(no_link_tweet)  # Technique 1
    else:
        # Remove mentions
        no_mention_tweet = preprocessTools.remove_at_user(no_link_tweet)

    if remove_hashtag_or_segment:
        # Remove '#' character from hashtags
        no_hashtag_tweet = preprocessTools.remove_hashtag_in_front_of_word(
            no_mention_tweet)  # Technique 1
    else:
        # Segment hashtags
        no_hashtag_tweet = preprocessTools.replace_hashtags(no_mention_tweet)

    # Replace contractions
    # Technique 3: replaces contractions to their equivalents
    no_contraction_tweet = preprocessTools.replace_contraction(no_hashtag_tweet)

    if replace_or_remove_punctuation:
        # Replace punctuation repetition by a descriptive tag
        # Technique 5: replaces repetitions of exlamation marks with the tag "multiExclamation"
        simple_punctuation_tweet = preprocessTools.replace_multi_exclamation_mark(
            no_contraction_tweet)
        # Technique 5: replaces repetitions of question marks with the tag "multiQuestion"
        simple_punctuation_tweet = preprocessTools.replace_multi_question_mark(
            simple_punctuation_tweet)
        # Technique 5: replaces repetitions of stop marks with the tag "multiStop"
        simple_punctuation_tweet = preprocessTools.replace_multi_stop_mark(simple_punctuation_tweet)
        # Replace new line with space
        clean_punctuation_tweet = preprocessTools.replace_new_line(simple_punctuation_tweet)
    else:
        clean_punctuation_tweet = preprocessTools.remove_punctuation(no_contraction_tweet)

    if replace_or_remove_numbers:
        clean_tweet = preprocessTools.replace_numbers(clean_punctuation_tweet)
    else:
        clean_tweet = preprocessTools.remove_numbers(clean_punctuation_tweet)

    return clean_tweet


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(description="Dataset preprocessing. Prepare the text of each tweet for analysis and count the number of tweets per day.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_path", help="Path to the folder containing the dataset formated with the *import* module.")
    parser.add_argument(
        "output_path", help="Path to the folder where the preprocessed dataset should be saved.")

    # Optional arguments
    parser.add_argument("-pi", "--pickled_input",
                        help="The dataset to load is stored in pickled pandas DataFrame rather than CSV files.",
                        action='store_true')
    parser.add_argument("-po", "--pickled_output",
                        help="The output dataset is saved in pickled pandas DataFrame rather than CSV files.",
                        action='store_true')
    parser.add_argument("-url", "--remove_url",
                        help="Use this flag to remove URLs from the tweets instead of replacing them with 'url'",
                        action='store_false')
    parser.add_argument("-mention", "--remove_mentions",
                        help="Use this flag to remove user mentions '@userHandle' from the tweets instead of replacing them with 'atUser'",
                        action='store_false')
    parser.add_argument("-hashtag", "--segment_hashtags",
                        help="Use this flag to segment hashtags instead of simply removing the preceding '#' character. See documentation for details on the segmentation.",
                        action='store_false')
    parser.add_argument("-punct", "--remove_punctuation",
                        help="Use this flag to remove all punctuation expect hyphens, instead of replacing repeated symbols and newlines.",
                        action='store_false')
    parser.add_argument("-num", "--remove_numbers",
                        help="Use this flag to remove all numbers from the tweets instead of replacing them with their text version",
                        action='store_false')

    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_arguments()

    # Inside the loop use command:
    # preprocessing(tweet, args.remove_url, args.remove_mentions, args.segment_hashtags, args.remove_punctuation, args.remove_numbers)
