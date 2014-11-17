# -*- coding: utf-8 -*-
__author__ = 'vadim'

import requests
import json

url = 'http://localhost:8888/db/api/thread/update'

values = {
    'forum': 'forum1',
    'title': 'tirerwre',
    'isClosed': 0,
    'user': 'larionov.vadim@mail.ru',
    'date': '2014-11-16 19:31:00',
    'message': 'looouuuse',
    'slug': 'threadd'
}

headers = {'content-type': 'application/json'}

get_params = {
    'thread': 1,
    'slug': 'firstThread',
    'message': 'new Message'
}
# Get запрос
g = requests.get(url, params=get_params)
#print(g.url)

#p = requests.post(url, data=json.dumps(values), headers=headers)

# Вывод ошибки в файл err.html
f = open('err.html', 'w')
f.write(g.text.encode('utf8'))