# !/usr/bin/python3.4
# -*- coding: utf-8 -*-


# 百度指数的抓取
# 截图教程：http://www.myexception.cn/web/2040513.html
#
# 登陆百度地址：https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F
# 百度指数地址：http://index.baidu.com

import time
import os
import glob
import random
import numpy as np
import cv2
import urllib.parse as urlparse
from urllib.parse import urlencode
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from image_slicer import ImageSlicer


class BaiduIndexFetcher:

    DATE_FORMAT = '%Y%m%d'
    BAIDU_INDEX_URL = 'http://index.baidu.com/?tpl=trend&type=0'
    RESOURCE_DIR = 'resource/'
    DEFAULT_WORKING_DIR = 'baidu/'
    TEMPLATE = cv2.imread(RESOURCE_DIR + 'template.jpg', 0)

    def __init__(self, working_dir=DEFAULT_WORKING_DIR):
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        self.working_dir = working_dir
        self.browser = BaiduIndexFetcher.open_browser()
        self.image_slicer = ImageSlicer(working_dir)

    # 打开浏览器
    @staticmethod
    def open_browser():
        # https://passport.baidu.com/v2/?login
        url = "https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F"
        # 打开谷歌浏览器
        # Firefox()
        # Chrome()
        browser = webdriver.Chrome('./chromedriver')
        # 输入网址
        browser.get(url)

        # 找到id="TANGRAM__PSP_3__userName"的对话框
        # 清空输入框
        browser.find_element_by_id("TANGRAM__PSP_3__userName").clear()
        browser.find_element_by_id("TANGRAM__PSP_3__password").clear()

        # 输入账号密码
        # 输入账号密码
        account = []
        try:
            fileaccount = open(BaiduIndexFetcher.RESOURCE_DIR + 'account.txt')
            accounts = fileaccount.readlines()
            for acc in accounts:
                account.append(acc.strip())
            fileaccount.close()
        except Exception as err:
            print(err)
            input("请正确在account.txt里面写入账号密码")
            exit()
        browser.find_element_by_id("TANGRAM__PSP_3__userName").send_keys(account[0])
        browser.find_element_by_id("TANGRAM__PSP_3__password").send_keys(account[1])

        # 点击登陆登陆
        # id="TANGRAM__PSP_3__submit"
        browser.find_element_by_id("TANGRAM__PSP_3__submit").click()

        print("等待网址加载完毕...")

        select = input("请观察浏览器网站是否已经登陆(y/n)：")
        while 1:
            if select == "y" or select == "Y":
                print("登陆成功！")
                print("准备打开新的窗口...")
                # time.sleep(1)
                # browser.quit()
                break

            elif select == "n" or select == "N":
                selectno = input("账号密码错误请按0，验证码出现请按1...")
                # 账号密码错误则重新输入
                if selectno == "0":

                    # 找到id="TANGRAM__PSP_3__userName"的对话框
                    # 清空输入框
                    browser.find_element_by_id("TANGRAM__PSP_3__userName").clear()
                    browser.find_element_by_id("TANGRAM__PSP_3__password").clear()

                    # 输入账号密码
                    account = []
                    try:
                        fileaccount = open("../baidu/account.txt")
                        accounts = fileaccount.readlines()
                        for acc in accounts:
                            account.append(acc.strip())
                        fileaccount.close()
                    except Exception as err:
                        print(err)
                        input("请正确在account.txt里面写入账号密码")
                        exit()

                    browser.find_element_by_id("TANGRAM__PSP_3__userName").send_keys(account[0])
                    browser.find_element_by_id("TANGRAM__PSP_3__password").send_keys(account[1])
                    # 点击登陆sign in
                    # id="TANGRAM__PSP_3__submit"
                    browser.find_element_by_id("TANGRAM__PSP_3__submit").click()

                elif selectno == "1":
                    # 验证码的id为id="ap_captcha_guess"的对话框
                    input("请在浏览器中输入验证码并登陆...")
                    select = input("请观察浏览器网站是否已经登陆(y/n)：")

            else:
                print("请输入“y”或者“n”！")
                select = input("请观察浏览器网站是否已经登陆(y/n)：")

        # 最大化窗口
        browser.maximize_window()
        return browser

    @staticmethod
    def __get_date_type(input_str):
        try:
            dates = input_str.split()
            start_date = datetime.strptime(dates[0], BaiduIndexFetcher.DATE_FORMAT)
            end_date = datetime.strptime(dates[1], BaiduIndexFetcher.DATE_FORMAT)
            if start_date > end_date:
                raise AttributeError
            return '|'.join(dates), (end_date - start_date).days
        except Exception as ex:
            print('输入错误：' + ex)
            return None

    @staticmethod
    def __add_param_to_url(url, params):
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query, encoding='gbk')  # 百度使用gbk编码
        return urlparse.urlunparse(url_parts)

    def get_index(self):
        # 每个字大约占横坐标12.5这样
        # 按照字节可自行更改切割横坐标的大小rangle
        keyword = input("请输入查询关键字，按Q退出：")
        if keyword == "q" or keyword == "Q":
            self.browser.close()
            for tmp_file in glob.glob(self.working_dir + '*.png'):
                os.remove(tmp_file)
            return None

        sel = int(input("查询7天请按0，30天请按1，自定义请按2："))
        days = 7
        date_type = 12
        if sel == 0:
            days = 7
            date_type = 12
        elif sel == 1:
            days = 30
            date_type = 13
        elif sel == 2:
            date_response = None
            while date_response is None:
                sel = str(input("请输入起止日期，格式按YYMMDD，空格分隔："))
                date_response = BaiduIndexFetcher.__get_date_type(sel)
            date_type = date_response[0]
            days = date_response[1]

        city_code = input("请输入城市编号，按回车跳过：")

        index_url = self.__add_param_to_url(self.BAIDU_INDEX_URL, {'time': date_type,
                                                                   'word': keyword,
                                                                   'area': city_code})

        # 这里开始进入百度指数
        # 要不这里就不要关闭了，新打开一个窗口
        # http://blog.csdn.net/DongGeGe214/article/details/52169761
        # 新开一个窗口，通过执行js来新开一个窗口
        js = 'window.open("' + index_url + '");'
        self.browser.execute_script(js)
        # 新窗口句柄切换，进入百度指数
        # 获得当前打开所有窗口的句柄handles
        # handles为一个数组
        handles = self.browser.window_handles
        # 切换到当前最新打开的窗口
        self.browser.switch_to_window(handles[-1])

        # 等待网页加载
        time.sleep(3)
        # 滑动思路：http://blog.sina.com.cn/s/blog_620987bf0102v2r8.html
        # 滑动思路：http://blog.csdn.net/zhouxuan623/article/details/39338511
        # 向上移动鼠标80个像素，水平方向不同
        # ActionChains(browser).move_by_offset(0,-80).perform()
        # <div id="trend" class="R_paper" style="height:480px;_background-color:#fff;"><svg height="460" version="1.1" width="954" xmlns="http://www.w3.org/2000/svg" style="overflow: hidden; position: relative; left: -0.5px;">
        # <rect x="20" y="130" width="914" height="207.66666666666666" r="0" rx="0" ry="0" fill="#ff0000" stroke="none" opacity="0" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); opacity: 0;"></rect>
        # xoyelement = browser.find_element_by_xpath('//rect[@stroke="none"]')
        xoyelement = self.browser.find_elements_by_css_selector("#trend rect")[2]
        # 获得坐标长宽
        # x = xoyelement.location['x']
        # y = xoyelement.location['y']
        width = xoyelement.size['width']
        height = xoyelement.size['height']
        # 常用js:http://www.cnblogs.com/hjhsysu/p/5735339.html
        # 搜索词：selenium JavaScript模拟鼠标悬浮
        x_0 = 1
        y_0 = float(height / 2)

        # 储存数字的数组
        index = []
        # webdriver.ActionChains(driver).move_to_element().click().perform()
        # 只有移动位置xoyelement[2]是准确的
        step = (float(width) - 2) / (days-1)
        for i in range(days):
            try:
                # 坐标偏移量???
                ActionChains(self.browser).move_to_element_with_offset(xoyelement, x_0, y_0).perform()

                # 构造规则
                x_0 += step

                time.sleep(3)
                # <div class="imgtxt" style="margin-left:-117px;"></div>
                img_element = self.browser.find_element_by_xpath('//div[@id="viewbox"]')
                img_date = self.browser.find_element_by_css_selector("#viewbox .view-table-wrap")
                # 找到图片坐标
                locations = img_element.location
                # 找到图片大小
                sizes = img_element.size
                # 构造指数的位置
                rangle = (int(locations['x']), int(locations['y'] + sizes['height']/2),
                          int(locations['x'] + sizes['width']), int(locations['y'] + sizes['height']))
                # 截取当前浏览器
                path = self.working_dir + str(i)
                self.browser.save_screenshot(str(path) + ".png")
                # 打开截图切割
                img = Image.open(str(path) + ".png")
                cropped = img.crop(rangle)
                cropped.save(str(path) + ".png")

                # 将图片放大一倍
                # 原图大小73.29
                # jpgzoom = Image.open(str(path) + ".jpg")
                # (x, y) = jpgzoom.size
                # x_s = 146
                # y_s = 58
                # out = jpgzoom.resize((x_s, y_s), Image.ANTIALIAS)
                # out.save(path + 'zoom.jpg', 'png', quality=95)

                # 图像识别
                digits = self.image_slicer.pretreatment(str(i)+".png")
                number = BaiduIndexFetcher.recognize_number(digits, BaiduIndexFetcher.recognize_digit)
                index.append((img_date.text, number))

            except IndexError as err:
                print(i, err)
        return index

    def __save_digit(self, digit, digit_image):
        directory = self.working_dir + str(digit)
        if not os.path.exists(directory):
            os.makedirs(directory)
        digit_image.save(directory + '/' + str(random.randint(0, 9999)) + '.jpg')

    def get_index_from_image(self, days):
        # 储存数字的数组
        index = []
        for i in range(days):
            try:
                digits = self.image_slicer.pretreatment(str(i)+".png")
                number = BaiduIndexFetcher.recognize_number(digits, BaiduIndexFetcher.recognize_digit)
                index.append(number)
            except Exception as ex:
                print(ex)
        return index

    @staticmethod
    def recognize_number(digits, func):
        number = 0
        for digit_img in digits:
            digit = func(digit_img)
            if isinstance(digit, int):
                number = number * 10 + digit
            else:
                raise Exception("Unrecognized %s" % digit)
        return number

    @staticmethod
    def recognize_digit(digit_img):
        img_array = np.array(digit_img)
        res = cv2.matchTemplate(img_array, BaiduIndexFetcher.TEMPLATE, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        return int(min_loc[0] / 8)

if __name__ == "__main__":

    baidu_index_fetcher = BaiduIndexFetcher()
    while 1:
        index = baidu_index_fetcher.get_index()
        if index is None:
            break
        for ele in index:
            print(ele)
