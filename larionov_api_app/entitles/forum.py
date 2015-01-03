# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb
from mysql.connector import errorcode
from larionov_api_app.service import Codes
from larionov_api_app.service import response_error
from larionov_api_app import dbService
import user
import post
import thread
from larionov_api_app.service import check_optional_params, check_required_params


def create(**data):
    try:
        check_required_params(data, ['name', 'short_name', 'user'])
    except Exception as e:
        response = response_error(Codes.unknown_error, str(e))
        return response

    query = "INSERT INTO Forum(name, short_name, user) VALUES (%s, %s, %s)"
    values = (data['name'], data['short_name'], data['user'])
    response = dict()

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        data['id'] = cursor.lastrowid
        db.commit()

    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_DUP_ENTRY:
            forum = details(db=db, close_db=False, **{'forum': data['short_name']})
            # Ok возвращать????
            response = response_error(Codes.ok, forum)

        elif e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)

        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        forum = {
            "id": data['id'],
            "name": data['name'],
            "short_name": data['short_name'],
            "user": data['user']
        }
        response = {
            'code': Codes.ok,
            'response': forum
        }

    return response


# Всё надо проверять
def details(get_resp=False, db=0, close_db=True, **data):
    query = """SELECT id, name, short_name, user FROM Forum WHERE short_name=%s"""
    values = (data['forum'])

    if db == 0:
        db = dbService.connect()
    cursor = db.cursor()

    cursor.execute(query, values)
    forum = cursor.fetchone()
    if forum is not None:
        if ('related' in data) and (data['related'] == 'user'):
            user_data = {'user': forum['user']}
            forum['user'] = user.details(**user_data)
    else:
        forum = {}

    cursor.close()
    if close_db:
        db.close()

    if get_resp:
        if len(forum) == 0:
            str_err = "Forum '%s' not found" % data['forum']
            response = response_error(Codes.not_found, str_err)
        else:
            response = {
                'code': Codes.ok,
                'response': forum
            }
        return response

    return forum


def list_posts(**data):
    # Приходит forum, а для list_posts нужен thread
    posts = post.list_posts(**data)

    if len(posts) == 0:
        # Знатный костыль, но так требует серв
        return response_error(Codes.ok, "")

    if 'related' in data:
        if 'user' in data['related']:
            for one_post in posts:
                user_data = {'user': one_post['user']}
                one_post['user'] = user.details(**user_data)

        if 'forum' in data['related']:
            for one_post in posts:
                forum_data = {'forum': one_post['forum']}
                one_post['forum'] = details(**forum_data)

        if 'thread' in data['related']:
            for one_post in posts:
                thread_data = {'thread': one_post['thread']}
                one_post['thread'] = thread.details(**thread_data)

    response = {
        'code': Codes.ok,
        'response': posts
    }
    return response


def list_users(**data):
    query = """SELECT id, username, email, name, about, isAnonymous,
              GROUP_CONCAT(DISTINCT thread
              ORDER BY thread SEPARATOR ' ') AS subscriptions,
              GROUP_CONCAT(DISTINCT Fr.followee
              ORDER BY Fr.followee SEPARATOR ' ') AS followers,
              GROUP_CONCAT(DISTINCT Fe.follower
              ORDER BY Fe.follower SEPARATOR ' ') AS following
              FROM User LEFT JOIN Subscriptions
              ON User.email = Subscriptions.user
              LEFT JOIN Followers AS Fr
              ON User.email = Fr.follower
              LEFT JOIN Followers AS Fe
              ON User.email = Fe.followee
              WHERE email IN
              (SELECT user FROM Post WHERE forum = '%s') """ % data['forum']

    if 'since_id' in data:
        query += """AND id >= %s """ % data['since_id']
    query += "GROUP BY id "

    if 'order' in data:
        query += """ORDER BY name %s """ % data['order']
    else:
        query += """ORDER BY name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    db = dbService.connect()
    cursor = db.cursor()
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    db.close()

    for user_data in users:
        if user_data['email'] is not None:
            if user_data['followers'] is None:
                user_data['followers'] = []
            else:
                user_data['followers'] = user_data['followers'].split()

            if user_data['following'] is None:
                user_data['following'] = []
            else:
                user_data['following'] = user_data['following'].split()

            if user_data['subscriptions'] is None:
                user_data['subscriptions'] = []
            else:
                # Строка не проходит тесты :(
                user_data['subscriptions'] = user_data['subscriptions'].split()
                list_subscriptions = list()
                for elem in user_data['subscriptions']:
                    list_subscriptions.append(int(elem))
                user_data['subscriptions'] = list_subscriptions

            user_data['isAnonymous'] = bool(user_data['isAnonymous'])
        else:
            users = []

    ret_users = list()
    for usr in users:
        ret_users.append(usr)

    response = {
        'code': Codes.ok,
        'response': '',
    }

    if len(users) != 0:
        response['response'] = ret_users

    return response


def list_threads(**data):
    threads = thread.list_threads(**data)

    if len(threads) == 0:
        # response = {
        #    'code': Codes.not_found,
        #    'response': 'Threads not found, forum short_name=%s' % data['forum']
        #}
        #return response
        return response_error(Codes.ok, "")

    elif 'related' in data:
        if 'user' in data['related']:
            for one_thread in threads:
                user_data = {'user': one_thread['user']}
                one_thread['user'] = user.details(**user_data)

        if 'forum' in data['related']:
            for one_thread in threads:
                forum_data = {'forum': one_thread['forum']}
                one_thread['forum'] = details(**forum_data)

    response = {
        'code': Codes.ok,
        'response': threads
    }
    return response