__author__ = 'staff'

import csv
from pku.hyys.util import index
from pku.hyys.util.constant_data import provinces


if __name__=='__main__':
    data_dir = 'E:/hyys_data/news/news_data_all'
    baidu_index_file = 'E:/hyys_data/baidu/20160401-20160630搜索结果_converted.csv'
    baidu_index_raw_file = 'E:/hyys_data/baidu/20160401-20160630搜索结果.csv'
    with open(baidu_index_file, mode='w', encoding='GBK', newline='') as output_csv,\
        open(baidu_index_raw_file, mode='r', encoding='utf-8', newline='') as input_csv:
        writer = csv.writer(output_csv)
        reader = csv.reader(input_csv)
        header = reader.__next__()
        area_keyword_map = {}
        for record in reader:
            area_keyword_map[record[1]+'_'+record[2]] = record[3:]
        header.insert(0, 'order')
        writer.writerow(header)
        level3_cnt = 0
        for level1 in index.get_level1():
            for level2 in index.get_level2_by_level1(level1):
                for level3 in index.get_level3_by_level2(level2):
                    level3_cnt += 1
                    for keyword in index.get_keywords_by_level3(level3):
                        for province in provinces:
                            record = [level3_cnt, level3, province, keyword] + area_keyword_map[province + '_' + keyword]
                            writer.writerow(record)
