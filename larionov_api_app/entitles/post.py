# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb
from mysql.connector import errorcode
from larionov_api_app import dbService
from larionov_api.error_handler import response_error
from larionov_api_app.service import Codes
from larionov_api_app.service import check_optional_params
import user
import forum
import thread


def create(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """INSERT INTO Post(message, isApproved, isDeleted,
                isEdited, isHighlighted, isSpam, date, parent,
                 forum, thread, user)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    check_optional_params(data, 'parent', None)
    check_optional_params(data, 'isApproved', False)
    check_optional_params(data, 'isHighlighted', False)
    check_optional_params(data, 'isEdited', False)
    check_optional_params(data, 'isSpam', False)
    check_optional_params(data, 'isDeleted', False)

    values = (
        data['message'],
        data['isApproved'],
        data['isDeleted'],
        data['isEdited'],
        data['isHighlighted'],
        data['isSpam'],
        data['date'],
        data['parent'],
        data['forum'],
        data['thread'],
        data['user']
    )

    response = list()
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        db.rollback()
        # Посты не уникальны
        if e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)

        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        # Для обновления posts в Thread в БД предусмотрены триггеры
        #   increment_posts и decrement_posts
        cursor.close()
        db.close()

    post = {
        'date': data['date'],
        'forum': data['forum'],
        'id': cursor.lastrowid,
        'isApproved': data['isApproved'],
        'isDeleted': data['isDeleted'],
        'isEdited': data['isEdited'],
        'isHighlighted': data['isHighlighted'],
        'isSpam': data['isSpam'],
        'message': data['message'],
        'parent': data['parent'],
        'thread': data['thread'],
        'user': data['user']
    }
    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': post
        }
    return response


def details(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT date, dislikes, forum, id, isApproved,
              isDeleted, isEdited, isHighlighted, isSpam, likes,
              message, parent, likes - dislikes AS points,
              thread, user
              FROM Post WHERE id = %s""" % data['post']

    cursor.execute(query)
    post = cursor.fetchone()

    if post is None:
        post = {}
    else:
        if 'related' in data:
            if 'user' in data['related']:
                user_data = {'user': post['user']}
                post['user'] = user.details(**user_data)

            if 'forum' in data['related']:
                forum_data = {'forum': post['forum']}
                post['forum'] = forum.details(**forum_data)

            if 'thread' in data['related']:
                thread_data = {'thread': post['thread']}
                post['thread'] = thread.details(**thread_data)

        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])

    return post


def remove(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Post SET isDeleted = 1
               WHERE id = %s """ % data['post']

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

    # А если нет post-а с таким id?
    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'post': data['post']
            }
        }
    return response


def restore(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Post SET isDeleted = 0
               WHERE id = %s """ % data['post']

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

    # А если нет post-а с таким id?
    if len(response) == 0:
        response = {
            'code': Codes.ok,
            'response': {
                'post': data['post']
            }
        }
    return response

def update(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """UPDATE Post SET message = %s WHERE id = %s"""
    values = (data['message'], data['post'])

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
        post_data = {'post': data['post']}
        post = details(**post_data)
        if len(post) == 0:
            response = {
                'code': Codes.not_found,
                'response': "Post with id=%s not found" % data['post']
            }
        else:
            response = {
                'code': Codes.ok,
                'response': post
            }
    return response




def vote(**data):
    values = (data['post'])
    if str(data['vote']) == '1':
        query = """UPDATE Post SET likes = likes + 1 WHERE id = %s """
    elif str(data['vote']) == '-1':
        query = """UPDATE Post SET dislikes = dislikes + 1 WHERE id = %s """
    else:
        response = {
            'code': Codes.unknown_error,
            'response': 'Not enough parameters or have uncorrect parameters'
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
        post_data = {'post': data['post']}
        post = details(**post_data)
        if len(post) == 0:
            response = {
                'code': Codes.not_found,
                'response': "Post with id=%s not found" % data['post']
            }
        else:
            response = {
                'code': Codes.ok,
                'response': post
            }
    return response


def list_posts(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT date, dislikes, forum, id, isApproved, isDeleted,
                isEdited, isHighlighted, isSpam, likes, message, parent,
                likes - dislikes AS points, thread, user
                FROM Post WHERE """

    if 'forum' in data:
        query += "forum = '%s' " % data['forum']
    elif 'thread' in data:
        query += "thread = %s " % data['thread']
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
    posts = cursor.fetchall()

    ret_posts = list()
    for pst in posts:
        if pst['forum'] is not None:
            pst['date'] = pst['date'].strftime("%Y-%m-%d %H:%M:%S")
            ret_posts.append(pst)
        else:
            ret_posts = []
    return ret_posts




















