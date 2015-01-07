# -*- coding: utf-8 -*-
__author__ = 'vadim'

import requests
import json

url = 'http://localhost:8888/db/api/thread/details/'

values = {
    'thread': 1,
    'related': ['user', 'forum']
}

headers = {'content-type': 'application/json'}

get_params = {
    'thread': 1,
    'related': ['user', 'forum']
}
# Get запрос
g = requests.get(url, params=get_params)
#print(g.url)

p = requests.post(url, data=json.dumps(values), headers=headers)

# Вывод ошибки в файл err.html
f = open('err.html', 'w')
f.write(p.text.encode('utf8'))