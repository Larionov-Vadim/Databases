# -*- coding: utf-8 -*-
__author__ = 'vadim'
from larionov_api_app.dbService import cnxpool, execute
from contextlib import closing
from mysql.connector import Error as MysqlException
from mysql.connector import errorcode
from larionov_api_app.service import Codes, response_error, check_required_params
from larionov_api_app import get_lists
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
    query = """SELECT id, username, email, name, about, isAnonymous
           FROM User WHERE email IN
           (SELECT DISTINCT user FROM Post WHERE forum='%s') """ % data['forum']

    if 'since_id' in data:
        query += "AND id>=%s " % data['since_id']

    if 'order' in data:
        query += """ORDER BY name %s """ % data['order']
    else:
        query += """ORDER BY name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    try:
        response = execute(query)
        for x in response:
            x['following'] = get_lists.get_followers_list(x['email'])
            x['followers'] = get_lists.get_following_list(x['email'])
            x['subscriptions'] = get_lists.get_subscriptions_list(x['email'])
            x['isAnonymous'] = bool(x['isAnonymous'])

    except MysqlException as e:
        return response_error(Codes.unknown_error, e)

    return {
        'code': Codes.ok,
        'response': response
    }


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