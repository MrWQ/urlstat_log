#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import linecache
import os
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

requests.adapters.DEFAULT_RETRIES = 5           # 增加重连次数
results_dir = 'log'                             # 文件夹名称
url_file = 'url.txt'                            # url列表文件
platform_file = 'platform.txt'                  # 平台列表文件,url所属平台/系统
url_list = []                                   # url测试列表
platform_flag = True                            # 平台文件存在标志
platform_list = []                              # 平台列表


# 初始化
def init():
    encode_file(url_file)
    encode_file(platform_file)
    global url_list
    global platform_list
    url_list = linecache.getlines(url_file)                     # url测试列表
    platform_list = linecache.getlines(platform_file)           # 平台列表


def makedir(dir_name):
    if os.path.lexists(dir_name):
        os.chdir(dir_name)
    else:
        os.makedirs(dir_name)
        os.chdir(dir_name)


# 打印log
def log(log_file, string):
    with open(log_file, 'a', encoding='utf-8') as log_f:
        log_f.write('[{}] {}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), string))


# 将文件编码改为utf-8
# 改变文件编码utf-8 防止gbk编码文件无法打开
def encode_file(path):
    # 改变文件编码utf-8 防止gbk编码文件无法打开
    fp = open(path, 'rb')
    fps = fp.read()
    fp.close()
    try:
        fps = fps.decode('utf-8')
    except Exception as e:
        print(e)
        fps = fps.decode('gbk')
    fps = fps.encode('utf-8')
    fp = open(path, 'wb')
    fp.write(fps)
    fp.close()


def url_test():
    now = datetime.datetime.now()  # 获取当前时间对象
    name = now.strftime("%Y-%m-%d")
    log_file = name + '.log'
    log(log_file, "url_test start")
    print("url_test start")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'Connection': 'close'
    }
    if url_list == []:
        print('获取url列表失败！检查同文件夹下是否有{}，以及{}文件中是否有url'.format(url_file, url_file))
        log(log_file, '获取url列表失败！检查同文件夹下是否有{}，以及{}文件中是否有url'.format(url_file, url_file))
    else:
        for counter in range(len(url_list)):
            url = url_list[counter]
            if '://' in url:
                url = url.replace('Http://', 'http://')
                url = url.replace('Https://', 'https://')
            else:
                url = 'http://' + url
            url = url.replace('\n', '')
            url = url.replace('\t', '')
            url = url.replace(' ', '')
            # 发送请求获取状态码
            try:
                session = requests.session()
                session.keep_alive = False
                code = session.head(url=url, headers=headers, timeout=10, verify=False, allow_redirects=True).status_code
            except Exception as e:
                print(e)
                code = '超时'
            # 4xx和5xx 状态码用get方法重新请求验证，某些平台可能禁用head方法
            # 如果不为2xx,用get请求
            if str(code)[0] != '2':
                try:
                    code = session.get(url=url, headers=headers, timeout=10, verify=False).status_code
                except Exception as e:
                    print(e)
                    code = '超时'
            if platform_list[counter] and platform_list[counter] != '\n':
                print(platform_list[counter], url, code)
                # 日志记录平台、url、code
                log(log_file, platform_list[counter].strip() + '\t' + url + '\t' + str(code))

    log(log_file, "url_test end")
    print("url_test end")


if __name__ == '__main__':
    init()                  # 初始化
    makedir(results_dir)    # 创建结果文件夹,同时切换工作目录
    scheduler = BlockingScheduler()
    scheduler.add_job(url_test, 'cron', day_of_week='*', hour='*', minute='*')
    print(scheduler.get_jobs())
    scheduler.start()
