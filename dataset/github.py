#!/usr/bin/env python2
import sys
import requests
import json
import random
import base64

def result(r, expected_code):
    if r.status_code == expected_code:
        return json.loads(r.content)
    else:
        print '[*] response content', r.content
        return None

class Github():
    def __init__(self, token):
        self.session = requests.Session()
        if random.choice([True, False]) == True:
            self.session.headers['Authorization'] = 'token %s' % token

    @property
    def url(self):
        return 'https://api.github.com'

    def post(self, query, data, expected_code=201):
        return result(self.session.post(self.url + query, data), expected_code)

    def get(self, query, expected_code=200):
        return result(self.session.get(self.url + query), expected_code)

    def put(self, query, data):
        r = self.session.put(self.url + query, data = data)
        return r.status_code == 205

    def patch(self, query, data):
        r = self.session.patch(self.url + query, data = data)
        return r.status_code == 205

    def poll(self, query):
        r = self.session.get(self.url + query)
        poll_interval = int(r.headers['X-Poll-Interval'])
        response = result(r, 200)
        return response, poll_interval
