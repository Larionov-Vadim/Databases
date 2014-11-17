# -*- coding: utf-8 -*-
__author__ = 'vadim'
import MySQLdb


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