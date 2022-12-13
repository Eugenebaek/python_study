from bs4 import BeautifulSoup
from io import BytesIO
from collections import deque
import pandas as pd
import re
import time
import numpy as np
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


def getLinks() -> pd.DataFrame:
    """
    Finds all news articles and stores the value in a DataFrame

    returns DataFrame
    """

    links_DF = pd.DataFrame()

    # Loop through all news pages of website
    for page in range(1, 3):
        links_page_buffer = BytesIO()
        links_page = Scraper(URL + str(page))
        links_page_data = BeautifulSoup(
            links_page.scrape(links_page_buffer), 'html.parser')

        links_page_data = links_page_data.find('div', class_='list_l')

        list_head = links_page_data.find('div', class_='list_head')

        list = links_page_data.find_all('li')

        if bool(list_head):
            link_head_DF = pd.DataFrame({'_id': [re.search(r'(?<=ud=).*', list_head.a['href']).group()],
                                         'sid': [np.nan],
                                         'sid2': [np.nan],
                                         'oid': [np.nan],
                                         'aid': [np.nan],
                                         'news_date': [list_head.find('div', class_='list_date').text],
                                         'category': [np.nan],
                                         'subcategory': [np.nan],
                                         'press': [np.nan],
                                         'headline': [list_head.find('div', class_='list_head_title').text],
                                         'summary': [list_head.find('div', class_='list_head_txt').text],
                                         'body_raw': [np.nan],
                                         'article_date': [np.nan],
                                         'article_editdate': [np.nan],
                                         'content_url': [BASE_URL + list_head.a['href']],
                                         'img_url': [np.nan],
                                         'insertTime': [np.nan]})
        links_DF = pd.concat([links_DF, link_head_DF], ignore_index=True)

        for link in list:
            link_DF = pd.DataFrame({'_id': [re.search(r'(?<=ud=).*', link.a['href']).group()],
                                    'sid': [np.nan],
                                    'sid2': [np.nan],
                                    'oid': [np.nan],
                                    'aid': [np.nan],
                                    'news_date': [link.find('div', class_='l_date').text],
                                    'category': [np.nan],
                                    'subcategory': [np.nan],
                                    'press': [np.nan],
                                    'headline': [link.find('div', class_='list_title').text],
                                    'summary': [link.find('div', class_='list_txt').text],
                                    'body_raw': [np.nan],
                                    'article_date': [np.nan],
                                    'article_editdate': [np.nan],
                                    'content_url': [BASE_URL + link.a['href']],
                                    'img_url': [np.nan],
                                    'insertTime': [np.nan]})
            links_DF = pd.concat([links_DF, link_DF], ignore_index=True)

    time.sleep(2)
    return links_DF


def main():
    news_DF = getLinks()

    for data in news_DF.loc[news_DF[]]:
        page_buffer = BytesIO()
        page = Scraper(link)
        page_data = BeautifulSoup(
            page.scrape(page_buffer), 'html.parser')

        time.sleep(2)


if __name__ == "__main__":
    main()
