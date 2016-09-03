__author__ = 'staff'

"""
将标准化后的数据合并，以便求整体得分
"""


import csv
from pku.hyys.util import index
from pku.hyys.util.constant_data import provinces


def read_standardized_data(file_path):
    data = {}
    with open(file_path, mode='r', encoding='GBK') as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            data[row['level3']+'_'+row['keyword']+'_'+row['area']] = row
    return data


def get_rows(baidu_std_data, news_std_data, weibo_std_data, level3, keyword, province):
    rows = []
    baidu_row = baidu_std_data.get(level3+'_'+keyword+'_'+province)
    if baidu_row is not None:
        rows.append(baidu_row)
    news_row = news_std_data.get(level3+'_'+keyword+'_'+province)
    if news_row is not None:
        rows.append(news_row)
    weibo_row = weibo_std_data.get(level3+'_'+keyword+'_'+province)
    if weibo_row is not None:
        rows.append(weibo_row)
    return rows


def get_avg(rows, field):
    score = 0
    for row in rows:
        score += float(row[field])
    return score/len(rows)


if __name__=='__main__':
    baidu_standardized_file = 'E:/hyys_data/baidu/_compute/baid_search_20150701_20160630_avg_standardized.csv'
    news_standardized_file = 'E:/hyys_data/news/_compute/news_comment_cnts_standardized.csv'
    weibo_standardized_file = 'E:/hyys_data/weibo/_compute/weibo_comment_cnt_standardized.csv'
    all_merged_file = 'E:/hyys_data/_all/_compute/merged.csv'

    baidu_std_data = read_standardized_data(baidu_standardized_file)
    news_std_data = read_standardized_data(news_standardized_file)
    weibo_std_data = read_standardized_data(weibo_standardized_file)

    with open(all_merged_file, mode='w', encoding='GBK', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(('order', 'level3', 'area', 'keyword', 'score_std', 'score_avg_std', 'score_weight'))
        level3_cnt = 0
        for level1 in index.get_level1():
            for level2 in index.get_level2_by_level1(level1):
                for level3 in index.get_level3_by_level2(level2):
                    level3_cnt += 1
                    for keyword in index.get_keywords_by_level3(level3):
                        for province in provinces:
                            rows = get_rows(baidu_std_data, news_std_data, weibo_std_data, level3, keyword, province)
                            writer.writerow((level3_cnt, level3, province, keyword,
                                             get_avg(rows, 'score_std'),
                                             get_avg(rows, 'score_avg_std'),
                                             get_avg(rows, 'score_weight')))
