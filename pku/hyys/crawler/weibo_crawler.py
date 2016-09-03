__author__ = 'luopc'

"""
抓取新浪微博数据：根据关键词搜索微博，爬取所有能够浏览到的检索页面，并提取评论数量最高的TOP20微博
"""

from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import quote
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
import gzip
import json
import os
import time


def save(data, path):
    """保存数据至文件"""
    file = open(path, 'w+b')
    file.write(data)
    file.close()


def read_str(file, encoding='utf-8', errors='ignore'):
    """从文件中读取数据"""
    file = open(file, 'r', encoding=encoding)
    data = file.read()
    file.close()
    return data


class Weibo:
    """微博类"""

    def __init__(self, cookie, save_path):
        """先在浏览器中登陆，然后将cookie取出，作为Weibo类的初始参数，数据爬取结果保存在save_path路径下"""
        self.cookie = cookie
        self.content = None
        self.save_path = save_path

    def crawl(self, keyword, time_start, time_end):
        """根据指定起止时间和关键词爬取新浪微博检索页面"""
        result_saved_dir = self.save_path+'/'+keyword
        if not os.path.exists(result_saved_dir):
            os.mkdir(result_saved_dir)
        next_page_num = 1
        next_page_link = 'http://s.weibo.com/weibo/'\
                         + quote(keyword) \
                         + '&typeall=1&suball=1&timescope=custom:'+time_start+':'+time_end+'&Refer=g'
        previous_link = 'http://s.weibo.com/'
        while next_page_num is not None:
            if os.path.exists(result_saved_dir+'/'+str(next_page_num)+'.html') and \
                            os.path.getsize(result_saved_dir+'/'+str(next_page_num)+'.html') > 2048:
                next_page_num, next_page_link, weibo_list = self.parser(result_saved_dir+'/'+str(next_page_num)+'.html',
                                                                        next_page_num)
            else:
                html_path = self.request_page(next_page_num, next_page_link, previous_link, result_saved_dir)
                previous_link = next_page_link
                next_page_num, next_page_link, weibo_list = self.parser(html_path, next_page_num)
                if next_page_num is None and next_page_link is not None:
                    s = input('Continue?')
                time.sleep(15)

    def request_page(self, page_num, page_link, referer, result_saved_dir):
        """请求一个检索页面"""
        print(page_link)
        request = Request(page_link)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:47.0) Gecko/20100101 Firefox/47.0')
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_header('Referer', referer)
        request.add_header('Cookie', self.cookie)

        zip_path = result_saved_dir+'/'+str(page_num)+'.zip'
        html_path = result_saved_dir+'/'+str(page_num)+'.html'

        response = urlopen(request)
        data = response.read()
        save(data, zip_path)
        unzipped = gzip.GzipFile(zip_path)
        save(unzipped.read(), html_path)
        return html_path

    def request_img(self, link, referer, result_saved_dir):
        """需要验证码输入时爬取图片，验证码功能未完全实现"""
        request = Request(link)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:47.0) Gecko/20100101 Firefox/47.0')
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_header('Referer', referer)
        request.add_header('Cookie', self.cookie)

        img_path = result_saved_dir+'/img.png'

        response = urlopen(request)
        data = response.read()
        save(data, img_path)

    def parser(self, file_path, page_num):
        """解析一个检索页面"""
        if os.path.getsize(file_path) < 2048:
            data = read_str(file_path, encoding='gbk')
        else:
            data = read_str(file_path)
        soup = BeautifulSoup(data, 'html.parser')
        next_page_num = None
        next_page_link = None
        weibo_list = []
        for node in soup.select('script'):
            text = node.get_text()
            if '"pid":"pl_common_sassfilter"' in text:
                js = json.loads(text[text.index('(')+1:text.rindex(')')])
                html_soup = BeautifulSoup(js['html'], 'html5lib')
                img_soup = html_soup.select('span.code_img > img')
                print(len(img_soup))
                next_page_link = 'http://s.weibo.com'+img_soup[0]['src']
            if text.strip().startswith('location.replace'):
                next_page_link = text[text.index('"')+1:text.rindex('"')]
                next_page_num = page_num
            if '"pid":"pl_weibo_direct"' in text:
                js = json.loads(text[text.index('(')+1:text.rindex(')')])
                # print(js['html'])
                html_soup = BeautifulSoup(js['html'], 'html5lib')
                next_page_soup = html_soup.select('a.page.next.S_txt1.S_line1')
                if len(next_page_soup) > 0:
                    next_page_link = 'http://s.weibo.com'+next_page_soup[0]['href']
                    next_page_num = parse_qs(next_page_soup[0]['href'])['page'][0]
                for element in html_soup.select('.WB_cardwrap.S_bg2.clearfix > div[mid]'):
                    content_soup = element.select('.feed_content.wbcon > .comment_txt')
                    time_soup = element.select('.feed_from.W_textb > .W_textb')
                    forward = ''
                    comment = ''
                    praise = ''
                    for feed_soup in element.select('.feed_action_info.feed_action_row4 > li > a'):
                        text = feed_soup.get_text().strip()
                        if text == "收藏":
                            continue
                        elif text.startswith("转发"):
                            forward = text[2:]
                        elif text.startswith("评论"):
                            comment = text[2:]
                        elif len(text) > 0 and feed_soup['title'] == '赞':
                            praise = text
                    if len(forward.strip()) == 0:
                        forward = '0'
                    if len(comment.strip()) == 0:
                        comment = '0'
                    if len(praise.strip()) == 0:
                        praise = '0'
                    weibo_list.append((element['mid'], time_soup[0].get_text(), int(forward), int(comment), int(praise),
                                     content_soup[0].get_text().strip()))
        return next_page_num, next_page_link, weibo_list

    def extract_top_20_mids(self, dir_path, mids_saved_path):
        """提取每个检索词结果列表中，评论数据量TOP20的微博ID"""
        dir_names = os.listdir(dir_path)
        output = open(mids_saved_path, 'w', encoding='utf-8')
        for dir_name in dir_names:
            print(dir_name)
            file_names = os.listdir(dir_path+'/'+dir_name)
            file_names = filter(lambda f: f.endswith('html'), file_names)
            file_names = sorted(file_names, key=lambda x: int(x[:x.index('.')]), reverse=False)
            mids = {}
            for file_name in file_names:
                next_page_num, next_page_link, weibo_list = self.parser(dir_path+'/'+dir_name+'/'+file_name, None)
                for weibo in weibo_list:
                    if weibo[3] > 0:
                        mids[weibo[0]] = weibo[3]
            count = 0
            for mid in sorted(mids.items(), key=lambda x: x[1], reverse=True):
                output.write(dir_name+'\t'+mid[0]+'\t'+str(mid[1])+'\n')
                count += 1
                if count >= 20:
                    break
        output.close()


