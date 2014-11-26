# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb
from mysql.connector import errorcode
from larionov_api_app import dbService
from larionov_api_app.service import Codes
from larionov_api_app.service import response_error
from larionov_api_app.service import check_optional_params, check_required_params


def create(**data):
    try:
        check_required_params(data, ['username', 'email', 'name', 'about'])
    except Exception as e:
        return response_error(Codes.unknown_error, str(e))

    # Тут должна быть проверка на корректность данных в data
    db = dbService.connect()
    cursor = db.cursor()
    query = "INSERT INTO User(username, email, name, about, isAnonymous) VALUES (%s, %s, %s, %s, %s)"

    if 'isAnonymous' not in data:
        data['isAnonymous'] = False

    values = (data['username'],
              data['email'],
              data['name'],
              data['about'],
              bool(data['isAnonymous']))

    response = dict()
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        if e[0] == errorcode.ER_DUP_ENTRY:
            response = response_error(Codes.user_exists, e)

        elif e[0] == errorcode.ER_PARSE_ERROR:
            response = response_error(Codes.incorrect_query, e)

        else:
            response = response_error(Codes.unknown_error, e)

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        user = {
            "about": data['about'],
            "email": data['email'],
            "id": cursor.lastrowid,
            "isAnonymous": data['isAnonymous'],
            "name": data['name'],
            "username": data['username']
        }
        response.update({
            'code': Codes.ok,
            'response': user
        })

    return response


