## Unit and integration tests for preprocessing modules

# Unit testing for functions in preprocessingTools.py
# All testing is done on lower case strings

from cranetoolbox.preprocess.preprocessTools import *


def test_remove_unicode():
    assert remove_unicode(r"bob\uff2c is \u008c my \u022c\u002c uncle\ua02dishe?") == r"bob is  my  uncleishe?"
    # Should find a way to test for the removal of \x00-type non-ASCI characters
    # assert remove_unicode(r"bobx96 is x2a my uncle x01xffis he?") == r"bob is  my uncle xffis he?"
    # assert remove_unicode(r"bobx96\uff2c is my \ufx96f2c uncle is he?") == r"bob is my \uff2c uncle is he?"


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
    # Enhancement needed: deal with ordinal numbers
    # assert replace_numbers("bob is 27 but my 2nd uncle.") == "bob is twenty-seven but my second uncle."
