__author__ = 'Luo-Pc'

from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import quote
from bs4 import BeautifulSoup
import gzip
import time
import os
import json
import datetime
import re
import math
import collections


def save(content, data_dir, name):
    """将内容以name命名保存在data_dir目录中"""
    file = open(data_dir + '/' + name, 'w+b')
    file.write(content)
    file.close()


def read_str(file, encoding, errors='ignore'):
    """从文件中读取数据"""
    file = open(file, 'r', encoding=encoding, errors=errors)
    data = file.read()
    file.close()
    return data


def get_timestamp_str(date_time_str):
    date_time = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
    return "%.0f" % time.mktime(date_time.timetuple())


def crawl_page(url, result_saved_dir, name, cookie=None):
    """爬取指定url的数据，并以name命名保存在result_saved_dir目录中"""
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0')
    request.add_header('Accept-Encoding', 'gzip, deflate, br')
    request.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    if cookie is not None:
        request.add_header('cookie', cookie)

    response = urlopen(request)
    data = response.read()

    if response.info()['Content-Encoding'] == 'gzip':
        save(data, result_saved_dir, name + '.zip')
        content = gzip.GzipFile(filename=result_saved_dir + '/' + name + '.zip')
        data = content.read()

    if 'text/html' in response.info()['Content-Type'].lower():
        save(data, result_saved_dir, name + '.html')
    elif 'application/javascript' in response.info()['Content-Type'].lower():
        save(data, result_saved_dir, name + '.json')

    return data, response.getheader('Set-Cookie')


def retrieval_news_from_baidu(site, keyword, start_time, end_time, max_page_count, result_saved_dir):
    """使用百度高级搜索爬取指定站点(site)、关键词（keyword)、起止时间（start_time, end_time)的搜索数据，最大爬取页面数量为
    max_page_count，将结果保存到指定目录（result_saved_dir）下"""
    result_saved_dir = result_saved_dir+'/'+keyword
    if not os.path.exists(result_saved_dir):
        os.mkdir(result_saved_dir)

    url_part1 = 'https://www.baidu.com/s?wd=site%3A%28'+site+'%29%20%22'+quote(keyword)+'%22&pn='
    url_part2 = '&oq=site%3A%28'+site+'%29%20%22'+quote(keyword)+'%22&ct=2097152&tn=baiduadv&ie=utf-8&si=%28'+\
                site+'%29&rsv_pq=c991ba4100cce1f9&rsv_t=a179fkqLua0%2B7HGfugHFNzuc9m1RyWVyPLcGUA%2F2%2FVPHceJD1eKX4ys5fQY44%2B0&'+ \
                'gpc=stf%3D'+get_timestamp_str(start_time)+'%2C'+get_timestamp_str(end_time) + '%7Cstftype%3D2&' + \
                'tfflag=1'
    (data, cookie) = crawl_page(url_part1 + str(0*10) + url_part2, result_saved_dir, str(1))
    soup = BeautifulSoup(data, 'html.parser')
    total_text = soup.select('div.head_nums_cont_inner > div.nums')[0].get_text()
    total_count = int(total_text[total_text.find('约')+1:total_text.find('个')].replace(',', ''))
    print('crawl page [%d]: site=%s, keyword=%s, start_time=%s, end_time=%s, total_result_count=%d'
          % (1, site, keyword, start_time, end_time, total_count))
    max_page_count = max_page_count if max_page_count*10 <= total_count else int((total_count-1)/10)+1
    time.sleep(3)
    for i in range(1, max_page_count):
        crawl_page(url_part1 + str(i*10) + url_part2, result_saved_dir, str(i+1))
        print('crawl page [%d]: site=%s, keyword=%s, start_time=%s, end_time=%s, total_result_count=%d'
          % (i+1, site, keyword, start_time, end_time, total_count))
        time.sleep(3)

    return result_saved_dir


def crawl_news_from_baidu_retrieval_list(retrieval_list_dir):
    """从百度检索列表中爬取新闻页面"""
    if not os.path.exists(retrieval_list_dir+'/news'):
        os.mkdir(retrieval_list_dir+'/news')
    files = os.listdir(retrieval_list_dir)
    urls = collections.OrderedDict()
    for file in files:  # 遍历所有从百度中搜索出的新闻结果，提取其中的url，使用OrderedDict保存结果，避免url重复
        if not file.endswith(".html"):
            continue
        pages = file[0:file.find('.')]
        internal_count = 0
        soup = BeautifulSoup(open(retrieval_list_dir+'/'+file, 'r', encoding='utf8'), 'html.parser')
        for element in soup.select('div.result.c-container > h3 > a'):
            internal_count += 1
            if urls.get(element['href']) is None:
                urls[element['href']] = "%s_%d" % (pages, internal_count)

    for url, name in urls.items():  # 根据检索结果中的URL，抓取其中的页面
        crawl_page(url, retrieval_list_dir+'/news', name)
        print('%s is craled: %s' % (name, url))
        time.sleep(3)
    return retrieval_list_dir+'/news'


