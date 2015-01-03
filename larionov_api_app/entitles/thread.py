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
    try:
        check_required_params(data, ['forum', 'title', 'isClosed', 'user', 'date', 'message', 'slug'])
    except Exception as e:
        response = response_error(Codes.unknown_error, str(e))
        return response

    query = """INSERT INTO Thread(title, slug, message,
            isClosed, isDeleted, date, forum, user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    if 'isDeleted' not in data:
        data['isDeleted'] = False

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
    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        data['id'] = cursor.lastrowid
        db.commit()

    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_DUP_ENTRY:
            cursor.execute("SELECT * FROM Thread WHERE slug='%s'" % data['slug'])
            thread = cursor.fetchone()
            thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")
            # Ok возвращать????
            return response_error(Codes.ok, thread)

        elif e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)

        else:
            return response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    thread = {
        'date': data['date'],
        'forum': data['forum'],
        'id': data['id'],
        'isClosed': data['isClosed'],
        'isDeleted': data['isDeleted'],
        'message': data['message'],
        'slug': data['slug'],
        'title': data['title'],
        'user': data['user']
    }

    return {
        'code': Codes.ok,
        'response': thread
    }


def details(get_resp=False, **data):
    try:
        check_required_params(data, ['thread'])
    except Exception as e:
        if get_resp:
            return response_error(Codes.unknown_error, str(e))
        else:
            raise e

    # check optional params
    if 'related' in data:
        for elem in data['related']:
            if elem not in ['user', 'forum']:
                return response_error(Codes.incorrect_query, "Illegal arg %s" % elem)

    query = """SELECT id, title, slug, message, likes, dislikes,
              likes-dislikes AS points, isClosed, isDeleted,
              user, forum, posts, date
              FROM Thread WHERE id = %s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        thread = cursor.fetchone()
    except MySQLdb.Error as e:
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)
    finally:
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
    query = """UPDATE Thread SET isClosed = 1
                WHERE id=%s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread']
        }
    }


def open(**data):
    query = """UPDATE Thread SET isClosed = 0
                WHERE id=%s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread']
        }
    }


def list_threads(get_resp=False, **data):
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

    db = dbService.connect()
    cursor = db.cursor()
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
        return {
            'code': Codes.ok,
            'response': ret
        }

    return ret


def subscribe(**data):
    query = """INSERT INTO Subscriptions(user, thread)
              VALUES (%s, %s)"""
    values = (data['user'], data['thread'])

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)
    finally:
        cursor.close()
        db.close()

    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread'],
            'user': data['user']
        }
    }


def unsubscribe(**data):
    query = """DELETE FROM Subscriptions
                WHERE user = %s AND thread = %s"""
    values = (data['user'], data['thread'])

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)
    finally:
        cursor.close()
        db.close()

    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread'],
            'user': data['user']
        }
    }


def update(**data):
    query = """UPDATE Thread SET message = %s, slug = %s
                WHERE id = %s"""
    values = (data['message'], data['slug'], data['thread'])

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        # А какие тут ошибки могут быть?
        return response_error(Codes.unknown_error, err=e)
    finally:
        cursor.close()
        db.close()

    thread = details(**{'thread': data['thread']})
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
    try:
        check_required_params(data, ['thread'])
    except Exception as e:
        return response_error(Codes.unknown_error, e)

    query = """UPDATE Thread SET isDeleted=1 WHERE id=%s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        cursor.execute("UPDATE Post SET isDeleted=1 WHERE thread=%s" % data['thread'])
        cursor.execute("UPDATE Thread SET posts=0 WHERE id=%s" % data['thread'])
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    # А если нет thread-а с таким id, то что возвращать?
    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread']
        }
    }


def restore(**data):
    try:
        check_required_params(data, ['thread'])
    except Exception as e:
        return response_error(Codes.unknown_error, str(e))

    query = """UPDATE Thread SET isDeleted=0 WHERE id=%s""" % data['thread']

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        count_posts = cursor.execute("UPDATE Post SET isDeleted=0 WHERE thread=%s" % data['thread'])
        query_upd = "UPDATE Thread SET posts=%s WHERE id=%s" % (count_posts, data['thread'])
        cursor.execute(query_upd)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    # А если нет thread-а с таким id, то что возвращать?
    return {
        'code': Codes.ok,
        'response': {
            'thread': data['thread']
        }
    }


def vote(**data):
    if str(data['vote']) == '1':
        query = "UPDATE Thread SET likes=likes+1 WHERE id=%s " % data['thread']
    elif str(data['vote']) == '-1':
        query = "UPDATE Thread SET dislikes=dislikes+1 WHERE id=%s " % data['thread']
    else:
        return {
            'code': Codes.unknown_error,
            'response': "Not enough parameters or have uncorrected parameters"
        }

    db = dbService.connect()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
    except MySQLdb.Error as e:
        db.rollback()
        if e[0] == errorcode.ER_PARSE_ERROR:
            return response_error(Codes.incorrect_query, e)
        else:
            return response_error(Codes.unknown_error, e)
    finally:
        cursor.close()
        db.close()

    thread = details(**{'thread': data['thread']})
    if len(thread) != 0:
        return {
            'code': Codes.ok,
            'response': thread
        }
    else:
        return response_error(Codes.not_found, "Thread with id=%s not found" % data['thread'])


def list_posts(get_resp=False, **data):
    # Тут нужна магия при сортировке
    # Нет параметра sort
    try:
        check_required_params(data, ['thread'])
    except Exception as e:
        if get_resp:
            return response_error(Codes.unknown_error, str(e))
        else:
            raise e

    query = """SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited, isHighlighted,\
                isSpam, likes, message, parent, likes-dislikes AS points, thread, user \
                FROM Post WHERE thread=%s """ % data['thread']

    if 'since' in data:
        query += """AND date >= '%s' """ % data['since']
    if 'order' in data:
        query += """ORDER BY date %s """ % data['order']
    else:
        query += """ORDER BY date DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    db = dbService.connect()
    cursor = db.cursor()
    cursor.execute(query)
    posts = cursor.fetchall()

    for post_data in posts:
        if post_data['id'] is not None:
            post_data['isApproved'] = bool(post_data['isApproved'])
            post_data['isDeleted'] = bool(post_data['isDeleted'])
            post_data['isEdited'] = bool(post_data['isEdited'])
            post_data['isHighlighted'] = bool(post_data['isHighlighted'])
            post_data['date'] = post_data['date'].strftime("%Y-%m-%d %H:%M:%S")
        else:
            posts = []

    ret = list()
    for pst in posts:
        ret.append(pst)

    if get_resp:
        ## Если len(ret) == 0?
        return {
            'code': Codes.ok,
            'response': ret
        }

    return ret