# -*- coding: utf-8 -*-
__author__ = 'vadim'

import json


class Codes:
    ok = 0
    not_found = 1
    invalid_query = 2
    incorrect_query = 3
    unknown_error = 4
    user_exists = 5


def check_optional_params(kwargs, param, default):
    if param not in kwargs:
        kwargs[param] = default


def check_required_params(kwargs, params):
    for param in params:
        if param not in kwargs:
            raise Exception("Required parameter %s not found" % param)


def get_request_data(request):
    try:
        if request.method == 'POST':
            request_data = json.loads(request.body, encoding='UTF-8')
        else:
            lists = request.GET.lists()
            request_data = dict()
            for param in lists:
                if len(param[1]) == 1:
                    request_data[param[0]] = param[1][0]

                else:
                    request_data[param[0]] = param[1]


    except Exception as e:
        raise e

    return request_data


def response_error(code, err):
    response = {
        'code': code,
        'response': str(err)
    }
    return response