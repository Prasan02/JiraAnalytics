import datetime
import json
import math
import threading
import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from json2xml import json2xml
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Capture Start Time
start_time = time.time()
jsonlst = []


def getTransistion_json(json, issueid):
    allstatus = ""
    status = []
    for a in json:
        if a['items'][0]['field'] == "status":
            author = (a['author']['key'] if 'author' in a else "No author")
            fromString = (a['items'][0]['fromString'] if 'items' in a else "No from status")
            toString = (a['items'][0]['toString'] if 'items' in a else "No to status")
            createdstatus = (a['created'] if 'created' in a else "No to Created date")
            try:
                # allstatus = allstatus + ">" + "[" + fromString + "," + toString + "," + \
                #             author + "," + createdstatus + "]"
                status.append(fromString + ">" + toString + "-" + \
                              author + "^" + createdstatus)
            except Exception as e:
                allstatus = "error" + str(e)
    # print(str(status).replace("'",""))
    return str(status).replace("'", "")


class Jira:
    # JIRA
    def jira_parse(*args, **kwargs):
        jql = args[0]
        start_at = args[1]
        maxResults = args[2]

        url = "https://askblackswan.atlassian.net/rest/api/3/search?startAt=" + str(
            start_at) + "&maxResults=" + str(maxResults) + "&expand=changelog"
        auth = HTTPBasicAuth("prasannakumar.karakavalasa@cigniti.com", "CHMlaJNzzYtLR33KePbB3D04")
        headers = {
            "Accept": "application/json"
        }
        query = {

            'jql': 'project = "TRT EPOS" ORDER BY  '
                   'id ASC', "fields": ["id", "key", "reporter", "summary", "priority", "issuetype", "status",
                                        "customfield_18695", "customfield_11401", "assignee", "created", "updated",
                                        "fixVersions", "components", "issuelinks", "labels"]
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query,
            auth=auth
        )
        return response.text


# Create new JSON file
def writeToJsonFile(path, filename, data):
    filePathNameExt = './' + path + '/' + filename + '.json'
    with open(filePathNameExt, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)


# get Jira transitions
def getTransition(json):
    xml = json2xml.Json2xml(json).to_xml()
    root = ET.fromstring(xml)
    statusUpdate = ""
    lst = []
    for issues in root.findall('issues'):
        # print(issues.find('key').text)
        for history in issues.findall('changelog/histories'):
            if history.find('author/key') is not None:
                author = history.find('author/key').text
            else:
                author = "No author"

            if history.find('items/fromString') is not None:
                fromString = history.find('items/fromString').text
            else:
                fromString = "NoFromStatus"

            if history.find('items/toString') is not None:
                toString = history.find('items/toString').text
            else:
                toString = "NoToString"

            if history.find('created') is not None:
                createdstatus = history.find('created').text
            else:
                createdstatus = "NoCreated"
            try:
                if history.find('items/field').text == 'status':
                    statusUpdate = "[" + fromString + "," + toString + "," + \
                                   author + "," + createdstatus + "]"
            except Exception as e:
                statusUpdate = "error" + str(e)

            lst.append(statusUpdate)

    return lst


