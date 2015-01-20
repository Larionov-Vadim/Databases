__author__ = 'vadim'

from larionov_api_app.dbService import cnxpool, execute
from contextlib import closing


def get_followers_list(email):
    query = "SELECT followee FROM Followers WHERE follower='%s'" % email
    followers = execute(query)
    list_followers = list()
    for x in followers:
        list_followers.append(x['followee'])
    return list_followers


def get_following_list(email):
    query = "SELECT follower FROM Followers WHERE followee='%s'" % email
    following = execute(query)
    list_following = list()
    for x in following:
        list_following.append(x['follower'])
    return list_following


def get_subscriptions_list(email):
    query = "SELECT thread FROM Subscriptions WHERE user='%s'" % email
    subscriptions = execute(query)
    list_subscriptions = list()
    for x in subscriptions:
        list_subscriptions.append(x['thread'])
    return list_subscriptions