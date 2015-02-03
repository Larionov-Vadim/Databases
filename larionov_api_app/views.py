# -*- coding: utf-8 -*-
__author__ = 'vadim'
import time

from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
import re
from larionov_api_app import dbService
from larionov_api_app.service import Codes
from larionov_api_app.entitles import user, forum, thread, post
from larionov_api_app.service import get_request_data, response_error
import traceback


@csrf_exempt
def user_view(request, method):
    method = re.sub('/', '', method)
    func = {
        'create': user.create,
        'details': user.details,
        'follow': user.follow,
        'listFollowers': user.list_followers,
        'listFollowing': user.list_following,
        'listPosts': user.list_posts,
        'unfollow': user.unfollow,
        'updateProfile': user.update_profile
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    try:
        if func is not user.details:
            response = func(**request_data)
        else:
            response = func(get_resp=True, **request_data)
    except Exception as e:
        if e:
            print("Exception in User: ", str(e))
            print traceback.print_exc()
            response = response_error(Codes.unknown_error, e)

    if response['code'] != Codes.ok:
        # Логгирование
        print "REQUEST_DATA: " + str(request_data)
        print "RESPONSE: " + str(response)

    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def forum_view(request, method):
    method = re.sub('/', '', method)
    func = {
        'create': forum.create,
        'details': forum.details,
        'listPosts': forum.list_posts,
        'listThreads': forum.list_threads,
        'listUsers': forum.list_users
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    try:
        if func is not forum.details:
            response = func(**request_data)
        else:
            response = func(get_resp=True, **request_data)
    except Exception as e:
        print("Exception in Forum: ", str(e))
        print traceback.print_exc()
        response = response_error(Codes.unknown_error, e)

    if response['code'] != Codes.ok:
        # Логгирование
        print "REQUEST_DATA: " + str(request_data)
        print "RESPONSE: " + str(response)

    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def thread_view(request, method):
    method = re.sub('/', '', method)
    func = {
        'create': thread.create,
        'details': thread.details,
        'close': thread.close,
        'list': thread.list_threads,
        'listPosts': thread.list_posts,
        'open': thread.open,
        'remove': thread.remove,
        'restore': thread.restore,
        'subscribe': thread.subscribe,
        'unsubscribe': thread.unsubscribe,
        'update': thread.update,
        'vote': thread.vote
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    try:
        if func is thread.details:
            response = func(get_resp=True, **request_data)
        elif func is thread.list_threads:
            response = func(get_resp=True, **request_data)
        elif func is thread.list_posts:
            response = func(get_resp=True, **request_data)
        else:
            response = func(**request_data)
    except Exception as e:
        print("Exception in Thread: ", str(e))
        print traceback.print_exc()
        response = response_error(Codes.unknown_error, e)

    if response['code'] != Codes.ok:
        print "REQUEST_DATA: " + str(request_data)
        print "RESPONSE: " + str(response)

    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def post_view(request, method):
    method = re.sub('/', '', method)
    func = {
        'create': post.create,
        'details': post.details,
        'list': post.list_posts,
        'remove': post.remove,
        'restore': post.restore,
        'update': post.update,
        'vote': post.vote
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    try:
        if func is post.details:
            response = func(get_resp=True, **request_data)
        elif func is post.list_posts:
            response = func(get_resp=True, **request_data)
        else:
            response = func(**request_data)
    except Exception as e:
        if e:
            print("Exception in Post: ", str(e))
            print traceback.print_exc()
            response = response_error(Codes.unknown_error, e)

    if response['code'] != Codes.ok:
        print "REQUEST_DATA: " + str(request_data)
        print "RESPONSE: " + str(response)

    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def clear_view(request):
    ret_resp = dbService.clear()
    return HttpResponse(json.dumps(ret_resp), content_type='application/json')


@csrf_exempt
def hello(request):
    response = "Hello, my Friend!"
    return HttpResponse(response)