import json, re, argparse
from queue import Queue
from time import sleep
from pprint import pprint


from author import Author, load_profile
from database import DBConnection



COOKIES_STR = 'd_c0="AGACDrRUpQuPTqD8WfNLPLOkf2C5KT21xUs=|1492853728"; _zap=acfffa44-5e86-4dd7-b66e-b29ca277c260; q_c1=d6168e6a8e73416a81c092fc706ae561|1499690037000|1492741497000; q_c1=d6168e6a8e73416a81c092fc706ae561|1499690037000|1492741497000; r_cap_id="NmFiOTFlZGQ2Yzk0NGIyYjlmMzQxMTYxNjJkZDExMjU=|1502073700|4fdc40c077bd1fbb79c5d9e9504673e3363313fb"; cap_id="MjhlNTI0MTRlN2Y3NDg3MDlkNjA4YmU3Y2VkZDk0ZTU=|1502073700|3a584bc8d380a81b0edff25778eb819d3b7e5d46"; capsion_ticket="2|1:0|10:1502076733|14:capsion_ticket|44:MjFkMjM5Y2I4NzEwNDk1Y2E0NjA4ZGFkZTU2NTgyODk=|74cb4a492141ff01822088156fcc683551a905fd1e28ef7cd2c6863ab710baf4"; z_c0="2|1:0|10:1502076734|4:z_c0|92:Mi4wQUVDQS1wbHp3UWtBWUFJT3RGU2xDeVlBQUFCZ0FsVk5QbXl2V1FBMFJ2Q2hUcWtZc0RfZnFMeFBtU2kyd2h2aUpn|48e75414777769fc777dc69436bb65b775a1dee04371bbde0a63af571309e238"; __utma=51854390.2140610821.1502112318.1502112318.1502112318.1; __utmc=51854390; __utmz=51854390.1502112318.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/settings/profile; __utmv=51854390.100-1|2=registration_date=20160411=1^3=entry_date=20160411=1; _xsrf=f8b3d4b8-88a0-467a-ba37-c48197fc1e76'
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


def crawl_one(url_token, db_connection):
    profile = load_profile(url_token, COOKIES_STR)
    if not profile:
        return False
    author = Author(url_token, COOKIES_STR, profile['name'], profile['gender'], profile['avatar_url_template'])
    author.load_answers()
    db_connection.save_author(author)


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
        crawl_one(args.crawl, db_connection)
    if args.find is not None:
        pprint(db_connection.find_one(args.find))
    if args.get is not None:
        result = db_connection.find_one(args.get)
        if result is None:
            crawl_one(args.get, db_connection)
            result = db_connection.find_one(args.get)
        pprint(result)
    if args.delete is not None:
        print(bool(db_connection.delete_one(args.delete)))

if __name__ == '__main__':
    main()
