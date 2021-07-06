#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队  :  Sunniwell
# 开发人员  :  chengc
# 开发时间  :  2021/5/28 14:13
# 文件名称  :  main.py
# 开发工具  :  PyCharm

import re
import xlwt
import urllib.request
import urllib.error
from bs4 import BeautifulSoup


class DouBanMovie:
    def __init__(self):
        self.text = ""

        # 评分
        self.find_score = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>', re.S)
        # 评分人数
        self.find_rating_num = re.compile(r'<span>(\d*)人评价</span>', re.S)
        # 图片链接
        self.find_image_link = re.compile(r'<img.*src="(.*?)".*/>', re.S)
        # 视频链接
        self.find_movie_link = re.compile(r'<a class="" href="(.*?)">', re.S)
        # 电影名称
        self.find_movie_title = re.compile(r'<span class="title">(.*?)</span>', re.S)
        self.find_other_title = re.compile(r'<span class="other">(.*?)</span>', re.S)
        # 评语
        self.find_comment = re.compile(r'<span class="inq">(.*?)</span>', re.S)
        # 演职员
        self.find_actor = re.compile(r'<p class="">(.*?)</p>', re.S)
        # 排名
        self.find_rank = re.compile(r'<em class="">(\d*)</em>', re.S)

    def setText(self, text):
        self.text = text

    def getImageLink(self):
        image_link = re.findall(self.find_image_link, self.text)
        return image_link[0]

    def getMovieLink(self):
        movie_link = re.findall(self.find_movie_link, self.text)
        return movie_link[0]

    def getChineseTitle(self):
        content = re.findall(self.find_movie_title, self.text)
        try:
            title = content[0]
            title = title.replace(u'\xa0', u'')
            title = title.replace('/', '')
            return title
        except IndexError:
            return ""

    def getEnglishTitle(self):
        content = re.findall(self.find_movie_title, self.text)
        try:
            title = content[1]
            title = title.replace(u'\xa0', u'')
            title = title.replace('/', '')
            return title
        except IndexError:
            return ""

    def getOtherTitle(self):
        content = re.findall(self.find_other_title, self.text)
        try:
            title = content[0]
            title = title.replace(u'\xa0', u'')
            title = title.replace('/', '')
            return title
        except IndexError:
            return ""

    def getRating(self):
        rating = re.findall(self.find_score, self.text)
        try:
            return rating[0]
        except IndexError:
            return 0

    def getRatingNumber(self):
        rating_num = re.findall(self.find_rating_num, self.text)
        try:
            return rating_num[0]
        except IndexError:
            return 0

    def getComment(self):
        content = re.findall(self.find_comment, self.text)
        try:
            comment = content[0]
            comment = comment.replace("。", "")
            return comment
        except IndexError:
            return ""

    def getActor(self):
        content = re.findall(self.find_actor, self.text)
        try:
            actor = content[0]
            actor = actor.replace(u'\n', u'')
            actor = actor.replace(u'\xa0', u'')
            actor = re.sub(r"<br(\s+)?/>(\s+)?", "", actor)
            return actor.strip()
        except IndexError:
            return ""

    def getRank(self):
        content = re.findall(self.find_rank, self.text)
        try:
            rank = content[0]
            return rank
        except IndexError:
            return 0


def getHtmlData(url):
    text = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    }
    try:
        request = urllib.request.Request(url=url, headers=headers)
        html = urllib.request.urlopen(request)
        text = html.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'status'):
            print(e.status)
    return text


def saveDataToExcel(data_list, save_path):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)
    col = ("排名", "中文名称", "外文名称", "其他名称", "电影链接", "封面链接", "评分", "评分人数", "评语", "职员表")
    # 设置字体样式
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font
    # 设置冻结
    sheet.set_panes_frozen(True)
    sheet.set_horz_split_pos(1)  # 水平冻结
    # sheet.set_vert_split_pos(1)  # 垂直冻结
    for i in range(len(col)):
        sheet.write(0, i, col[i], style)

    for i in range(len(data_list)):
        data = data_list[i]
        for j in range(len(data)):
            sheet.write(i + 1, j, data[j])

    try:
        book.save(save_path)
    except PermissionError:
        print("文件被占用...")


def main():
    data_list = []
    save_path = "豆瓣电影Top250.xls"
    dbm = DouBanMovie()
    baseUrl = "https://movie.douban.com/top250?start="
    for i in range(0, 10):
        url = baseUrl + str(i * 25)
        html = getHtmlData(url)

        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all('div', class_='item')
        for item in items:
            data = []
            dbm.setText(str(item))
            data.append(dbm.getRank())
            data.append(dbm.getChineseTitle())
            data.append(dbm.getEnglishTitle())
            data.append(dbm.getOtherTitle())
            data.append(dbm.getMovieLink())
            data.append(dbm.getImageLink())
            data.append(dbm.getRating())
            data.append(dbm.getRatingNumber())
            data.append(dbm.getComment())
            data.append(dbm.getActor())

            data_list.append(data)

    saveDataToExcel(data_list, save_path)


if __name__ == '__main__':
    main()
