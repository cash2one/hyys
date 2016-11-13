__author__ = 'staff'

import os

def selected_news_count(data_dir):
    keyword_dirs = os.listdir(data_dir)
    news_count = 0
    for keyword_dir in keyword_dirs:
        print(keyword_dir)
        filenames = os.listdir(data_dir+'/'+keyword_dir+'/'+'news/comments/most_comments')
        news_count_set = set()
        for filename in filenames:
            if not filename.endswith('.info.json'):
                continue
            news_count_set.add(filename[:filename.rfind('_')])
        news_count += len(news_count_set)
    return news_count



if __name__ == '__main__':
    data_dir = 'E:/hyys_data/news/news_data_all'
    print(selected_news_count(data_dir))