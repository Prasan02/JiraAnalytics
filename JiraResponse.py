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
