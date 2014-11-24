# -*- coding: utf-8 -*-
__author__ = 'vadim'

import requests
import json

url = 'http://localhost:8888/db/api/post/details'

values = {
    'forum': 'forum1',
    'user': 'larionov.vadim@mail.ru',
    'message': 'Xa-Xa-Xa',
    'thread': 2,
    'date': '2014-11-16 21:15'
}

headers = {'content-type': 'application/json'}

get_params = {
    'post': 3
}
# Get запрос
g = requests.get(url, params=get_params)
#print(g.url)

#p = requests.post(url, data=json.dumps(values), headers=headers)

# Вывод ошибки в файл err.html
f = open('err.html', 'w')
f.write(g.text.encode('utf8'))