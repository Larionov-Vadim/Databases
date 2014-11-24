# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb
from mysql.connector import errorcode
from larionov_api_app import dbService
from larionov_api_app.service import response_error
from larionov_api_app.service import Codes
import user
import forum
from larionov_api_app.service import check_optional_params, check_required_params


def create(**data):
    print("Thread Create")
    try:
        check_required_params(data, ['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'])
    except Exception as e:
        response = response_error(Codes.unknown_error, str(e))
        return response

    db = dbService.connect()
    cursor = db.cursor()

    query = """INSERT INTO Thread(title, slug, message,
            isClosed, isDeleted, date, forum, user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    check_optional_params(data, 'isDeleted', False)

    values = (
        data['title'],
        data['slug'],
        data['message'],
        data['isClosed'],
        data['isDeleted'],
        data['date'],
        data['forum'],
        data['user']
    )

    response = dict()
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_DUP_ENTRY:
            cursor.execute("SELECT * FROM Thread WHERE slug='%s'" % data['slug'])
            thread = cursor.fetchone()
            thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
            # Ok возвращать????
            response = response_error(Codes.ok, thread)

        elif e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)

        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        thread = {
            "date": data['date'],
            "forum": data['forum'],
            "id": cursor.lastrowid,
            "isClosed": data['isClosed'],
            "isDeleted": data['isDeleted'],
            "message": data['message'],
            "slug": data['slug'],
            "title": data['title'],
            "user": data['user']
        }
        response = {
            'code': Codes.ok,
            'response': thread
        }

    return response


def details(get_resp=False, **data):
    print("Thread details")

    try:
        check_required_params(data, ['thread'])
    except Exception as e:
        if get_resp:
            return response_error(Codes.unknown_error, str(e))
        else:
            raise e

    query = """SELECT id, title, slug, message, likes, dislikes,
              likes-dislikes AS points, isClosed, isDeleted,
              user, forum, posts, date
              FROM Thread WHERE id = %s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    cursor.execute(query)
    thread = cursor.fetchone()
    cursor.close()
    db.close()

    if thread is None:
        return response_error(Codes.not_found, "Thread with id=%s not found" % data['thread'])

    if thread['title'] is None:
        thread = {}
    else:
        if 'related' in data:
            if 'user' in data['related']:
                user_data = {'user': thread['user']}
                thread['user'] = user.details(**user_data)

            if 'forum' in data['related']:
                forum_data = {'forum': thread['forum']}
                thread['forum'] = forum.details(**forum_data)

        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
        thread['isClosed'] = bool(thread['isClosed'])
        thread['isDeleted'] = bool(thread['isDeleted'])

    if get_resp:
        if len(thread) != 0:
            response = {
                'code': Codes.ok,
                'response': thread
            }
        else:
            response = response_error(Codes.not_found, "Thread with id=%s not found" % data['thread'])
        return response

    return thread


def close(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Thread SET isClosed = 1
                WHERE id=%s""" % data['thread']

    response = list()
    try:
        cursor.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread']
            }
        }
    return response


def open(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Thread SET isClosed = 0
                WHERE id=%s""" % data['thread']

    response = list()
    try:
        cursor.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread']
            }
        }
    return response


def list_threads(get_resp=False, **data):
    print("Post list")
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT id, title, slug, message, likes, dislikes,
              likes-dislikes AS points, isClosed, isDeleted,
              user, forum, posts, date
              FROM Thread WHERE """

    if 'user' in data:
        query += "user = '%s' " % data['user']
    elif 'forum' in data:
        query += "forum = '%s' " % data['forum']
    # else, по-идее, запрос не должен пройти семантически
    # Хотяя...

    if 'since' in data:
        query += """AND date >= '%s' """ % data['since']

    if 'order' in data:
        query += """ORDER BY date %s """ % data['order']
    else:
        query += """ORDER BY date DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    cursor.execute(query)
    threads = cursor.fetchall()

    for thread_data in threads:
        if thread_data['title'] is not None:
            thread_data['isClosed'] = bool(thread_data['isClosed'])
            thread_data['isDeleted'] = bool(thread_data['isDeleted'])
            thread_data['date'] = thread_data['date'].strftime("%Y-%m-%d %H:%M:%S")
        else:
            threads = []

    ret = list()
    for thr in threads:
        ret.append(thr)

    if get_resp:
        ## Если len(ret) == 0?
        response = {
            'code': Codes.ok,
            'response': ret
        }
        return response

    return ret


def subscribe(**data):
    print("Thread subscribe")
    print(data)
    db = dbService.connect()
    cursor = db.cursor()

    query = """INSERT INTO Subscriptions(user, thread)
              VALUES (%s, %s)"""
    values = (data['user'], data['thread'])

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread'],
                'user': data['user']
            }
        }
    return response


def unsubscribe(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """DELETE FROM Subscriptions
                WHERE user = %s AND thread = %s"""
    values = (data['user'], data['thread'])

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)
    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread'],
                'user': data['user']
            }
        }
    return response


def update(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Thread SET message = %s, slug = %s
                WHERE id = %s"""
    values = (data['message'], data['slug'], data['thread'])

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        # А какие тут ошибки могут быть?
        response = response_error(Codes.unknown_error, err=e)
        #raise e
    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        thread_data = {'thread': data['thread']}
        thread = details(**thread_data)
        if len(thread) == 0:
            response = {
                'code': Codes.not_found,
                'response': "Thread with id=%s not found" % data['thread']
            }
        else:
            response = {
                'code': Codes.ok,
                'response': thread
            }

    return response


def remove(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Thread SET isDeleted = 1 WHERE id = %s"""
    values = (data['thread'])

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    # А если нет thread-а с таким id?
    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread']
            }
        }
    return response


def restore(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Thread SET isDeleted = 0 WHERE id = %s"""
    values = (data['thread'])

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    # А если нет thread-а с таким id?
    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'thread': data['thread']
            }
        }
    return response


def vote(**data):
    print("Thread vote")

    values = (data['thread'])
    if str(data['vote']) == '1':
        query = """UPDATE Thread SET likes = likes + 1 WHERE id = %s """
    elif str(data['vote']) == '-1':
        query = """UPDATE Thread SET dislikes = dislikes + 1 WHERE id = %s """
    else:
        response = {
            'code': Codes.unknown_error,
            'response': "Not enough parameters or have uncorrect parameters"
        }
        return response

    db = dbService.connect()
    cursor = db.cursor()

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)
        else:
            response = response_error(Codes.unknown_error, e)
    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        thread_data = {'thread': data['thread']}
        thread = details(**thread_data)
        if len(thread) == 0:
            response = response_error(Codes.not_found, "Thread with id=%s not found" % data['thread'])
        else:
            response = {
                'code': Codes.ok,
                'response': thread
            }
    return response


def list_posts(**data):
    # Тут нужна магия при сортировке
    return True