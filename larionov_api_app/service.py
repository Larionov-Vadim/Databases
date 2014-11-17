# -*- coding: utf-8 -*-
__author__ = 'vadim'


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