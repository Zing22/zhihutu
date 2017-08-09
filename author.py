import requests
import json
from time import sleep

def construct_cookies(cookies_str):
    cookies = {}
    for cookie in cookies_str.replace('; ', ';').split(';'):
        (key, value) = cookie.split('=', 1)
        cookies[key] = value
    return cookies

class Author:
    "An author object represents an zhihu author"
    def __init__(self, url_token, cookies_str, name, gender, avatar_url_template="", user_type="people"):
        self.url_token = url_token # global unique!
        self.name = name
        self.gender = gender
        self.avatar_url_template = avatar_url_template
        self.user_type = user_type

        self.raw_cookies = cookies_str
        self.cookies = construct_cookies(cookies_str) # a dict storing cookies
        self.answers = [] # stores all answers of this author
        self.followees = [] # stores all followees

    def load_all(self):
        "Load all following persons and answers of this author"
        self.load_answers()
        self.load_followees()

    def _save_followees(self, followees_list):
        for followee in followees_list:
            followee_item = {
                "name": followee["name"],
                "avatar_url_template": followee["avatar_url_template"],
                "answer_count": followee["answer_count"],
                "follower_count": followee["follower_count"],
                "url_token": followee["url_token"],
                "user_type": followee["user_type"],
                "gender": followee["gender"],
            }
            self.followees.append(followee_item)

    def load_followees(self):
        "Load all following persons"
        print("Begin loading followees of {0}...".format(self.url_token))
        sleep(3)
        url = "https://www.zhihu.com/api/v4/members/{0}/followees".format(self.url_token) \
                + "?include=data%5B*%5D.answer_count%2Carticles_count%2Cuser_type%2Cgender%2Cfollower_count" \
                + "%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics" \
                + "&offset=0" \
                + "&limit=20"
        headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Connection":"keep-alive",
            "Cookie":self.raw_cookies,
            "Host":"www.zhihu.com",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        r = requests.get(url, headers=headers, cookies=self.cookies, allow_redirects=True, verify=True)
        try:
            res = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            print("Empty content... url:\n{0}".format(url))
            return False
        self._save_followees(res['data'])
        while(res['paging'] and res['paging']['is_end'] is False):
            print('Another page...')
            sleep(3) # safety
            url = res['paging']['next']
            r = requests.get(url, headers=headers, cookies=self.cookies, allow_redirects=True, verify=True)
            try:
                res = json.loads(r.text)
            except json.decoder.JSONDecodeError:
                print("Empty content... url:\n{0}".format(url))
                return False
            self._save_followees(res['data'])
        print('Done!')

    def _save_answers(self, answers_list):
        for answer in answers_list:
            answer_item = {
                "content": answer['content'],
                "id": answer['id'],
                "voteup_count": answer['voteup_count'],
                "comment_count": answer['comment_count'],
            }
            self.answers.append(answer_item)

    def load_answers(self):
        "Load all answers"
        print("Begin loading answers of {0}...".format(self.url_token))
        sleep(3)
        url = "https://www.zhihu.com/api/v4/members/{0}/answers".format(self.url_token) \
                + "?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Ccomment_count" \
                + "%2Ccontent%2Cvoteup_count%2Ccreated_time%2Cupdated_time%2Creview_info" \
                + "%2Cvoting%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.author.badge" \
                + "%5B%3F(type%3Dbest_answerer)%5D.topics" \
                + "&offset=0" \
                + "&sort_by=voteups" \
                + "&limit=20"
        headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Connection":"keep-alive",
            "Cookie":self.raw_cookies,
            "Host":"www.zhihu.com",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        r = requests.get(url, headers=headers, cookies=self.cookies, allow_redirects=True, verify=True)
        try:
            res = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            print("Empty content... url:\n{0}".format(url))
            return False
        self._save_answers(res['data'])
        while(res['paging'] and res['paging']['is_end'] is False):
            print('Another page...')
            sleep(3) # safety
            url = res['paging']['next']
            r = requests.get(url, headers=headers, cookies=self.cookies, allow_redirects=True, verify=True)
            try:
                res = json.loads(r.text)
            except json.decoder.JSONDecodeError:
                print("Empty content... url:\n{0}".format(url))
                return False
            
            self._save_answers(res['data'])
        print('Done!')


def load_profile(url_token, cookies_str):
    "Get one's profile with url_token and cookies only"
    url = "https://www.zhihu.com/api/v4/members/{0}".format(url_token)
    cookies = construct_cookies(cookies_str)
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Cookie":cookies_str,
        "Host":"www.zhihu.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    }
    r = requests.get(url, headers=headers, cookies=cookies, allow_redirects=True, verify=True)
    try:
        res = json.loads(r.text)
    except json.decoder.JSONDecodeError:
        print("Empty content... url: {0}".format(url))
        return False
    result = {
        "gender": res['gender'],
        "avatar_url_template": res['avatar_url_template'],
        "name": res['name'],
        "user_type": res['user_type'],
        "url_token": res['url_token'],
    }
    return result
