from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import re
import time
from scraper import Scraper

BASE_URL = "https://biz.heraldcorp.com/"
URL = "https://biz.heraldcorp.com/list.php?ct=010108000000&ctv=&np="
FILENAME = "news.csv"
HEADER = ['_id',
          'sid',
          'sid2',
          'oid',
          'aid',
          'news_date',
          'category',
          'subcategory',
          'press',
          'headline',
          'summary',
          'body_raw',
          'article_date',
          'article_editdate',
          'content_url',
          'img_url',
          'insertTime']


def parseHTML(url) -> pd.DataFrame:
    buffer = BytesIO()
    test = Scraper(url)
    data = test.scrape(buffer)
    news_data = pd.DataFrame()

    soup = BeautifulSoup(data, 'html.parser')
    list = soup.find('div', class_="list_l")

    list_items = list.find_all('li')

    list_head = list.find('div', class_='list_head')

    if bool(list_head):
        article_data = pd.DataFrame({'_id': [re.search(r'(?<=ud=).*', list_head.a['href']).group()],
                                     'sid': [0],
                                     'sid2': [0],
                                     'oid': [0],
                                     'aid': [0],
                                     'news_date': [list_head.find('div', class_='list_date').text],
                                     'category': [0],
                                     'subcategory': [0],
                                     'press': [0],
                                     'headline': [list_head.find('div', class_='list_head_title').text],
                                     'summary': [list_head.find('div', class_='list_head_txt').text],
                                     'body_raw': [0],
                                     'article_date': [0],
                                     'article_editdate': [0],
                                     'content_url': [BASE_URL + list_head.a['href']],
                                     'img_url': [0],
                                     'insertTime': [0]})
        news_data = pd.concat([news_data, article_data], ignore_index=True)

    for item in list_items:
        article_data = pd.DataFrame({'_id': [re.search(r'(?<=ud=).*', item.a['href']).group()],
                                     'sid': [0],
                                     'sid2': [0],
                                     'oid': [0],
                                     'aid': [0],
                                     'news_date': [item.find('div', class_='l_date').text],
                                     'category': [0],
                                     'subcategory': [0],
                                     'press': [0],
                                     'headline': [item.find('div', class_='list_title').text],
                                     'summary': [item.find('div', class_='list_txt').text],
                                     'body_raw': [0],
                                     'article_date': [0],
                                     'article_editdate': [0],
                                     'content_url': [BASE_URL + item.a['href']],
                                     'img_url': [0],
                                     'insertTime': [0]})
        news_data = pd.concat([news_data, article_data], ignore_index=True)

    return news_data


def main():

    data = pd.DataFrame()

    for page in range(1, 3):
        single_data = parseHTML(URL + str(page))
        data = pd.concat([data, single_data], ignore_index=True)
        time.sleep(5)

    data.to_csv('data/out.csv', index=False)


if __name__ == "__main__":
    main()
