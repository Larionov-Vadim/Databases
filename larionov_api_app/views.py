# -*- coding: utf-8 -*-
from larionov_api_app.entitles import user, forum, thread, post

__author__ = 'vadim'

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpRequest, HttpResponse

@csrf_exempt
def user_view(request, method):
    print("I am user_views!")

    func = {
        'create': user.create,                  # Готовит сразу response
        'details': user.details,
        'follow': user.follow,                  # Как-то работает, сразу response
        'listFollowers': user.list_followers,   # response
        'listFollowing': user.list_foolowing,   # В точности listFollowers
        'listPosts': user.list_posts,           # response
        'unfollow': user.unfollow,              # В точности как follow
        'updateProfile': user.update_profile    # response
    }[method]

    if request.method == 'POST':
        request_data = json.loads(request.body, encoding='UTF-8')
    else:
        request_data = request.GET.dict()

    print(request.method)
    print(request_data)

    response = HttpResponse()
    response.write("<h3>Hello, World!</h3>")
    #response.content
    try:
        t = func(**request_data)
        response.write(t)
    except Exception as e:
        if e:
            print("Exception!!!!!")
            response.write(e)

    return response


@csrf_exempt
def forum_view(request, method):
    print("I am forum_view")

    func = {
        'create': forum.create,                 # response
        'details': forum.details,
        'listPosts': forum.list_posts,          # response
        'listThreads': forum.list_threads,      # response
        'listUsers': forum.list_users           # response
    }[method]

    if request.method == 'POST':
        request_data = json.loads(request.body, encoding='UTF-8')
    else:
        request_data = request.GET.dict()

    response = HttpResponse()
    response.write("<h3>Hello, World!</h3>")
    try:
        t = func(**request_data)
        response.write(t)

    except Exception as e:
        print("Exception!!!")
        response.write(e)

    print(response)
    return response


@csrf_exempt
def thread_view(request, method):
    print("I am thread_view")

    func = {
        'create': thread.create,                # response
        'details': thread.details,
        'close': thread.close,                  # response
        'list': thread.list_threads,
        #'listPosts': thread.list_posts,
        'open': thread.open,                    # response
        'remove': thread.remove,                # response
        'restore': thread.restore,              # response
        'subscribe': thread.subscribe,          # response
        'unsubscribe': thread.unsubscribe,      # response
        'update': thread.update,                # response
        'vote': thread.vote                     # response
    }[method]

    if request.method == 'POST':
        request_data = json.loads(request.body, encoding='UTF-8')
    else:
        request_data = request.GET.dict()

    response = HttpResponse()

    try:
        t = func(**request_data)
        response.write(t)
    except Exception as e:
        print("Exception!!!")
        response.write(e)

    return response


@csrf_exempt
def post_view(request, method):
    print("I am post_views!")

    func = {
        'create': post.create,      # response
        'details': post.details,
        'list': post.list_posts,
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
    print(request_data)

    response = HttpResponse()
    response.write("<h3>Hello, World!</h3>")

    try:
        t = func(**request_data)
        response.write(t)
    except Exception as e:
        if e:
            print("Exception!!!")
            response.write(e)
    return response