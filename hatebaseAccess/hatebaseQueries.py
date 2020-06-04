## Query vocabulary lists from Hatebase.org

import requests
import urllib
import json
from datetime import datetime
from os import environ as env

## Start an API session, lasts one hour
def startHatebaseAPISession():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    ## Start an API session, lasts one hour

    sessionToken = None
    auth = requests.post("https://api.hatebase.org/4-4/authenticate", headers=headers,
                         data=urllib.parse.urlencode(env.get('HATEBASE_KEY')))
    # Get session token
    try:
        authJson = auth.json()
        try:
            sessionToken = authJson["result"]["token"]
        except Exception as e:
            print(e)
            print("No token, see full JSON")
            print(authJson)
            raise Exception(e)
    except Exception as e:
        print(e)
        print("The query did not return a JSON")
        raise Exception(e)

    return sessionToken


def getSinglePageVocab(sessionToken = None, page = 1, queryDetails = {}):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Get the vocabulary list
    vocabList = []
    if sessionToken != None:
        queryData = {"token": sessionToken, "format": "json", "page": page}
        queryData.update(queryDetails)
        results = requests.post("https://api.hatebase.org/4-4/get_vocabulary", headers=headers,
                                data=urllib.parse.urlencode(queryData))
        # Extract list from response
        try:
            resultsJSON = results.json()
            for item in resultsJSON["result"]:
                try:
                    vocab = item["term"]
                    vocabList.append(vocab)
                except Exception as e:
                    print(e)
                    print("Not a word")
                    raise Exception(e)

        except Exception as e:
            print(e)
            print("The query did not return a JSON")
            raise Exception(e)

        return vocabList


## Useful if we want to get more than 100 lines at the same time
# /!\ Would need to be adapted because the API gives no indication when we reach the end of the pages
# def getFullVocab(sessionToken = None, queryDetails = {}):
#     if sessionToken == None:
#         print("Please provide a valid session token")
#         return
#
#     # Get all pages for given queryDetails
#     page = 1
#     end = False
#     vocabList = []
#     while not end:
#         try:
#             vocabList.append(getSinglePageVocab(sessionToken, page, queryDetails))
#             page += 1
#         except Exception as e:
#             print(e)
#             end = True
#
#     saveVocabList(vocabList)



def saveVocabList(vocabList, queryDetails):
    # Save results to file
    if len(vocabList) > 0:
        now = datetime.utcnow()
        date_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        vocabSave = { "queryInfo": queryDetails, "date": date_time, "worlds": vocabList }
        fileName = "hatebaseAccess/hatebaseVocabulary_%s" % date_time
        try:
            with open(fileName, "w") as saveFile:
                json.dump(vocabSave, saveFile)
        except Exception as e:
            print(e)
            print("Could not save results")
            raise Exception(e)


sessionToken = startHatebaseAPISession(queryKey)
## Loop over ethnicities
ethnicities = ["african", "african american", "arabs", "asian", "chinese", "hispanic", "japanese", "jews", "korean", "vietnamese"]
for eth in ethnicities:
    queryDetails = {"language": "ENG", "is_about_ethnicity": "true", "ethnicity": eth}
    saveVocabList(getSinglePageVocab(sessionToken = sessionToken, queryDetails = queryDetails), queryDetails)
