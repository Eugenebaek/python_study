from bs4 import BeautifulSoup
from io import BytesIO
from collections import deque
import pandas as pd
import logging
import re
import time
import numpy as np
from scraper import Scraper

BASE_URL = "https://biz.heraldcorp.com/"
URL = "https://biz.heraldcorp.com/list.php?ct=010108000000&ctv=&np="
DATA_PATH = "data/news.csv"
LOG_PATH = "logs/" + time.strftime('SCRAPPY_%Y-%m-%d_%H:%M:%S.log')
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
    for page in range(1, 11):
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
                                         'img_url': [list_head.find('div', class_='list_head_img').img['src'] if list_head.find('div', class_='list_head_img') else np.nan],
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
                                    'img_url': [link.find('div', class_='list_img').img['src'] if link.find('div', class_='list_img') else np.nan],
                                    'insertTime': [np.nan]})
            links_DF = pd.concat([links_DF, link_DF], ignore_index=True)

    time.sleep(2)
    return links_DF

# Print iterations progress


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def main():
    news_DF = getLinks()
    logger.info("retrieved " + str(news_DF.shape[0]) + " links")

    logger.info("Start Scraping")

    printProgressBar(
        0, news_DF.shape[0], prefix='Progress:', suffix='Complete', length=50)

    for i, link in enumerate(news_DF['content_url']):

        page_buffer = BytesIO()
        page = Scraper(link)
        page_data = BeautifulSoup(
            page.scrape(page_buffer), 'html.parser')

        news_DF.loc[news_DF['content_url'] == link,
                    'body_raw'] = str(page_data.find('div', id='articleText'))

        logger.info("Processed " + link)
        printProgressBar(i + 1, news_DF.shape[0], prefix='Progress:',
                         suffix='Complete', length=50)
        time.sleep(2)

    news_DF.to_csv(DATA_PATH, index=False)
    logger.info("End Scraping")


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_PATH,
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)

    logger.info("-SCRAPPY start-")
    main()
    logger.info("-SCRAPPY end-")
