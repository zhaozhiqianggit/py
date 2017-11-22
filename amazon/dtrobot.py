#!/usr/bin/env python
# coding=utf-8



from urllib import request, parse
import json


# 自定义机器人的封装类
class DtalkRobot(object):
    """docstring for DtRobot"""
    webhook = ""

    def __init__(self, webhook):
        super(DtalkRobot, self).__init__()
        self.webhook = webhook

    # text类型
    def sendText(self, msg, isAtAll=False, atMobiles=[]):
        data = {"msgtype": "text", "text": {"content": msg}, "at": {"atMobiles": atMobiles, "isAtAll": isAtAll}}
        return self.post(data)

    # markdown类型
    def sendMarkdown(self, title, text):
        data = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
        return self.post(data)

    # link类型
    def sendLink(self, title, text, messageUrl, picUrl=""):
        data = {"msgtype": "link", "link": {"text": text, "title": title, "picUrl": picUrl, "messageUrl": messageUrl}}
        return self.post(data)

    # ActionCard类型
    def sendActionCard(self, actionCard):
        data = actionCard.getData();
        return self.post(data)

    # FeedCard类型
    def sendFeedCard(self, links):
        data = {"feedCard": {"links": links}, "msgtype": "feedCard"}
        return self.post(data)

    def post(self, data):
        post_data = json.JSONEncoder().encode(data).encode('utf-8')
        headers = {
        'Content-Type': 'application/json'
        }
        req = request.Request(self.webhook, headers=headers,data=post_data)
        content = request.urlopen(req).read()
        return content


# ActionCard类型消息结构
class ActionCard(object):
    """docstring for ActionCard"""
    title = ""
    text = ""
    singleTitle = ""
    singleURL = ""
    btnOrientation = 0
    hideAvatar = 0
    btns = []

    def __init__(self, arg=""):
        super(ActionCard, self).__init__()
        self.arg = arg

    def putBtn(self, title, actionURL):
        self.btns.append({"title": title, "actionURL": actionURL})

    def getData(self):
        data = {"actionCard": {"title": self.title, "text": self.text, "hideAvatar": self.hideAvatar,
                               "btnOrientation": self.btnOrientation, "singleTitle": self.singleTitle,
                               "singleURL": self.singleURL, "btns": self.btns}, "msgtype": "actionCard"}
        return data


# FeedCard类型消息格式
class FeedLink(object):
    """docstring for FeedLink"""
    title = ""
    picUrl = ""
    messageUrl = ""

    def __init__(self, arg=""):
        super(FeedLink, self).__init__()
        self.arg = arg

    def getData(self):
        data = {"title": self.title, "picURL": self.picUrl, "messageURL": self.messageUrl}
        return data


# 测试
# webhook = "https://oapi.dingtalk.com/robot/send?access_token=a2f6a826190492d9bfb5d944af48f6fad06aea305b6d826a6dfbbfd90f11cff7"
# if __name__ == "__main__":
#     robot = DtalkRobot(webhook)
#     robot.sendText("{'spider_name':'aaa','error_str':'eee','url':'uuu'}")
    # robot.sendLink("link类型", "link类型内容link类型内容link类型内容link类型内容link类型内容link类型内容link类型内容", "http://www.baidu.com",
    #                "http://scimg.jb51.net/allimg/160716/103-160G61012361X.jpg")
    # robot.sendMarkdown("markdown类型", "## 标题2 \n##### 标题3 \n* 第一 \n* 第二 \n\n[链接](http://www.baidu.com/) \n")

