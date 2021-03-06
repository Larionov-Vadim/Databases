# -*- coding: utf-8 -*-
__author__ = 'vadim'
from contextlib import closing

import MySQLdb
import MySQLdb.cursors
import mysql.connector
import mysql.connector.pooling

settings_db = {
    'host': 'localhost',
    'user': 'vadim',
    'passwd': 'vadim',
    'db': 'forum_db',
    'charset': 'utf8'
}
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_size=2, **settings_db)


def connect():
    settings_db1 = {
        'host': 'localhost',
        'user': 'vadim',
        'passwd': 'vadim',
        'db': 'forum_db',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.SSDictCursor
    }
    db = MySQLdb.connect(**settings_db1)
    return db


def execute(query, args=None):
    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            cursor.execute(query, args)
            result_list = cursor.fetchall()

    return result_list


def clear():
    with closing(cnxpool.get_connection()) as db:
        with closing(db.cursor(dictionary=True)) as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.execute("TRUNCATE TABLE Followers")
            cursor.execute("TRUNCATE TABLE Subscriptions")
            cursor.execute("TRUNCATE TABLE Post")
            cursor.execute("TRUNCATE TABLE Thread")
            cursor.execute("TRUNCATE TABLE Forum")
            cursor.execute("TRUNCATE TABLE User")
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    response = {
        'code': 0,
        'response': "OK"
    }
    return response