# -*- coding: utf-8 -*-
__author__ = 'vadim'
from larionov_api_app.dbService import cnxpool, execute
from contextlib import closing
import mysql.connector
from mysql.connector import Error as MysqlException
from mysql.connector import errorcode
from larionov_api_app.service import Codes
from larionov_api_app.service import response_error
from larionov_api_app.service import check_optional_params, check_required_params

from larionov_api_app import get_lists


def create(**data):
    try:
        check_required_params(data, ['username', 'email', 'name', 'about'])
    except Exception as e:
        return response_error(Codes.unknown_error, str(e))

    # Тут должна быть проверка на корректность данных в data
    query = "INSERT INTO User(username, email, name, about, isAnonymous) VALUES (%s, %s, %s, %s, %s)"

    if 'isAnonymous' not in data:
        data['isAnonymous'] = False

    values = (data['username'],
              data['email'],
              data['name'],
              data['about'],
              bool(data['isAnonymous']))

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query, values)
                data['id'] = cursor.lastrowid
                db.commit()

            except MysqlException as e:
                db.rollback()
                if e[0] == errorcode.ER_DUP_ENTRY:
                    return response_error(Codes.user_exists, e)
                elif e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    user = {
        'about': data['about'],
        'email': data['email'],
        'id': data['id'],
        'isAnonymous': data['isAnonymous'],
        'name': data['name'],
        'username': data['username']
    }

    return {
        'code': Codes.ok,
        'response': user
    }


def details(get_resp=False, **data):
    query_user = "SELECT * FROM User WHERE email='%s'" % data['user']

    try:
        user = execute(query_user)[0]
        user['followers'] = get_lists.get_followers_list(data['user'])
        user['following'] = get_lists.get_following_list(data['user'])
        user['subscriptions'] = get_lists.get_subscriptions_list(data['user'])
        user['isAnonymous'] = bool(user['isAnonymous'])

    except MysqlException as e:
        if get_resp:
            return response_error(Codes.unknown_error, e)
        raise e

    if get_resp:
        return {
            'code': Codes.ok,
            'response': user
        }

    return user


def follow(**data):
    # Здесь должна быть проверка на корректность данных в **data

    # Здесь всё верно
    query = """INSERT INTO Followers(follower, followee)
               VALUES ('%s', '%s')""" % (data['followee'], data['follower'])

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                db.commit()

            except mysql.connector.Error as e:
                # Если email не существует
                #if e[0] == errorcode.ER_NO_REFERENCED_ROW_2:
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    user = details(**{'user': data['follower']})
    return {
        'code': Codes.ok,
        'response': user
    }


def unfollow(**data):
    query = "DELETE FROM Followers WHERE follower=%s AND followee=%s"
    # Тут всё верно
    values = (data['followee'], data['follower'])

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query, values)
                db.commit()

            except mysql.connector.Error as e:
                if e[0] == errorcode.ER_PARSE_ERROR:
                    return response_error(Codes.incorrect_query, e)
                else:
                    return response_error(Codes.unknown_error, e)

    user = details(**{"user": data['follower']})
    return {
        'code': Codes.ok,
        'response': user
    }


def update_profile(**data):
    query = "UPDATE User SET name=%s, about=%s WHERE email=%s"
    values = (data['name'], data['about'], data['user'])

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query, values)
                db.commit()

            except mysql.connector.Error as e:
                return response_error(Codes.unknown_error, e)

    user = details(**{'user': data['user']})
    return {
        'code': Codes.ok,
        'response': user
    }


def list_followers(**data):
    query = """SELECT DISTINCT Followers.followee AS user
                FROM User LEFT JOIN Followers ON User.email=Followers.follower
                INNER JOIN User AS Usr ON Followers.followee=Usr.email
                WHERE User.email='%s' """ % str(data['user'])

    if 'since_id' in data:
        query += """AND Usr.id >= %s """ % str(data['since_id'])

    if 'order' in data:
        query += """ORDER BY Usr.name %s """ % data['order']
    else:
        query += """ORDER BY Usr.name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                followers = cursor.fetchall()

            except mysql.connector.Error as e:
                return response_error(Codes.unknown_error, e)

    ret = list()
    if followers is not None:
        for user in followers:
            ret.append(details(**{"user": user['user']}))

    return {
        'code': Codes.ok,
        'response': ret
    }


def list_following(**data):
    query = """SELECT DISTINCT Followers.follower AS user
                FROM User LEFT JOIN Followers ON User.email=Followers.followee
                INNER JOIN User AS Usr ON Followers.follower=Usr.email
                WHERE User.email='%s' """ % str(data['user'])

    if 'since_id' in data:
        query += """AND Usr.id>=%s """ % str(data['since_id'])

    if 'order' in data:
        query += """ORDER BY Usr.name %s """ % data['order']
    else:
        query += """ORDER BY Usr.name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute(query)
                following = cursor.fetchall()

            except mysql.connector.Error as e:
                return response_error(Codes.unknown_error, e)

    ret = list()
    if following is not None:
        for user in following:
            user_data = {"user": user['user']}
            ret.append(details(**user_data))

    return {
        'code': Codes.ok,
        'response': ret
    }


def list_posts(**data):
    query = """SELECT date, dislikes, forum, id, isApproved,
              isDeleted, isEdited, isHighlighted, isSpam, likes,
              message, parent, likes - dislikes AS points,
              thread, user FROM Post WHERE user='%s' """ % data['user']

    if 'since' in data:
        query += """AND date>='%s' """ % data['since']

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

            except mysql.connector.Error as e:
                return response_error(Codes.unknown_error, e)

    ret = list()
    for post in posts:
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        ret.append(post)

    return {
        'code': Codes.ok,
        'response': ret
    }