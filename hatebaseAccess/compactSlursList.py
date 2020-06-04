## Fuse and clean slurs lists from various sources

import json

def compactLists(*arg):
    if len(arg) == 0:
        print("Please provide at least one .json file")
        return

    # Fuse the files
    files = list(arg)
    fullDict = {}
    for fileName in files:
        with open(fileName, 'r') as file:
            tempDict = json.load(file)
            for group, slurs in tempDict.items():
                l = fullDict.get(group, [])
                fullDict[group] = l + slurs

    # Lowercase and clean duplicates
    noDuplicateDict = {}
    for group, slurs in fullDict.items():
        lowerList = [x.lower() for x in slurs]
        noDuplicateList = list(set(lowerList))
        noDuplicateList.sort()
        noDuplicateDict[group] = noDuplicateList

    # Remove unwanted words from removedSlurs.json
    cleanDict = {}
    with open("removedSlurs.json", 'r') as removedFile:
        removedDict = json.load(removedFile)
        for group, slurs in noDuplicateDict.items():
            cleanDict[group] = list(set(noDuplicateDict[group]).difference(removedDict.get(group, [])))

    with open("compactSlursList.json", "w") as outputFile:
        json.dump(cleanDict, outputFile)


compactLists("selectedSlursFromHatebase.json", "selectedSlursFromPapers.json", "selectedSlursFromWikipedia.json")
