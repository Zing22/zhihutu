# -*- coding=utf8 -*-

import os
from flask import Flask, request, send_from_directory, jsonify
import zhihutu
from database import DBConnection

app = Flask(__name__, static_url_path='')
db_connection = DBConnection()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/find', methods=['POST'])
def find():
    url_token = request.form['url_token']
    result = db_connection.find_one(url_token)
    del result['_id']
    return jsonify(result)


@app.route('/get', methods=['POST'])
def get():
    url_token = request.form['url_token']
    cookies_str = request.form['cookies_str']
    return jsonify(zhihutu.get_one(url_token, db_connection, cookies_str))


if __name__ == '__main__':
    app.run(debug=True, port=7070)
