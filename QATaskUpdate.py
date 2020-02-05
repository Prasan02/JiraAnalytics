import json

import requests
from requests.auth import HTTPBasicAuth


# JIRA
def jira_parse(**kwargs):
    # url, query, payload
    auth = HTTPBasicAuth("prasannakumar.karakavalasa@cigniti.com", "CHMlaJNzzYtLR33KePbB3D04")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # get issue
    if "query" in kwargs:
        query = json.loads(kwargs["query"])
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query,
            auth=auth
        )
        #            data=kwargs["payload"],

    # post issue
    if "payload" in kwargs:
        payload = json.dumps(json.loads(kwargs["payload"]))
        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )
    return response.text


url = "https://askblackswan.atlassian.net/rest/api/3/search?&expand=changelog"
jql = '{"jql":"project = '"'TRT EPOS'"' AND issuetype='"'QA TASK'"'and assignee=prasannakumar.karakavalasa and status ' \
      '='"'Ready for Sign Off'"' ","fields":["key"]}'
# url, query, payload
jira_response = json.loads(jira_parse(url=url, query=jql))["issues"]

for istatus_update in jira_response:
    print(istatus_update["key"])
    issue = istatus_update["key"]
    url = "https://askblackswan.atlassian.net/rest/api/3/issue/" + issue + "/transitions"
    id = 41
    payload = '{"transition":{"id":"' + str(id) + '"}}'
    response = jira_parse(url=url, payload=payload)

print("Execution Completed, ", len(jira_response), "issues effected")
