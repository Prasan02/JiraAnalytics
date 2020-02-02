import json

import requests
from requests.auth import HTTPBasicAuth


class Jira():
    # JIRA
    # Accepted Params : url, query, payload
    def jira_parse(request_type, **kwargs):
        url = kwargs["url"]
        auth = HTTPBasicAuth("prasannakumar.karakavalasa@cigniti.com", "CHMlaJNzzYtLR33KePbB3D04")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        # get issue
        if request_type == "GET":
            if "query" in kwargs:
                query = json.loads(kwargs["query"])
            else:
                query = ""
            response = requests.request(
                "GET",
                url,
                headers=headers,
                params=query,
                auth=auth
            )
            #            data=kwargs["payload"],

        # post issue
        if request_type == "POST":
            payload = json.dumps(json.loads(kwargs["payload"]))
            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=headers,
                auth=auth
            )
        return response.text
