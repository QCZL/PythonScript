#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队  :  Sunniwell
# 开发人员  :  chengc
# 开发时间  :  2021/6/4 15:16
# 文件名称  :  MaoYanTop100.py
# 开发工具  :  PyCharm

import re
import time
import xlwt
import requests


class MaoYanTop100:
    def __init__(self):
        self.movies = []
        self.sess = requests.Session()
        self.re_compile = re.compile(
            r'<dd>.*?board-index.*?>(\d+)</i>.*?a href=.*?title="(.*?)".*?<img data-src="(.*?)".*?<p class="star">(.*?)</p>'
            r'.*?<p class="releasetime">(.*?)</p>.*?<i class="integer">(.*?)</i><i class="fraction">(.*?)</i>.*?</dd>',
            re.S)

    def get_page(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36'
        }
        req = requests.Request('GET', url, headers=headers)
        perpped = self.sess.prepare_request(req)
        html = self.sess.send(perpped)
        return html.text

    def parse_page(self, content):
        items = re.findall(self.re_compile, content)
        for item in items:
            movie = [item[0], item[1], item[2], item[3].replace(u'\n', u'').strip(), item[5] + item[6], item[4]]
            self.movies.append(movie)

    def get_all_page(self):
        base_url = 'https://maoyan.com/board/4?offset='
        for i in range(10):
            get_url = base_url + str(i * 10)
            content = self.get_page(get_url)
            if content != "":
                self.parse_page(content)
            time.sleep(2)
        print(self.movies)

    def save_data(self):
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet('猫眼电影Top100', cell_overwrite_ok=True)
        col = ("排名", "中文名称", "封面链接", "职员表", "评分", "上映时间")
        # 设置字体样式
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        # 设置冻结
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)  # 水平冻结

        for i in range(len(col)):
            sheet.write(0, i, col[i], style)

        for i in range(len(self.movies)):
            movie = self.movies[i]
            for j in range(len(movie)):
                sheet.write(i + 1, j, movie[j])

        book.save("猫眼电影Top100.xls")

    def startSpider(self):
        self.get_all_page()
        self.save_data()


def main():
    maoYanTop100 = MaoYanTop100()
    maoYanTop100.startSpider()


if __name__ == '__main__':
    main()
