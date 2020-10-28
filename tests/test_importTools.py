## Unit and integration tests for importTools module

# Input/output tests

import os
import pytest
from cranetoolbox.importTools.transform import process_files, TransformationOptions

# Set up data input
FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_importTools',
    )

@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_default(tmpdir, datafiles):
    # Create parameters
    opts_default = TransformationOptions("en",
                                 False,
                                 50000,
                                 None,
                                 None,
                                 None)

    # Run test for default options
    expected_output = "1,yes,date\n2,yes,date\n4,yes,date\n7,yes,date\n8,yes,date\n9,yes,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_default, output_file.strpath)
    assert line_count == 6
    assert failure_count == 12
    assert output_file.read() == expected_output


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_lang(tmpdir, datafiles):

    opts_lang = TransformationOptions("fr",
                                 False,
                                 50000,
                                 None,
                                 None,
                                 None)

    # Run test
    expected_output = "2,yes,date\n3,fr only,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_lang, output_file.strpath)
    assert line_count == 2
    assert failure_count == 1
    assert output_file.read() == expected_output


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_retweets(tmpdir, datafiles):
    opts_retweets = TransformationOptions("en",
                                 True,
                                 50000,
                                 None,
                                 None,
                                 None)

    # Run test
    expected_output = "1,yes,date\n2,yes,date\n4,yes,date\n5,retweet only,date\n6,RT retweet only,date\n7,yes,date\n8,yes,date\n9,yes,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_retweets, output_file.strpath)
    assert line_count == 8
    assert failure_count == 13
    assert output_file.read() == expected_output


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_memory(tmpdir, datafiles):
    opts_memory = TransformationOptions("en",
                                 False,
                                 2,
                                 None,
                                 None,
                                 None)

    # Run test
    expected_output = "1,yes,date\n2,yes,date\n4,yes,date\n7,yes,date\n8,yes,date\n9,yes,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_memory, output_file.strpath)
    assert line_count == 6
    assert failure_count == 12
    assert output_file.read() == expected_output



@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_field_names(tmpdir, datafiles):
    opts_field_names = TransformationOptions("en",
                                 False,
                                 50000,
                                 "fake_text",
                                 "fake_id",
                                 "fake_created_at")

    # Run test
    expected_output = "15,fail,date\n17,fail,date\n20,fail,date\n21,yes,date\n23,fail,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_field_names, output_file.strpath)
    assert line_count == 5
    assert failure_count == 13
    assert output_file.read() == expected_output


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'importTools_input.json'),
    )
def test_input_output_match_field_names_lang_retweet_memory(tmpdir, datafiles):
    opts_field_names_lang_retweet_memory = TransformationOptions("fr",
                                 True,
                                 2,
                                 "fake_text",
                                 "fake_id",
                                 "fake_created_at")

    # Run test
    expected_output = "16,fr only fail,date\n"
    output_file = tmpdir.join('output.txt')
    line_count, failure_count = process_files([str(datafiles.listdir()[0])], opts_field_names_lang_retweet_memory, output_file.strpath)
    assert line_count == 1
    assert failure_count == 2
    assert output_file.read() == expected_output