def details(get_resp=False, **data):
    print("Details !!!")
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
              WHERE email = %s"""
    values = (data['user'])

    db = dbService.connect()
    cursor = db.cursor()

    cursor.execute(query, values)
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user['email'] is None or len(user) == 0:
        user = {}

    else:
        if user['followers'] is None:
            user['followers'] = []
        else:
            user['followers'] = user['followers'].split()

        if user['following'] is None:
            user['following'] = []
        else:
            user['following'] = user['following'].split()

        # Вот это не проверил
        if user['subscriptions'] is None:
            user['subscriptions'] = []
        else:
            # Строка не проходит тесты :(
            # Аналогично в forum.list_users
            user['subscriptions'] = user['subscriptions'].split()
            list_subscriptions = list()
            for elem in user['subscriptions']:
                list_subscriptions.append(int(elem))
            user['subscriptions'] = list_subscriptions

        user['isAnonymous'] = bool(user['isAnonymous'])

    if get_resp:
        if len(user) == 0:
            str_err = "User %s not found" % data['user']
            response = response_error(Codes.not_found, str_err)
        else:
            response = {
                'code': Codes.ok,
                'response': user
            }
        return response

    return user


def follow(**data):
    print("User_follow")
    # Проверка на корректность данных в **data гдеее?
    db = dbService.connect()
    cursor = db.cursor()

    query = """INSERT INTO Followers(follower, followee)
                VALUES (%s, %s)"""

    #values = (data['follower'], data['followee'])
    #experiment
    values = (data['followee'], data['follower'])

    response = dict()
    print("CHEEEEK")
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        # Если email не существует
        #if e[0] == errorcode.ER_NO_REFERENCED_ROW_2:
        if e[0] == errorcode.ER_PARSE_ERROR:
            response.update({
                'code': Codes.incorrect_query,
                'response': str(e)
            })

        else:
            response.update({
                'code': Codes.unknown_error,
                'response': str(e)
            })

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        user = {'user': data['follower']}
        user = details(**user)
        response.update({
            'code': Codes.ok,
            'response': user
        })

    return response


def unfollow(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """DELETE FROM Followers WHERE follower=%s AND followee=%s"""

    #values = (data['follower'], data['followee'])
    #experiment
    values = (data['followee'], data['follower'])

    response = dict()
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        # Если email не существует
        #if e[0] == errorcode.ER_NO_REFERENCED_ROW_2:
        if e[0] == errorcode.ER_PARSE_ERROR:
            response.update({
                'code': Codes.incorrect_query,
                'response': str(e)
            })

        else:
            response.update({
                'code': Codes.unknown_error,
                'response': str(e)
            })

    finally:
        cursor.close()
        db.close()

    if len(response) == 0:
        user = {"user": data['follower']}
        user = details(**user)
        response.update({
            'code': Codes.ok,
            'response': user
        })
    return response


def update_profile(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """ UPDATE User SET name=%s, about=%s
                WHERE email=%s"""
    values = (data['name'], data['about'], data['user'])

    response = dict()
    try:
        cursor.execute(query, values)
        db.commit()

    except MySQLdb.Error as e:
        # А какие тут ошибки могут быть?
        response.update({
            'code': Codes.unknown_error,
            'response': str(e)
        })
        #raise e

    finally:
        cursor.close()
        db.close()


    if len(response) == 0:
        user = {'user': data['user']}
        user = details(**user)
        response.update({
            'code': Codes.ok,
            'response': user
        })

    return response


def list_followers(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT DISTINCT Followers.followee AS user
                FROM User LEFT JOIN Followers ON User.email=Followers.follower
                INNER JOIN User AS Usr ON Followers.followee=Usr.email
                WHERE User.email = '%s' """ % str(data['user'])

    if 'since_id' in data:
        query += """AND Usr.id >= %s """ % str(data['since_id'])

    if 'order' in data:
        query += """ORDER BY Usr.name %s """ % data['order']
    else:
        query += """ORDER BY Usr.name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    try:
        cursor.execute(query)

    except MySQLdb.Error as e:
        response = response_error(Codes.unknown_error, e)
        cursor.close()
        db.close()
        return response

    followers = cursor.fetchall()

    ret = list()
    if followers is not None:
        for user in followers:
            user_data = {"user": user['user']}
            ret.append(details(**user_data))

    response = {
        'code': Codes.ok,
        'response': ret
    }
    cursor.close()
    db.close()
    return response


def list_foolowing(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT DISTINCT Followers.follower AS user
                FROM User LEFT JOIN Followers ON User.email=Followers.followee
                INNER JOIN User AS Usr ON Followers.follower=Usr.email
                WHERE User.email = '%s' """ % str(data['user'])

    if 'since_id' in data:
        query += """AND Usr.id >= %s """ % str(data['since_id'])

    if 'order' in data:
        query += """ORDER BY Usr.name %s """ % data['order']
    else:
        query += """ORDER BY Usr.name DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    try:
        cursor.execute(query)

    except MySQLdb.Error as e:
        response = response_error(Codes.unknown_error, e)
        cursor.close()
        db.close()
        return response

    following = cursor.fetchall()

    ret = list()
    if following is not None:
        for user in following:
            user_data = {"user": user['user']}
            ret.append(details(**user_data))

    response = {
        'code': Codes.ok,
        'response': ret
    }
    cursor.close()
    db.close()
    return response


def list_posts(**data):
    db = dbService.connect()
    cursor = db.cursor()

    query = """SELECT date, dislikes, forum, id, isApproved,
              isDeleted, isEdited, isHighlighted, isSpam, likes,
              message, parent, likes - dislikes AS points,
              thread, user
              FROM Post WHERE user = '%s' """ % data['user']

    if 'since' in data:
        query += """AND date >= '%s' """ % data['since']

    if 'order' in data:
        query += """ORDER BY date %s """ % data['order']
    else:
        query += """ORDER BY date DESC """

    if 'limit' in data:
        query += """LIMIT %s """ % data['limit']

    try:
        cursor.execute(query)

    except MySQLdb.Error as e:
        response = response_error(Codes.unknown_error, e)
        cursor.close()
        db.close()
        return response

    posts = cursor.fetchall()
    ret = list()
    for post in posts:
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        ret.append(post)

    response = {
        'code': Codes.ok,
        'response': ret
    }
    cursor.close()
    db.close()
    return response