# -*- coding: utf-8 -*-
__author__ = 'vadim'
from larionov_api_app.dbService import cnxpool
from contextlib import closing
from mysql.connector import Error as MysqlException

# import MySQLdb
# from larionov_api_app import dbService
from mysql.connector import errorcode
from larionov_api_app.service import Codes, response_error, check_required_params
import user
import post
import thread


def create(**data):
    try:
        check_required_params(data, ['name', 'short_name', 'user'])
    except Exception as e:
        response = response_error(Codes.unknown_error, str(e))
        return response

    query = "INSERT INTO Forum(name, short_name, user) VALUES (%s, %s, %s)"
    values = (data['name'], data['short_name'], data['user'])

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query, values)
                data['id'] = cursor.lastrowid
                db.commit()

            except MysqlException as e:
                db.rollback()
                if e[0] == errorcode.ER_DUP_ENTRY:
                    forum = details(db=db, close_db=False)
                    # Ok возвращать????
                    return response_error(Codes.ok, forum)

                elif e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)

                else:
                    return response_error(Codes.unknown_error, e)

    forum = {
        'id': data['id'],
        'name': data['name'],
        'short_name': data['short_name'],
        'user': data['user']
    }
    return {
        'code': Codes.ok,
        'response': forum
    }


def details(get_resp=False, **data):
    query = "SELECT id, name, short_name, user FROM Forum WHERE short_name='%s'"

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            cursor.execute(query % data['forum'])
            forum = cursor.fetchone()

    if forum is not None:
        if ('related' in data) and (data['related'] == 'user'):
            forum['user'] = user.details(**{'user': forum['user']})
    else:
        forum = {}

    if get_resp:
        if len(forum) == 0:
            str_err = "Forum '%s' not found" % data['forum']
            return response_error(Codes.not_found, str_err)
        else:
            return {
                'code': Codes.ok,
                'response': forum
            }

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

    return {
        'code': Codes.ok,
        'response': posts
    }


def list_users(**data):
    query = """SELECT id, username, email, name, about, isAnonymous,
              GROUP_CONCAT(DISTINCT thread
              ORDER BY thread SEPARATOR ' ') AS subscriptions,
              GROUP_CONCAT(DISTINCT Fr.followee
              ORDER BY Fr.followee SEPARATOR ' ') AS followers,
              GROUP_CONCAT(DISTINCT Fe.follower
              ORDER BY Fe.follower SEPARATOR ' ') AS following
              FROM User INNER JOIN
              (SELECT user FROM Post WHERE forum='%s' GROUP BY user) AS T ON User.email=T.user
              LEFT JOIN Subscriptions
              ON User.email=Subscriptions.user
              LEFT JOIN Followers AS Fr
              ON User.email=Fr.follower
              LEFT JOIN Followers AS Fe
              ON User.email=Fe.followee """ % data['forum']

    if 'since_id' in data:
        query += """WHERE id>=%s """ % data['since_id']
    query += "GROUP BY id "

    if 'order' in data:
        query += """ORDER BY name %s """ % data['order']
    else:
        query += """ORDER BY name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                users = cursor.fetchall()
            except MysqlException as e:
                response_error(Codes.unknown_error, e)

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
        return response_error(Codes.ok, '')

    elif 'related' in data:
        if 'user' in data['related']:
            for one_thread in threads:
                user_data = {'user': one_thread['user']}
                one_thread['user'] = user.details(**user_data)

        if 'forum' in data['related']:
            for one_thread in threads:
                forum_data = {'forum': one_thread['forum']}
                one_thread['forum'] = details(**forum_data)

    return {
        'code': Codes.ok,
        'response': threads
    }