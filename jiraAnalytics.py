import datetime
import json
import math
import threading
import time

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# Capture Start Time
start_time = time.time()
jsonlst = []


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

            'jql': 'project = "TRT EPOS"  ORDER BY  '
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


# process JQL in multithreading
def processJQL(startAt, endAt, maxresults, jql):
    str_json = ""
    strComma = ""

    j = startAt
    while True:
        # start_time1 = time.time()
        jsonOutVal = json.loads(jira.jira_parse(jql, j, maxresults))
        # print("--Thread --", startAt,  " -- ",endAt," -- ", (time.time() - start_time1), " Seconds")
        totalIssue = len(jsonOutVal["issues"])
        # print("Total Issues in Thread : ", startAt, " -- ", totalIssue)
        i = 0
        while i < totalIssue:
            # JSON file construction
            # print(jsonOutVal["issues"][i]["key"], "-", startAt + j + i, "-",
            # jsonOutVal["issues"][i]["fields"]["summary"])
            # linked issues
            iLinkedIssues = 0
            strLnkedSubissues = "";
            strLnkedissues = ""

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

            strSubJson = '"' + jsonOutVal["issues"][i]["id"] + '" : {' \
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
total_threads = 15
maxResults = 100

if math.ceil(total_issues / 100) < total_threads:
    total_threads = math.ceil(total_issues / 100)

step = math.ceil(total_issues / total_threads)

if step < 100:
    step = 100

for i_thread in range(0, total_issues, step):
    threading.Thread(target=processJQL, args=(i_thread, i_thread + step, maxResults, 1,)).start()

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
dfT.to_csv("./""" + "JIRADUMP" + ".csv", index=False)
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