# process JQL in multithreading
def processJQL(startAt, endAt, maxresults, jql):
    str_json = ""
    strComma = ""

    j = startAt
    while True:
        # start_time1 = time.time()
        jsonOutVal = json.loads(jira.jira_parse(jql, j, maxresults))
        totalIssue = len(jsonOutVal["issues"])
        i = 0
        while i < totalIssue:
            # JSON file construction
            # linked issues
            iLinkedIssues = 0
            strLnkedSubissues = "";
            strLnkedissues = ""
            transitions = getTransistion_json(jsonOutVal["issues"][i]["changelog"]["histories"],
                                              jsonOutVal["issues"][i]["key"])

            if len(jsonOutVal["issues"][i]["fields"]["issuelinks"]) > 0:

                while True:
                    if 'outwardIssue' in jsonOutVal["issues"][i]["fields"]["issuelinks"][iLinkedIssues]:
                        strLnkedSubissues = \
                            jsonOutVal["issues"][i]["fields"]["issuelinks"][iLinkedIssues]["outwardIssue"][
                                "key"]
                    else:
                        strLnkedSubissues = \
                            jsonOutVal["issues"][i]["fields"]["issuelinks"][iLinkedIssues]["inwardIssue"][
                                "key"]

                    strLnkedissues = strLnkedissues + "%s" % ("," if iLinkedIssues > 0 else "") + strLnkedSubissues
                    iLinkedIssues += 1
                    if iLinkedIssues == len(jsonOutVal["issues"][i]["fields"]["issuelinks"]):
                        break;
            # path = './'
            # filename = "JiraImport"
            # writeToJsonFile(path, filename,
            #                 json.loads(
            #                     json.dumps(jsonOutVal, sort_keys=True, indent=4, separators=(",", ": "))))

            # labels
            iLabels = 0
            strLabel = ""
            if len(jsonOutVal["issues"][i]["fields"]["labels"]) > 0:
                while True:
                    strLabel = strLabel + "%s" % ("," if iLabels > 0 else "") + \
                               jsonOutVal["issues"][i]["fields"]["labels"][iLabels]
                    iLabels += 1
                    if iLabels == len(jsonOutVal["issues"][i]["fields"]["labels"]):
                        break;

            strSubJson = '"' + (jsonOutVal["issues"][i]["key"]).split("-")[1] + '" : {' \
                         + '"issueKey" :' + '"' + jsonOutVal["issues"][i]["key"] + '"' + "," \
                         + '"issueType" :' + '"' + jsonOutVal["issues"][i]["fields"]["issuetype"]["name"] + '"' + "," \
                         + '"summary" :' + '"' + (
                             (jsonOutVal["issues"][i]["fields"]["summary"]).replace('"', '\\"')).strip() + '"' + "," \
                         + '"reporter_name" :' + '"' + jsonOutVal["issues"][i]["fields"]["reporter"][
                             "displayName"] + '"' + "," \
                         + '"reporter_id" :' + '"' + jsonOutVal["issues"][i]["fields"]["reporter"]["name"] + '"' + "," \
                         + '"priority" :' + '"' + jsonOutVal["issues"][i]["fields"]["priority"]["name"] + '",' \
                         + '"status" :' + '"' + jsonOutVal["issues"][i]["fields"]["status"]["name"] + '",' \
                         + '"created" :' + '"' + str(
                datetime.datetime.strptime((jsonOutVal["issues"][i]["fields"]["created"]).split("+")[0],
                                           '%Y-%m-%dT%H:%M:%S.%f')) + '",' \
                         + '"Updated" :' + '"' + jsonOutVal["issues"][i]["fields"]["updated"] + '",' \
                         + '"components" :' + '"' + "%s" % (
                             'None' if len(jsonOutVal["issues"][i]["fields"]["components"]) == 0 else
                             jsonOutVal["issues"][i]["fields"]["components"][0]["name"]) + '",' \
                         + '"fixVersion" :' + '"' + "%s" % (
                             'None' if len(jsonOutVal["issues"][i]["fields"]["fixVersions"]) == 0 else
                             jsonOutVal["issues"][i]["fields"]["fixVersions"][0]["name"]) + '",' \
                         + '"build version" :' + '"' + "%s" % (
                             'None' if jsonOutVal["issues"][i]["fields"]["customfield_18695"] is None else
                             jsonOutVal["issues"][i]["fields"][
                                 "customfield_18695"]["value"]) + '",' \
                         + '"build" :' + '"' + "%s" % (
                             'None' if jsonOutVal["issues"][i]["fields"]["customfield_11401"] is None else
                             jsonOutVal["issues"][i]["fields"]["customfield_11401"]) + '",' \
                         + '"assignee" :' + '"' + "%s" % (
                             'None' if jsonOutVal["issues"][i]["fields"]["assignee"] is None else
                             jsonOutVal["issues"][i]["fields"]["assignee"]["displayName"]) + '",' \
                         + '"transitions" :' + '"' + transitions + '",' \
                         + '"labels" :' + '"' + strLabel + '",' \
                         + '"linkedIssues" :' + '"' + strLnkedissues \
                         + '"}'

            if i != 0:
                strComma = ","
            if i == totalIssue:
                strComma = ""
            str_json = str_json + strComma + strSubJson
            strSubJson = ""
            i += 1

        j += maxresults
        if j == endAt or j > endAt:
            break
    # if str_json != "":
    #     print("Thread -- ", startAt, " - ", endAt, " - ", str_json)

    jsonlst.append(str_json)


jira = Jira
total_issues = json.loads(jira.jira_parse(0, 0, 0))["total"]
total_threads = 20
maxResults = 100

if math.ceil(total_issues / 100) < total_threads:
    total_threads = math.ceil(total_issues / 100)

step = math.ceil(total_issues / total_threads)

if step < 100:
    step = 100

for i_thread in range(0, total_issues, step):
    threading.Thread(target=processJQL, args=(i_thread, i_thread + step, maxResults, 1,)).start()

iprogress = 0
pbar = tqdm(total=100, desc="Pulling data from Jira")
while True:
    # print((len(jsonlst) * step),"%", total_issues,"=",iprogress)
    # tqdm.write("Done task %i" % iprogress)
    pbar.update((((len(jsonlst) * step) / total_issues) * 100) - iprogress)
    iprogress = ((len(jsonlst) * step) / total_issues) * 100
    if len(jsonlst) * step >= total_issues:
        pbar.close()
        break;
    time.sleep(0.1)

# wait threads to finish
while threading.active_count() > 1:
    time.sleep(0.1)

print("Total Issues : ", total_issues)
strJson = ""
iComma = 0
strComma = ""

for item in jsonlst:
    if iComma != 0:
        strComma = ","
    if iComma == len(jsonlst):
        strComma = ""
    strJson = strJson + strComma + item
    iComma += 1

finalJson = json.loads('{' + strJson + '}')

df = pd.DataFrame(finalJson)
dfT = df.transpose()
dfT.index = dfT.index.astype(int)
dfS = dfT.sort_index()

dfS.to_csv("./""" + "JIRADUMP" + ".csv", index=False)
print("--- %s seconds ---" % (time.time() - start_time))

# https://askblackswan.atlassian.net/rest/api/2/issue/TRTEPOS-11390/transitions??expand=transitions.fields
# filename = "json" + str(iComma)
# writeFile = open(filename, 'w')
# writeFile.write('{' + item + '}')
# path = './'
# filename = "JiraImport_" + str(iComma)
# writeToJsonFile(path, filename,
#                 json.loads(
#                     json.dumps(json.loads('{' + item + '}'), sort_keys=True, indent=4, separators=(",", ": "))))
# processJQL(i_thread, i_thread + step, maxResults, 1)
# print("Thread ",i_thread, " Json --------------------------------------->")
# print("Thread from main program...........................", i_thread, "...to...", i_thread + step, "  completed")
# print("Thread from main program...........From......", i_thread, "...to...", i_thread + step)
