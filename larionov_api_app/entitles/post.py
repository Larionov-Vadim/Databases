# -*- coding: utf-8 -*-
__author__ = 'vadim'
from larionov_api_app.dbService import cnxpool
from contextlib import closing
from mysql.connector import Error as MysqlException
from mysql.connector import errorcode
from larionov_api_app.service import response_error
from larionov_api_app.service import Codes
from larionov_api_app.service import check_optional_params, check_required_params
import user
import forum
import thread


def create(**data):
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

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query, values)
                data['id'] = cursor.lastrowid
                db.commit()
                cursor.execute("UPDATE Thread SET posts=posts+1 WHERE id=%s" % data['thread'])
                db.commit()

            except MysqlException as e:
                db.rollback()
                # Посты не уникальны
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    post = {
        'date': data['date'],
        'forum': data['forum'],
        'id': data['id'],
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

    return {
        'code': Codes.ok,
        'response': post
    }


def details(get_resp=False, **data):
    query = """SELECT date, dislikes, forum, id, isApproved,
              isDeleted, isEdited, isHighlighted, isSpam, likes,
              message, parent, likes - dislikes AS points,
              thread, user
              FROM Post WHERE id = %s""" % data['post']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                post = cursor.fetchone()
            except MysqlException as e:
                if get_resp:
                    return response_error(Codes.unknown_error, e)
                raise e

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

    if get_resp:
        if len(post) != 0:
            response = {
                'code': Codes.ok,
                'response': post
            }
        else:
            str_err = "Post with id=%s not found" % data['post']
            response = response_error(Codes.not_found, str_err)
        return response

    return post


def remove(**data):
    query = "UPDATE Post SET isDeleted=1 WHERE id=%s " % data['post']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                query_upd = """UPDATE Thread SET posts=posts-1
                               WHERE id=(SELECT thread FROM Post WHERE id=%s) """ % data['post']
                cursor.execute(query_upd)
                db.commit()
            except MysqlException as e:
                db.rollback()
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    # А если нет post-а с таким id?
    return {
        'code': Codes.ok,
        'response': {
            'post': data['post']
        }
    }


def restore(**data):
    query = """UPDATE Post SET isDeleted=0 WHERE id=%s """ % data['post']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                query_upd = """UPDATE Thread SET posts=posts+1
                               WHERE id=(SELECT thread FROM Post WHERE id=%s) """ % data['post']
                cursor.execute(query_upd)
                db.commit()
            except MysqlException as e:
                db.rollback()
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    # А если нет post-а с таким id?
    return {
        'code': Codes.ok,
        'response': {
            'post': data['post']
        }
    }


def update(**data):
    query = "UPDATE Post SET message='%s' WHERE id=%s" % (data['message'], data['post'])

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                db.commit()
            except MysqlException as e:
                db.rollback()
                return response_error(Codes.unknown_error, err=e)

    post = details(**{'post': data['post']})
    if len(post) != 0:
        return {
            'code': Codes.ok,
            'response': post
        }
    else:
        return {
            'code': Codes.not_found,
            'response': "Post with id=%s not found" % data['post']
        }


def vote(**data):
    # Нужна ли проверка required params?
    if str(data['vote']) == '1':
        query = "UPDATE Post SET likes=likes+1 WHERE id=%s " % data['post']
    elif str(data['vote']) == '-1':
        query = "UPDATE Post SET dislikes=dislikes+1 WHERE id=%s " % data['post']
    else:
        return {
            'code': Codes.unknown_error,
            'response': 'Not enough parameters or have incorrect parameter'
        }

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                db.commit()
            except MysqlException as e:
                db.rollback()
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    post = details(**{'post': data['post']})
    if len(post) == 0:
        return {
            'code': Codes.not_found,
            'response': "Post with id=%s not found" % data['post']
        }
    else:
        return {
            'code': Codes.ok,
            'response': post
        }


def list_posts(get_resp=False, **data):
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

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                posts = cursor.fetchall()
            except MysqlException as e:
                if get_resp:
                    return response_error(Codes.unknown_error, e)
                raise e

    ret_posts = list()
    for pst in posts:
        if pst['forum'] is not None:
            pst['date'] = pst['date'].strftime("%Y-%m-%d %H:%M:%S")
            ret_posts.append(pst)
        else:
            ret_posts = []

    if get_resp:
        # А если len(ret_post) == 0 ?
        return {
            'code': Codes.ok,
            'response': ret_posts
        }

    return ret_posts