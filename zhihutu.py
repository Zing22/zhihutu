# -*- coding=utf8 -*-

import argparse
from queue import Queue
from pprint import pprint


from author import Author, load_profile
from database import DBConnection



COOKIES_STR = 'd_c0="AGACDrRUpQuPTqD8WfNLPLOkf2C5KT21xUs=|1492853728"; _zap=acfffa44-5e86-4dd7-b66e-b29ca277c260; q_c1=d6168e6a8e73416a81c092fc706ae561|1499690037000|1492741497000; q_c1=d6168e6a8e73416a81c092fc706ae561|1499690037000|1492741497000; r_cap_id="NmFiOTFlZGQ2Yzk0NGIyYjlmMzQxMTYxNjJkZDExMjU=|1502073700|4fdc40c077bd1fbb79c5d9e9504673e3363313fb"; cap_id="MjhlNTI0MTRlN2Y3NDg3MDlkNjA4YmU3Y2VkZDk0ZTU=|1502073700|3a584bc8d380a81b0edff25778eb819d3b7e5d46"; __utma=155987696.169479353.1502169342.1502169342.1502169342.1; __utmc=155987696; __utmz=155987696.1502169342.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1502173780|14:capsion_ticket|44:NDM2YTAyZDliN2E5NGY5OWI3ZDA5Yzg4ZTViMGJmMDA=|566c447449e0e82f0468630e30519b928ef59fdb023b13c089185da203546b90"; z_c0="2|1:0|10:1502173785|4:z_c0|92:Mi4wQUVDQS1wbHp3UWtBWUFJT3RGU2xDeVlBQUFCZ0FsVk5XZWV3V1FDSHQ3QUpYSWhoM01ta0IzSy1GVy1IeGRqZlFR|e931bae038931bb056be216dc0d6117f77dcc6ac144ae23277fe5c53fd5baccf"; _xsrf=f8b3d4b8-88a0-467a-ba37-c48197fc1e76'
ORIGIN_URL_TOKEN = "zing22"
ORIGIN_NAME = "Lee Zing"
ORIGIN_GENDER = 1 # 1 means male, 0 means female
ORIGIN_AVATAR_URL_TEMPLATE = "https://pic1.zhimg.com/50/v2-ac93e9fbb70157e94e7d2cdc5ff8db6c_{size}.jpg"


def init():
    print("Begin initialize...")
    db_connection = DBConnection()
    url_token_set = db_connection.restore_url_token()

    origin = Author(ORIGIN_URL_TOKEN, COOKIES_STR, ORIGIN_NAME, ORIGIN_GENDER, ORIGIN_AVATAR_URL_TEMPLATE)
    return db_connection, url_token_set, origin


def updateState(author: Author, url_token_set: set, waiting_list: Queue):
    url_token_set.add(author.url_token)
    for followee in author.followees:
        if followee['user_type'] != 'people' or\
           followee['follower_count'] < 100 or \
           followee['url_token'] in url_token_set:
            continue
        next_author = Author(followee['url_token'],
                             COOKIES_STR,
                             followee['name'],
                             followee['gender'],
                             followee['avatar_url_template'])
        waiting_list.put(next_author)


def loop():
    db_connection, url_token_set, origin = init()
    waiting_list = Queue()
    waiting_list.put(origin)
    print("Init done, stored: {0}, waiting: {1}".format(len(url_token_set), waiting_list.qsize()))
    # start infinite loop!
    while not waiting_list.empty():
        top_author = waiting_list.get()
        if top_author.url_token in url_token_set:
            continue
        print('Ready for: {0} | {1}'.format(top_author.name, top_author.url_token))

        top_author.load_all()
        result = db_connection.save_author(top_author)
        updateState(top_author, url_token_set, waiting_list)

        print('{0} is saved, stored: {1}, waiting: {2}' \
            .format(result, len(url_token_set), waiting_list.qsize()))

    print('OVER! Change origin and try again!')


def crawl_one(url_token, db_connection, cookies_str):
    profile = load_profile(url_token, cookies_str)
    if not profile:
        return False
    author = Author(url_token, cookies_str, profile['name'], profile['gender'], profile['avatar_url_template'])
    author.load_answers()
    db_connection.save_author(author)
    return True


def get_one(url_token, db_connection, cookies_str):
    result = db_connection.find_one(url_token)
    if result is None:
        # 超过5个loading的就不跑了，需要测试
        if db_connection.loading_number() > 5:
            return {'name': 'Too many loadings'}
        try:
            db_connection.save_temp(url_token) # 占位，防止重复爬
            crawl_result = crawl_one(url_token, db_connection, cookies_str)
            print('crawl_result', crawl_result)
            if not crawl_result:
                db_connection.delete_many(url_token)
                result = {"name": "Not Exist"}
            else:
                result = db_connection.find_one(url_token)
        except Exception as e:
            print(e)
            db_connection.delete_many(url_token)
            result = {"name": "ERROR"}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--get", type=str,
                        help="Print the document in database if exists, otherwise crawl it and then print")
    parser.add_argument("-c", "--crawl", type=str,
                        help="Crawl one's total answer pictures")
    parser.add_argument("-f", "--find", type=str,
                        help="Print the document in database")
    parser.add_argument("-d", "--delete", type=str,
                        help="delete one document from database")
    args = parser.parse_args()
    db_connection = DBConnection()
    if args.crawl is not None:
        crawl_one(args.crawl, db_connection, COOKIES_STR)
    if args.find is not None:
        pprint(db_connection.find_one(args.find))
    if args.get is not None:
        pprint(get_one(args.get, db_connection, COOKIES_STR))
    if args.delete is not None:
        print(db_connection.delete_many(args.delete))

if __name__ == '__main__':
    main()
