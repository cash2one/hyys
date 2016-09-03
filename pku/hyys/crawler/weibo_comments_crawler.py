"""
本程序需要在python 2.6~2.7环境下运行，需要安装新浪微博python SDK包
"""

from weibo import APIClient
import json
import math
import os
import io
import time


def save(data, path):
    """保存数据文件"""
    file = open(path, 'w+b')
    file.write(data)
    file.close()

# 新浪微博API接口参数
APP_KEY = 'YOUR APP_KEY'
APP_SECRET = 'YOUR APP SECRET'
CALLBACK_URL = 'YOUR CALL BACK URL'

# 数据爬取相关参数
mids_file_path = 'E:/hyys_data/weibo/mids.txt'
result_saved_path = 'E:/hyys_data/weibo/comment/comments'
count_per_page = 200

# 登陆验证
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
url = client.get_authorize_url()
print('Enter following url into web browser and get the code')
print(url)
code = input('code=')
r = client.request_access_token(code)
print(r.access_token)
print(r.expires_in)
client.set_access_token(r.access_token, r.expires_in)
# client.set_access_token('2.00LDemTFUGeKZE399d9ed184WAKk7E',1629898310)

# 数据爬取
mids_file = io.open(mids_file_path, 'r', encoding='utf-8')
for line in mids_file.readlines():
    array = line.strip().split('\t')
    keyword = array[0]
    mid = array[1]
    comment_count = int(array[2])
    print(keyword+'\t'+mid+'\t'+str(comment_count))

    mid_path = result_saved_path+'/'+mid
    if not os.path.exists(mid_path):
        os.mkdir(mid_path)
    
    page_total = int(math.ceil(comment_count/float(count_per_page)))
    print(page_total)
    for i in range(1, page_total+1):
        json_path = mid_path+'/'+str(i)+'.json'
        if os.path.exists(json_path):
            if os.path.getsize(json_path) < 200:
                pass
            else:
                continue
        if i == 1:
            loop = 3
        else:
            loop = 3
        for j in range(0, loop):
            data = client.comments.show.get(id=mid,page=i, count=count_per_page)
            if len(data['comments']) > 0:
                break
            else:
                time.sleep(3)
        print(str(i)+'\t'+str(len(data['comments'])))
        if len(data['comments']) == 0:
            break
        with open(mid_path+'/'+str(i)+'.json', 'w') as fp:
            json.dump(data, fp)
        time.sleep(8)
    time.sleep(15)
mids_file.close()
