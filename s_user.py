# -*- coding: utf-8 -*-
__author__ = 'vadim'

import requests
import json


url = 'http://localhost:8888/db/api/user/listPosts'

values = {
    'user': 'root@mail.ru'
}

headers = {'content-type': 'application/json'}

get_params = {
    'user': 'larionov.vadim@mail.ru',
    'order': 'DESC',
    'since': '2015-10-12 00:01:00'
}
# Get запрос
#g = requests.get(url, params=get_params)
#print(g.url)

p = requests.post(url, data=json.dumps(values), headers=headers)

# Вывод ошибки в файл err.html
f = open('err.html', 'w')
f.write(p.text.encode('utf8'))