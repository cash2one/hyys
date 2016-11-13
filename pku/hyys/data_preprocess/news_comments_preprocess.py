__author__ = 'staff'

import json
import os
import csv
from pku.hyys.util import index
from pku.hyys.util.constant_data import provinces


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


def read_comments(file):
    json_data = read_str(file, encoding='utf8')
    json_data = json_data[json_data.find('{'):]
    json_data = json.loads(json_data)
    return json_data


def get_comment_region(dir_path):
    file_names = os.listdir(dir_path)
    file_names = filter(lambda x: x.endswith('.info.json'), file_names)
    region_cnt_map = {}
    for file_name in file_names:
        json_data = read_comments(dir_path + '/' + file_name)
        for cmnt in json_data['result']['cmntlist']:
            area = cmnt['area'][0:2]
            if area in provinces:
                region_cnt_map[area] = region_cnt_map.get(area, 0) + 1
            else:
                area = cmnt['area'][0:3]
                if area in provinces:
                    region_cnt_map[area] = region_cnt_map.get(area, 0) + 1
    return region_cnt_map


if __name__ == '__main__':
    data_dir = 'E:/hyys_data/news/news_data_all'
    news_comment_cnt_file = 'E:/hyys_data/news/news_comment_cnts.csv'
    with open(news_comment_cnt_file, mode='w', encoding='GBK', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(('order', 'level3', 'area', 'keyword', 'score'))
        level3_cnt = 0
        for level1 in index.get_level1():
            for level2 in index.get_level2_by_level1(level1):
                for level3 in index.get_level3_by_level2(level2):
                    print(level3)
                    level3_cnt += 1
                    for keyword in index.get_keywords_by_level3(level3):
                        cnt_map = get_comment_region(data_dir+'/'+keyword+'/news/comments/most_comments')
                        for province in provinces:
                            writer.writerow((level3_cnt, level3, province, keyword, cnt_map.get(province, 0)))
