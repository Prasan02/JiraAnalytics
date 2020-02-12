import json
import xml.etree.ElementTree as ET

from json2xml import json2xml

from JiraResponse import Jira


def getTransition_xml(json):
    xml = json2xml.Json2xml(json).to_xml()
    root = ET.fromstring(xml)
    statusUpdate = ""
    lst = []
    i = 0
    for issues in root.findall('issues'):
        j = 0
        for history in issues.findall('changelog/histories'):
            if history.find('items/field').text == 'status':
                if history.find('author/key') is not None:
                    author = history.find('author/key').text
                else:
                    author = "No author"
                statusUpdate = "[" + history.find('items/fromString').text + "," + history.find(
                    'items/toString').text + "," + \
                               author + "," + history.find('created').text + "]"
                print(i, j, statusUpdate)
                j += 1
                lst.append(statusUpdate)
            i += 1

    return lst


def getTransistion_json(json, **kwargs):
    for issue in range(len(response["issues"])):
        print("------------------------------------------", response["issues"][issue]["key"],
              "------------------------------------------------")
        history = response["issues"][issue]["changelog"]["histories"]
        i = 0
        for a in history:
            if a['items'][0]['field'] == "status":
                print(i, "%s" % (a['author']['key'] if 'author' in a else "No author"), \
                      "%s" % (a['items'][0]['fromString'] if 'items' in a else "No from status"),
                      "%s" % (a['items'][0]['toString'] \
                                  if 'items' in a else "No to status"))
            i += 1


get_response = Jira

url = "https://askblackswan.atlassian.net/rest/api/2/issue/TRTEPOS-5883/changelog"

# url = "https://askblackswan.atlassian.net/rest/api/2/search?startAt=0&maxResults=100&expand=changelog"
jql = '{"jql":"project = '"'TRT EPOS'"' and issuekey=TRTEPOS-5883 ORDER BY ID ASC  "}'
response = json.loads(get_response.jira_parse("GET", url=url, query=jql))
getTransistion_json(response)

# print(history.find('items/field').text, "changed from", history.find('items/fromString').text, \
#       "to", history.find('items/toString').text, "by", history.find(`'author/key').text, "on",
#       history.find('created').text)AND issuekey in (TRTEPOS-2)