if __name__ == '__main__':
    cookie = 'SWB=usrmdinst_20; _s_tentry=-; Apache=2041445244019.735.1472007791393; SINAGLOBAL=2041445244019.735.1472007791393; ULV=1472007791404:1:1:1:2041445244019.735.1472007791393:; WBtopGlobal_register_version=8c1e1b02173542d7; SUB=_2A256uX70DeTxGeRI41MS8SbKyT6IHXVZz9c8rDV8PUNbmtBeLUqkkW9Pxf2V7iqwsbTAut19Ke6PCQd79w..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF6KoPFZ4yRDM7j8jzY2E9b5JpX5K2hUgL.Fozc1h20eKnceoz2dJLoIEBLxK-L1KnL1h.LxK.L1K.LBo-LxK.L1-2L1K5LxKnL1h5L1h-t; SUHB=00xYrXanrjlrNN; ALF=1472612634; SSOLoginState=1472007844; un=13521610273;'
    save_dir = 'E:/hyys_data/weibo'
    start = '2015-07-01-0'
    end = '2016-06-30-23'
    client = Weibo(cookie, save_dir)
    keywords = ['悉尼歌剧院']
    for keyword in keywords:
        print(keyword)
        client.crawl(keyword, start, end)
        time.sleep(60*3)
    # client.request_img(client.parser('E:/hyys_data/weibo/龙王庙/40.html')[1], 'http://s.weibo.com', 'E:/hyys_data/weibo')
    client.extract_top_20_mids('E:/hyys_data/weibo/data_localhost', 'E:/hyys_data/weibo/mids.txt')

