from bs4 import BeautifulSoup
from io import BytesIO
from collections import deque
import pandas as pd
import logging
import re
import time
import numpy as np
from scraper import Scraper
import utils
import queue
import threading

BASE_URL = "https://biz.heraldcorp.com/"
DATA_PATH = "data/news.csv"
LOG_PATH = "logs/" + time.strftime("HERALD_%Y-%m-%d_%H:%M:%S.log")
TARGETS = [
    {
        "category": "politics",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010108000000&np=",
    },
    {
        "category": "economy",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010104000000&np=",
    },
    {
        "category": "social",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010109000000&np=",
    },
    {
        "category": "international",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010110000000&np=",
    },
    {
        "category": "IT_science",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010107000000&np=",
    },
    {
        "category": "life_culture",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010504000000&np=",
    },
    {
        "category": "entertainment_sports",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010400000000&np=",
    },
    {
        "category": "opinion",
        "subcategory": None,
        "url": "https://biz.heraldcorp.com/list.php?ct=010103000000&np=",
    },
    {
        "category": "local_news",
        "subcategory": "honam",
        "url": "https://biz.heraldcorp.com/village/list.php?ct=011900000000&np=",
    },
    {
        "category": "local_news",
        "subcategory": "daegu_gyeongbuk",
        "url": "https://biz.heraldcorp.com/village/list.php?ct=10-&np=",
    },
]

HEADER = [
    "_id",
    "sid",
    "sid2",
    "oid",
    "aid",
    "news_date",
    "category",
    "subcategory",
    "press",
    "headline",
    "summary",
    "body_raw",
    "article_date",
    "article_editdate",
    "content_url",
    "img_url",
    "insertTime",
]


def getLinks(queue, url) -> pd.DataFrame:
    """
    Finds all news articles and stores the value in a DataFrame

    returns DataFrame
    """

    # Loop through all news pages of website
    for page in range(1, 11):
        links_page_buffer = BytesIO()
        links_page = Scraper(url + str(page))
        links_page_data = BeautifulSoup(
            links_page.scrape(links_page_buffer), "html.parser"
        )

        links_page_data = links_page_data.find("div", class_="list_l")

        list_head = links_page_data.find("div", class_="list_head")

        list = links_page_data.find_all("li")

        if bool(list_head):
            pass
        for link in list:
            pass


def main():

    link_queue = queue.Queue

    for target in TARGETS:
        thread = threading.Thread(target=getLinks, args=(link_queue, target.url))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_PATH, format="%(asctime)s %(message)s", filemode="w"
    )

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)

    logger.info("-HERALD start-")
    main()
    logger.info("-HERALD end-")
