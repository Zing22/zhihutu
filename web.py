# -*- coding=utf8 -*-


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
    cookies_str = request.form['cookies_str'] # optional param

    result = db_connection.find_one(url_token)
    if result is None:
        if len(cookies_str) == 0:
            return jsonify({'name': 'Not Found'})
        result = zhihutu.get_one(url_token, db_connection, cookies_str)

    if '_id' in result:
        result.pop('_id')

    return jsonify(result)


@app.route('/delete/<url_token>', methods=['GET'])
def delete(url_token):
    return jsonify(db_connection.delete_many(url_token))


if __name__ == '__main__':
    app.run(debug=True, port=7070, threaded=True)
