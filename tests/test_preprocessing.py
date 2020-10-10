## Unit and integration tests for preprocessing modules

# Unit testing for functions in preprocessingTools.py
# All testing is done on lower case strings

from cranetoolbox.preprocess.preprocessTools import *


def test_remove_escaped_unicode():
    assert remove_escaped_unicode("`\u2020` is a unicode char.") == "`\u2020` is a unicode char."
    assert remove_escaped_unicode("`\\u2020` is an escaped unicode char.") == "`` is an escaped unicode char."
    assert remove_escaped_unicode("`†` is an other unicode char while `\\u002c` is not.") == "`†` is an other unicode char while `` is not."
    assert remove_escaped_unicode(r"With raw strings `\u2020` is an escaped unicode.") == "With raw strings `` is an escaped unicode."


def test_remove_non_ascii():
    assert remove_non_ascii("bob \x00is \x2a my uncle \x01\xffis he?") == "bob \x00is \x2a my uncle \x01is he?"
    assert remove_non_ascii("All the english letters are ascii while `九` is not.") == "All the english letters are ascii while `` is not."
    assert remove_non_ascii("Bytes from `\x00` to `\x7f` can be represented as ascii.") == "Bytes from `\x00` to `\x7f` can be represented as ascii."
    assert remove_non_ascii("Bytes from `\x80` to `\xff` don't.") == "Bytes from `` to `` don't."
    assert remove_non_ascii("Some unicode chars, like `\u0031`, are ascii compatible.") == "Some unicode chars, like `\u0031`, are ascii compatible."
    assert remove_non_ascii("Others, like `\u2020`, don't.") == "Others, like ``, don't."


def test_replace_url():
    assert replace_url(
        "bob www.bobismyuncle.totis myhttps://myuncle#isthatrue.dude #uncle http://www.bob.fr") == "bob url myurl #uncle url"


def test_remove_url():
    assert remove_url(
        "bob www.bobismyuncle.totis myhttps://myuncle#isthatrue.dude #uncle http://www.bob.fr") == "bob  my #uncle "


def test_replace_at_user():
    assert replace_at_user(
        "bob@bob is my @uncle https://myuncle@bob.fr") == "bobatUser is my atUser https://myuncleatUser.fr"


def test_remove_at_user():
    assert remove_at_user("bob@bob is my @uncle https://myuncle@bob.fr") == "bob is my  https://myuncle.fr"


def test_remove_hashtag_in_front_of_word():
    assert remove_hashtag_in_front_of_word(r"#bob ##is my#uncle") == "bob #is myuncle"


def test_replace_hashtags():
    assert replace_hashtags("#bobismyuncle, is #he not?") == "bob is my uncle, is he not?"


def test_replace_contraction():
    assert replace_contraction(
        "i won't tell you that i can't because i'm holding bob's cat & we've said we wouldn't.") == "i will not tell you that i cannot because i am holding bob's cat and we have said we would not."
    assert replace_contraction("dammit, don't do that or i'll too.") == "damn it, do not do that or I will too."
    assert replace_contraction(
        "i'd come, but it ain't what it looks like.") == "i would come but it is not what it looks like."
    assert replace_contraction(
        "you won't tell him he's late because we're nice.") == "you will not tell him he is late because we are nice."


def test_replace_multi_exclamation_mark():
    assert replace_multi_exclamation_mark(
        "!!! oh!!bob! my uncle!!!!!") == " multiExclamation  oh multiExclamation bob! my uncle multiExclamation "


def test_replace_multi_question_mark():
    assert replace_multi_question_mark(
        "??? oh??bob? my uncle?????") == " multiQuestion  oh multiQuestion bob? my uncle multiQuestion "


def test_replace_multi_stop_mark():
    assert replace_multi_stop_mark("... oh..bob. my uncle.....") == " multiStop  oh multiStop bob. my uncle multiStop "


def test_replace_new_line():
    assert replace_new_line("\nbob is my\n uncle, is\n\n he?") == " bob is my  uncle, is   he?"


def test_remove_punctuation():
    assert remove_punctuation(".bob, is;:/my ?! &@-_# uncle.") == "bob ismy  - uncle"


def test_remove_numbers():
    assert remove_numbers("bob is 27 but my 2nd uncle.") == "bob is  but my nd uncle."


def test_replace_numbers():
    assert replace_numbers("bob is 27.") == "bob is twenty-seven."
    assert replace_numbers("bob is 27 but my 2nd uncle.") == "bob is twenty-seven but my second uncle."
    assert replace_numbers("today is the 31st of december.") == "today is the thirty-first of december."
    assert replace_numbers("it is the 1st time i have been here.") == "it is the first time i have been here."
    assert replace_numbers("i am born on september 29th and i am 29 years old.") == "i am born on september twenty-ninth and i am twenty-nine years old."
    assert replace_numbers("bob finished 3rd in the 2010 edition of the new york marathon.") == "bob finished third in the two thousand and ten edition of the new york marathon."
