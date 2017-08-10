# -*- coding=utf8 -*-

import datetime, re
from pymongo import MongoClient, ASCENDING
from author import Author

class DBConnection:
    def __init__(self, addr='localhost', port=27017, db_name='zhihutu', collection='author'):
        self.client = MongoClient(addr, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection]

    def save_author(self, author: Author):
        """
        Saved pattern:
        {
            name: "Str",  // Doesn't unique!
            url_token: "Str",
            avatar_url_template: "Str",
            gender: 0/1,
            answer_pictures: ["str", "str", ...],
            user_type: "People",
            update_time: datetime.datetime.utcnow(),
        }
        """
        MIN_VOTE_UP_COUNT = 50 # 低于此赞数的回答不保存
        author_to_save = {
            "name": author.name,
            "url_token": author.url_token,
            "avatar_url_template": author.avatar_url_template,
            "gender": author.gender,
            "user_type": author.user_type,
            "update_time": datetime.datetime.utcnow(),
            # "answer_pictures": []
        }

        pic_set = set()
        for answer in author.answers:
            if answer['voteup_count'] < MIN_VOTE_UP_COUNT:
                continue
            self._get_pic_list(answer['content'], pic_set)

        author_to_save['answer_pictures'] = list(pic_set)

        self.collection.delete_many({'url_token': author.url_token})
        self.collection.insert_one(author_to_save)

        return author.url_token

    def _get_pic_list(self, content, pic_set: set):
        for pic in re.findall(r"data-original=\"([\w./\-:]+)", content):
            pic_set.add(pic.replace('_b.', '_r.'))
        for pic in re.findall(r"data-actualsrc=\"([\w./\-:]+)", content):
            pic_set.add(pic.replace('_b.', '_r.'))
    

    def save_temp(self, url_token):
        temp_author = {
            'url_token': url_token,
            'name': 'Loading...'
        }
        return self.collection.insert_one(temp_author)


    def loading_number(self):
        return self.collection.find({'name': 'Loading...'}).count()


    def restore_url_token(self):
        result = set()
        for item in self.collection.find({}, {'url_token': 1, '_id': 0}):
            print(item)
            result.add(item['url_token'])
        return result


    def find_one(self, url_token):
        return self.collection.find_one({'url_token': url_token})

    def delete_many(self, url_token):
        result = self.collection.delete_many({'url_token': url_token})
        return result.deleted_count == 1
