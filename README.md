# ZhiHuTu

爬取一个知乎答主所有回答里的照片，并保存到本地MongoDB中。


## Dependencies
1. Python 3.x, with requests==2.18.2, pymongo==3.4.0
2. MongoDB v3.4.6


## Usage
修改zhihutu.py中的`COOKIES_STR`变量为你本地打开知乎页面时，Requests Headers中的Cookie字段。

在命令行中：

    python zhihutu.py -g <url_token>

抓取用户`<url_token>`的所有回答下的图片链接并输出。会在本地MongoDB下创建zhihutu/author。

点击知乎用户个人主页，在URL中可以找到`<url_token>`：

    https://www.zhihu.com/people/<url_token>/answers

其他用法：

    python zhihutu.py -h


## License

[MIT LICENSE][1]

[1]: https://raw.githubusercontent.com/Zing22/zhihutu/master/LICENSE
