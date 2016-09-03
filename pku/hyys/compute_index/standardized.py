import pandas as pd
import numpy as np
from pandas import Series

"""
将原始数据标准化（包括求网民人均值）
"""

def add_divided_by_cybercitizen(data_frame, cybercitizen_frame):
    data_avg_frame = pd.merge(data_frame, cybercitizen_frame, on='area')
    data_avg_frame = pd.concat([data_avg_frame, data_avg_frame['score']/data_avg_frame['population']], axis=1)
    data_avg_frame.columns = ['order', 'level3', 'area', 'keyword', 'score', 'population', 'score_avg']
    return data_avg_frame


def add_standardized(data_frame, column_name, new_column_name):
    standardized = data_frame[column_name].groupby([data_frame['level3'],data_frame['keyword']]).apply(lambda x:x/np.max(x))
    standardized.name = new_column_name
    data_frame = pd.concat([data_frame, standardized], axis=1)
    return data_frame


def add_weight_score(data_frame):
    weight_score = 0.5*data_frame['score_std']+0.5*data_frame['score_avg_std']
    weight_score.name = 'score_weight'
    data_frame = pd.concat([data_frame, weight_score], axis=1)
    return data_frame


def standardized(file_path):
    data = pd.read_csv(file_path, encoding='GBK')
    # add average data
    data = add_divided_by_cybercitizen(data, cybercitizen)
    # standardized
    data = add_standardized(data, 'score', 'score_std')
    data = add_standardized(data, 'score_avg', 'score_avg_std')
    data = add_weight_score(data)
    return data


if __name__ == '__main__':
    data_file_path = 'news_comment_cnts.csv'
    cybercitizen_file_path = 'cybercitizen.xlsx'

    cybercitizen = pd.read_excel(cybercitizen_file_path)
    data = standardized(data_file_path)
    data.to_csv('news_comment_cnts_standardized.csv', encoding='GBK')
