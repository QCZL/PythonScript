#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队  :  Sunniwell
# 开发人员  :  chengc
# 开发时间  :  2021/6/2 15:02
# 文件名称  :  zolWallpaper.py
# 开发工具  :  PyCharm

import os
import requests
import urllib.error
import urllib.request
from bs4 import BeautifulSoup


def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.77 Safari/537.36"
    }
    request = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(request)
        content = response.read().decode('gb18030')
        return content
    except urllib.error.URLError as e:
        print("URLError", e)
    except urllib.error.HTTPError as e:
        print("HTTPError", e)
    except UnicodeEncodeError as e:
        print("解码错误", e)


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)


class ZolWallpaper:
    def __init__(self):
        self.base_url = "https://desk.zol.com.cn"

    def get_category_path(self):
        category = {}
        content = get_html(self.base_url)
        soup = BeautifulSoup(content, 'lxml')

        dds = soup.find('dd', class_='brand-sel-box clearfix')
        links = dds.find_all('a')[1:]
        for link in links:
            category[link.string] = link['href'].replace('/', '')

        return category

    def get_size_path(self):
        size = []
        content = get_html(self.base_url)
        soup = BeautifulSoup(content, 'lxml')

        dds = soup.find_all('dd', class_='brand-sel-box clearfix')[1]
        links = dds.find_all('a')[1:]
        for link in links:
            size.append(link['href'].replace('/', ''))

        return size


class PhotoList(ZolWallpaper):
    def __init__(self, path):
        super(PhotoList, self).__init__()
        # 获取壁纸尺寸
        self.all_size = self.get_size_path()
        # 获取壁纸分类
        self.all_category = self.get_category_path()

        # 当前壁纸尺寸
        self.now_size = ''
        # 保存根路径
        self.base_path = path
        # 当前保存路径
        self.save_path = ''

        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

    def get_album_url(self, url):
        """
        获取所有专辑地址
        :param url:
        :return:
        """
        photo_url = []
        content = get_html(url)
        soup = BeautifulSoup(content, 'lxml')

        links = soup.find_all('a', class_='pic')
        for link in links:
            photo_url.append(self.base_url + link['href'])

        return photo_url

    def get_next_page_url(self, url):
        """
        获取下一页的地址
        :param url:
        :return:
        """
        content = get_html(url)
        soup = BeautifulSoup(content, 'lxml')
        try:
            link = soup.find('a', id='pageNext')
            return self.base_url + link['href']
        except TypeError:
            return ''

    def get_album_photo_url(self, url):
        """
        获取专辑中所有图片地址
        :param url: 专辑地址
        :return:
        """
        urls = []
        content = get_html(url)
        soup = BeautifulSoup(content, 'lxml')
        ul = soup.find('ul', id='showImg')
        links = ul.find_all('a')
        for link in links:
            urls.append(self.base_url + link['href'])

        return urls

    def get_show_image_url(self, url):
        """
        获取图片显示地址
        :param url:
        :return:
        """
        content = get_html(url)
        soup = BeautifulSoup(content, 'lxml')
        try:
            link = soup.find('a', id=self.now_size)
            return self.base_url + link['href']
        except TypeError as e:
            print("当前图片没有 {} 分辨率的尺寸".format(self.now_size))
        return ''

    def get_image_url(self, url):
        """
        从图片显示地址中获取图片真实地址
        :param url: 专辑地址
        :return:
        """
        content = get_html(url)
        soup = BeautifulSoup(content, 'lxml')
        img_url = soup.find('img')['src']
        return img_url

    def save_picture(self, url):
        """
        保存图片
        :param url: 图片真实地址
        :return:
        """
        filename = os.path.basename(url)
        file_path = self.save_path + filename
        if not os.path.exists(file_path):
            try:
                response = requests.get(url, timeout=5)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print("保存图片 {} 到 {} ".format(filename, self.save_path))
            except requests.exceptions as e:
                print(e)
        else:
            print(file_path, " 已经存在")

    def spiderPhoto(self, category, size):
        # 记录当前壁纸的尺寸
        self.now_size = size
        # 构造保存路径
        self.save_path = os.path.join(self.base_path, category, size) + "\\"
        print(self.save_path)
        # 创建文件夹
        if not os.path.exists(self.save_path):
            mkdir(self.save_path)
        # 获取所有专辑地址
        tem_list = [self.base_url, self.all_category[category], size]
        root_url = "/".join(tem_list) + '/'
        while root_url != '':
            print('将要爬取的页面为 ', root_url)
            album_urls = self.get_album_url(root_url)
            for album_url in album_urls:
                print("当前爬取的专辑为 {}".format(album_url))
                # 获取专辑中所有图片的地址
                photo_urls = self.get_album_photo_url(album_url)
                for photo_url in photo_urls:
                    # 获取图片显示地址
                    show_url = self.get_show_image_url(photo_url)
                    # 获取图片的真实地址
                    if show_url != '':
                        url = self.get_image_url(show_url)
                        self.save_picture(url)
                print("专辑 {} 爬取完成".format(album_url))
            print('页面 {} 爬取完成'.format(root_url))
            root_url = self.get_next_page_url(root_url)


if __name__ == '__main__':
    photo = PhotoList(r"E:\10-我的图片\04-ZOL")
    print("壁纸分类：")
    for key in photo.all_category.keys():
        print(key, end=" ")
    print("")
    print("壁纸尺寸：")
    for size in photo.all_size:
        print(size, end=" ")
    print("")
    size = input("请输入您需要的尺寸（默认：4096x2160）").strip()
    category = input("请输入您需要的的类别（默认：模特）").strip()

    if size == "":
        size = "4096x2160"
    if category == "":
        category = "模特"

    if size not in photo.all_size:
        print("您选择的尺寸 {} 不在支持范围之内".format(size))
        exit()
    if category not in photo.all_category.values():
        print("您选择的类别 {} 不在支持范围之内".format(category))
        exit()

    print("您的选择为 {} {}, 即将为您爬取相关内容".format(category, size))
    photo.spiderPhoto(category, size)
