# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb
import MySQLdb.cursors
# from DBUtils.PooledDB import PooledDB
# import mysql.connector

# pool_size = 3
# pool = PooledDB(mysql.connector, pool_size, database='forum_db', user='vadim', host='127.0.0.1', passwd='vadim', charset='utf8')

# db1 = MySQLdb.connect(**{'host': 'localhost',
#         'user': 'vadim',
#         'passwd': 'vadim',
#         'db': 'forum_db',
#         'charset': 'utf8',
#         'cursorclass': MySQLdb.cursors.SSDictCursor})


def connect():
    settings_db = {
        'host': 'localhost',
        'user': 'vadim',
        'passwd': 'vadim',
        'db': 'forum_db',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.SSDictCursor
    }
    db = MySQLdb.connect(**settings_db)
    return db


def clear():
    db = connect()
    cursor = db.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute("TRUNCATE TABLE Followers")
    cursor.execute("TRUNCATE TABLE Subscriptions")
    cursor.execute("TRUNCATE TABLE Post")
    cursor.execute("TRUNCATE TABLE Thread")
    cursor.execute("TRUNCATE TABLE Forum")
    cursor.execute("TRUNCATE TABLE User")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    cursor.close()
    db.close()

    response = {
        'code': 0,
        'response': "OK"
    }
    return response