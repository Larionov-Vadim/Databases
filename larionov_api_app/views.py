# -*- coding: utf-8 -*-
__author__ = 'vadim'


from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
import re
from larionov_api_app import dbService
from larionov_api_app.service import Codes
from larionov_api_app.entitles import user, forum, thread, post
from larionov_api_app.service import get_request_data, response_error


@csrf_exempt
def user_view(request, method):
    #print("I am user_views!")
    #print("method " + method)
    method = re.sub('/', '', method)
    func = {
        'create': user.create,                  # Готовит сразу response
        'details': user.details,                # Что-то response подобное
        'follow': user.follow,                  # Как-то работает, сразу response
        'listFollowers': user.list_followers,   # response
        'listFollowing': user.list_following,   # В точности listFollowers
        'listPosts': user.list_posts,           # response
        'unfollow': user.unfollow,              # В точности как follow
        'updateProfile': user.update_profile    # response
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    #print(request.method)
    #print(request_data)

    try:
        if func is not user.details:
            response = func(**request_data)
        else:
            response = func(get_resp=True, **request_data)
    except Exception as e:
        if e:
            print("Exception: ", str(e))
            response = response_error(Codes.unknown_error, e)

    #print("RESPONSE_USER: ", response)
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def forum_view(request, method):
    #print("I am forum_view")
    method = re.sub('/', '', method)
    func = {
        'create': forum.create,                 # response
        'details': forum.details,               # response
        'listPosts': forum.list_posts,          # response
        'listThreads': forum.list_threads,      # response
        'listUsers': forum.list_users           # response
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    #print(request.method)
    #print(request_data)

    try:
        if func is not forum.details:
            response = func(**request_data)
        else:
            response = func(get_resp=True, **request_data)
    except Exception as e:
        print("Exception: ", str(e))
        response = response_error(Codes.unknown_error, e)

    #print("RESPONSE_FORUM: ", response)
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def thread_view(request, method):
    #print("I am thread_view")
    method = re.sub('/', '', method)
    func = {
        'create': thread.create,                # response
        'details': thread.details,              # response, вроде как
        'close': thread.close,                  # response
        'list': thread.list_threads,            # Чё-то абы как
        'listPosts': thread.list_posts,         # Без сортировок
        'open': thread.open,                    # response
        'remove': thread.remove,                # response
        'restore': thread.restore,              # response
        'subscribe': thread.subscribe,          # response
        'unsubscribe': thread.unsubscribe,      # response
        'update': thread.update,                # response
        'vote': thread.vote                     # response
    }[method]

    try:
        request_data = get_request_data(request)
    except Exception as e:
        response = response_error(Codes.invalid_query, e)
        return HttpResponse(json.dumps(response), content_type='application/json')

    #print(request.method)
    #print(request_data)

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
        print("Exception: ", str(e))
        response = response_error(Codes.unknown_error, e)

    #print("RESPONSE_THREAD: ", response)
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def post_view(request, method):
    print("I am post_views!")
    method = re.sub('/', '', method)
    func = {
        'create': post.create,      # response
        'details': post.details,    # Как-то работает
        'list': post.list_posts,    # Чё-то как-то
        'remove': post.remove,      # response
        'restore': post.restore,    # response
        'update': post.update,      # response
        'vote': post.vote           # response
    }[method]

    if request.method == 'POST':
        request_data = json.loads(request.body, encoding='UTF-8')
    else:
        request_data = request.GET.dict()

    print(request.method)
    print("RequestData", request_data)

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
            print("Exception: ", str(e))
            response = response_error(Codes.unknown_error, e)

    print("RESPONSE_POST: ", response)
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def clear_view(request):
    ret_resp = dbService.clear()
    return HttpResponse(json.dumps(ret_resp), content_type='application/json')


@csrf_exempt
def hello(request):
    response = "Hello, my Friend!"
    return HttpResponse(response)