def crawl_comments(news_list_dir):
    """爬取每条新闻的评论数量信息"""
    if not os.path.exists(news_list_dir+'/comments'):
        os.mkdir(news_list_dir+'/comments')
    files = os.listdir(news_list_dir)
    cookies = None
    for file in files:
        if not file.endswith(".html"):
            continue
        # if file >= '3_5.html':
        #    continue
        print(news_list_dir+'/'+file)
        data = read_str(news_list_dir+'/'+file, 'gb2312')
        news_id = re.findall("newsid\s*:\s*'(.+?)'\s*,", data)
        if len(news_id) == 0:
            print('skip '+file)
            continue
        news_id = news_id[0]
        channel = re.findall("channel\s*:\s*'(.+?)'\s*,", data)[0]
        comments_name = file[0:file.find('.')]
        (content, cookies) = fail_recover_crawl_comments_for_news(news_id, channel, 1, 1, news_list_dir+'/comments',
                                                     comments_name+'.info', 5, cookies)


def fail_recover_crawl_comments_for_news(news_id, channel, page, page_size, comments_saved_dir, comments_name,
                                         try_times = 5, cookies=None):
    content = None
    for i in range(1, try_times + 1):
        try:
            (content, cookies) = crawl_comments_for_news(news_id, channel, page, page_size, comments_saved_dir,
                                                     comments_name+'.info', cookies)
            json_data = read_comments(comments_saved_dir + '/' + comments_name + '.info.json')
            if json_data['result'].get('count') is None:
                print('try again')
                time.sleep(5*i)
                continue
            else:
                print(json_data['result']['count'])
                time.sleep(3*i)
                break
        except BaseException as e:
            print(e)
            if i == 4:
                exit(1)
            else:
                print('try again')
    return content, cookies


def crawl_comments_for_news(news_id, channel, page, page_size, comments_saved_dir, comments_name, cookies=None):
    url = 'http://comment5.news.sina.com.cn/page/info?format=js&channel=' +channel + '&newsid=' + news_id +\
              '&group=0&compress=1&ie=utf-8&oe=gbk&page=' + str(page)+'&page_size='+str(page_size)
    print(url)
    (content, cookies) = crawl_page(url, comments_saved_dir, comments_name, cookies)
    return content, cookies


def read_comments(file):
    json_data = read_str(file, encoding='utf8')
    json_data = json_data[json_data.find('{'):]
    json_data = json.loads(json_data)
    return json_data


def crawl_most_comments(dir):
    """爬取评论数量最高的TOP20新闻的所有评论数据"""
    if not os.path.exists(dir+'/most_comments'):
        os.mkdir(dir+'/most_comments')
    files = os.listdir(dir)
    list = []
    for file in files:
        if not file.endswith('.info.json'):
            continue
        json_data = read_comments(dir + '/' + file)
        print(file)
        try:
          list.append((file,json_data['result']['count']['show'], json_data['result']['count']['qreply'],
                    json_data['result']['count']['total'], json_data['result']['news']['newsid'],
                    json_data['result']['news']['channel']))
        except BaseException as e:
          print(e)
    list = sorted(list, key=lambda e: e[1], reverse=True)
    print('filename\tshow\tqreply\ttotal\tnewsid\tchannel')
    cookies = None
    max_num = 20 if len(list) > 20 else len(list)
    for i in range(0, max_num):
        name = list[i][0][0:list[i][0].find('.')]
        total_pages = math.ceil(list[i][1]/50)
        news_id = list[i][4]
        channel = list[i][5]
        print('%d\t%s\t%d\t%d\t%d\t%s\t%s' % (i, list[i][0], list[i][1], list[i][2], list[i][3], news_id, channel))
        for page in range(1, total_pages + 1):
            # if (i < 1) or (i == 1 and page <= 9):
            #     continue
            (content, cookies) = fail_recover_crawl_comments_for_news(news_id, channel, page, 50, dir+'/most_comments',
                                                     name + '_'+str(page), 10, cookies)


def extract_comments(dir, area_count):
    provinces = citizen.keys()
    records = []
    for file in os.listdir(dir):
        if not file.endswith('.info.json'):
            continue
        json_data = read_comments(dir + '/' + file)
        for cmnt in json_data['result']['cmntlist']:
            records.append((file, cmnt['ip'], cmnt['area'], cmnt['content'].replace('\n', ' '), cmnt['time']))
            area = cmnt['area'][0:2]
            if area in provinces:
                area_count[area] = area_count.get(area, 0) + 1
            else:
                area = cmnt['area'][0:3]
                if area in provinces:
                    area_count[area] = area_count.get(area, 0) + 1
    return records


if __name__ == '__main__':
    dir = '/home/luopc/hyys/data'
    site = 'news.sina.com.cn'
    keywords = ['南海各方行为宣言']
    start_time = '2015-01-01'
    end_time = '2015-12-31'
    max_page_count = 10

    for keyword in keywords:
        result_saved_dir = dir
        result_saved_dir = retrieval_news_from_baidu(site, keyword, start_time, end_time, max_page_count, result_saved_dir)

        result_saved_dir = dir + '/' + keyword
        crawl_news_from_baidu_retrieval_list(result_saved_dir)

        result_saved_dir = dir + '/' + keyword+'/news'
        crawl_comments(result_saved_dir)

        result_saved_dir = dir + '/'+keyword+'/news/comments'
        crawl_most_comments(result_saved_dir)

    # result_saved_dir = 'C:/Users/Luo-Pc/Desktop/abc/temp/news/news/temp/'+keyword+'/news/comments/most_comments'
    # extracted_file = 'C:/Users/Luo-Pc/Desktop/extracted_file'
    # extract_comments(result_saved_dir, extracted_file)

