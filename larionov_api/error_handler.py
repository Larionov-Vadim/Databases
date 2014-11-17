__author__ = 'vadim'
#from mysql.connector import errorcode
#from larionov_api_app.service import Codes


def response_error(code, err):
    response = {
        'code': code,
        'response': err
    }
    return response