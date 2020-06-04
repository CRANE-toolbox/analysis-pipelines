# Filter, lighten and concatenate the data contained in all files from a tar.gz archive
# Read each file with a given marker string in its name in the tar.gz archive. Those files should contain one json-encoded tweet per line, a priori obtained from Twitter Streaming API
# The data is filtered by keeping only English language tweets, original (not a retweet, can be a quote), with text content
# The data is lightened by keeping only certain fields (see filterAndLightenTweet for full description). For truncated tweets, the full text is retrieved instead of the truncated version
# The tweets are saved in a single file, one json-encoded tweet per line


import json
import tarfile
import argparse
from progress.bar import Bar
from os import environ as env


def filterAndLightenTweet(fullTweetData):
    """Filter and lighten one tweet.

    :param dict fullTweetData: A json-encoded tweet, as obtained through Twitter Streaming API.
    :return: A json-encoded lightened tweet, with fields "id", "created_at", and "text".
    :rtype: dict

    """

    lightTweetData = {}
    if fullTweetData.get("lang", None) == "en":
        # If language is english
        text = fullTweetData.get("text", None)
        if text != None:
            # If contains text
            startWithRT = False
            if len(text) >= 2 and text[0:2] == "RT":
                # If manual retweet (text start with RT)
                startWithRT = True
            if fullTweetData.get("retweeted", False) == False and not startWithRT:
                # If original tweet

                # Remove unused fields
                usefulTweetKeys = ["created_at", "id", "text"]
                lightTweetData = dict((key, fullTweetData.get(key, None))
                                      for key in usefulTweetKeys)

                # If text was truncated, replace with full text
                if fullTweetData.get("truncated", False) == True:
                    extentedTweet = fullTweetData.get("extended_tweet", None)
                    if extentedTweet != None:
                        fullText = extentedTweet.get("full_text", "")
                        if len(fullText) > len(lightTweetData["text"]):
                            lightTweetData["text"] = fullText

    return lightTweetData


def combineDay(archiveName, datafileMarker):
    """Filter, lighten and save tweets from a tar.gz archive in a single file.

    :param str archiveName: Path to the archive to iterate on, using DATASET_PATH as the root.
    :param str datafileMarker: String that identifies all the data files in the archive.

    """

    # Get archive path
    archiveDirectory = env.get("DATASET_PATH")
    archivePath = archiveDirectory + "/" + archiveName

    # Get output path
    archivePrefix = archiveName[:-7]
    filteredDirectory = env.get("INTERMEDIATE_PATH")
    filteredName = filteredDirectory + "/" + archivePrefix

    # Read archive, filter and save
    incorrectCount = 0
    # Open output file
    with open(filteredName, "w") as outfile:
        # Open archive
        with tarfile.open(archivePath, "r:gz") as tar:
            # Progress bar
            nbFiles = len(tar.getmembers())
            bar = Bar('Filtering', max=nbFiles)
            # Iterate over compressed files
            for member in tar.getmembers():
                f = tar.extractfile(member)
                # Check that f is a data file
                if f is not None and datafileMarker in member.name:
                    # Iterate over lines
                    for line in f:
                        if len(line) > 2:
                            # Filter and lighten data
                            fullTweetData = {}
                            try:
                                fullTweetData = json.loads(line)
                            except json.decoder.JSONDecodeError:
                                # Some lines are corrupted, skip them, keeping count
                                incorrectCount += 1
                                continue
                            lightTweetData = filterAndLightenTweet(
                                fullTweetData)
                            if len(lightTweetData) > 0:
                                lightString = json.dumps(lightTweetData)
                                # Write to output
                                outfile.write(lightString)
                                outfile.write("\n")
                bar.next()
            bar.finish()

    print("Skipped %d incorrect lines" % incorrectCount)


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Filter, lighten and concatenate the data contained in all files from a tar.gz archive.")
    # Positional mandatory arguments
    parser.add_argument(
        "archiveName", help="Path to the archive to iterate on, using DATASET_PATH as the root.")
    parser.add_argument(
        "datafileMarker", help="String that identifies all the data files in the archive.")
    # Parse arguments
    args = parser.parse_args()
    return args


args = parseArguments()

# Run function
combineDay(args.archiveName, args.datafileMarker)
