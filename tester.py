#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 11:48:55 2020

@author: christophboomer
"""


import pandas as pd
import requests
import hashlib,hmac
import json
import urllib

api_key = "oH06ES95OuUn9X87CPmC0xvJfhmh5bL2O9nfFhMkngHPdjlM5lYXvBWSKuOAaIvH"
api_secret = "1VClNkmSGB5N6kQgsk2ZkSNoa9qzZVQzbH8UXlFr6gJVlGIIg47Y5tWYgHNDSTPH"
#signature = hashlib.sha256(api_secret.encode('utf-8'))




servertime = requests.get("https://api.binance.com/api/v1/time")
servertimeobject = json.loads(servertime.text)
servertimeint = servertimeobject['serverTime']
params = urllib.parse.urlencode({
    "timestamp" : servertimeint,
})
hashedsig = hmac.new(api_secret.encode('utf-8'), params.encode('utf-8'),
hashlib.sha256).hexdigest()
userdata = requests.get("https://api.binance.com/api/v3/account",
    params = {
        "timestamp" : servertimeint,
        "signature" : hashedsig,
    },
    headers = {
        "X-MBX-APIKEY" : api_key,
    }
)
