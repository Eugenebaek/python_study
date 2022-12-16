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

BASE_URL = "https://biz.heraldcorp.com/"
DATA_PATH = "data/news.csv"
LOG_PATH = "logs/" + time.strftime("HERALD_%Y-%m-%d_%H:%M:%S.log")
TARGETS = [
    {
        "category": "politics",
        "subcategory": None,
        "url": "list.php?ct=010108000000",
    },
    {
        "category": "economy",
        "subcategory": None,
        "url": "list.php?ct=010104000000",
    },
    {
        "category": "social",
        "subcategory": None,
        "url": "list.php?ct=010109000000",
    },
    {
        "category": "international",
        "subcategory": None,
        "url": "list.php?ct=010110000000",
    },
    {
        "category": "IT_science",
        "subcategory": None,
        "url": "list.php?ct=010107000000",
    },
    {
        "category": "life_culture",
        "subcategory": None,
        "url": "list.php?ct=010504000000",
    },
    {
        "category": "entertainment_sports",
        "subcategory": None,
        "url": "list.php?ct=010400000000",
    },
    {
        "category": "opinion",
        "subcategory": None,
        "url": "list.php?ct=010103000000",
    },
    {
        "category": "local_news",
        "subcategory": "honam",
        "url": "village/list.php?ct=011900000000",
    },
    {
        "category": "local_news",
        "subcategory": "daegu_gyeongbuk",
        "url": "village/list.php?ct=10-",
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


def getLinks() -> pd.DataFrame:
    """
    Finds all news articles and stores the value in a DataFrame

    returns DataFrame
    """

    links_DF = pd.DataFrame()

    # Loop through all news pages of website
    for target in TARGETS:
        for page in range(1, 11):
            links_page_buffer = BytesIO()
            links_page = Scraper(f'{BASE_URL}{target["url"]}&np={str(page)}')
            links_page_data = BeautifulSoup(
                links_page.scrape(links_page_buffer), "html.parser"
            )

            links_page_data = links_page_data.find("div", class_="list_l")

            list_head = links_page_data.find("div", class_="list_head")

            list = links_page_data.find_all("li")

            if bool(list_head):
                link_head_DF = pd.DataFrame(
                    {
                        "sid": [target["category"]],
                        "sid2": [target["subcategory"]],
                        "oid": ["016"],
                        "aid": [re.search(r"(?<=ud=).*", list_head.a["href"]).group()],
                        "news_date": [list_head.find("div", class_="list_date").text],
                        "category": [target["category"]],
                        "subcategory": [target["subcategory"]],
                        "press": ["헤럴드경제"],
                        "headline": [
                            list_head.find("div", class_="list_head_title").text
                        ],
                        "summary": [list_head.find("div", class_="list_head_txt").text],
                        "body_raw": [None],
                        "article_date": [None],
                        "article_editdate": [None],
                        "content_url": [BASE_URL + list_head.a["href"]],
                        "img_url": [
                            list_head.find("div", class_="list_head_img").img["src"]
                            if list_head.find("div", class_="list_head_img")
                            else None
                        ],
                    }
                )
            links_DF = pd.concat([links_DF, link_head_DF], ignore_index=True)

            for link in list:
                link_DF = pd.DataFrame(
                    {
                        "sid": [target["category"]],
                        "sid2": [target["subcategory"]],
                        "oid": ["016"],
                        "aid": [re.search(r"(?<=ud=).*", link.a["href"]).group()],
                        "news_date": [link.find("div", class_="l_date").text],
                        "category": [target["category"]],
                        "subcategory": [target["subcategory"]],
                        "press": ["헤럴드경제"],
                        "headline": [link.find("div", class_="list_title").text],
                        "summary": [link.find("div", class_="list_txt").text],
                        "body_raw": [None],
                        "article_date": [None],
                        "article_editdate": [None],
                        "content_url": [BASE_URL + link.a["href"]],
                        "img_url": [
                            link.find("div", class_="list_img").img["src"]
                            if link.find("div", class_="list_img")
                            else None
                        ],
                    }
                )
                links_DF = pd.concat([links_DF, link_DF], ignore_index=True)

    time.sleep(2)
    return links_DF


def main():
    news_DF = getLinks()
    logger.info("retrieved " + str(news_DF.shape[0]) + " links")

    logger.info("Start Scraping")

    utils.printProgressBar(
        0, news_DF.shape[0], prefix="Progress:", suffix="Complete", length=50
    )

    for i, link in enumerate(news_DF["content_url"]):

        page_buffer = BytesIO()
        page = Scraper(link)
        page_data = BeautifulSoup(page.scrape(page_buffer), "html.parser")

        news_DF.loc[news_DF["content_url"] == link, "body_raw"] = str(
            page_data.find("div", id="articleText")
        )

        logger.info("Processed " + link)
        utils.printProgressBar(
            i + 1, news_DF.shape[0], prefix="Progress:", suffix="Complete", length=50
        )
        time.sleep(2)

    news_DF.to_csv(DATA_PATH, index=False)
    logger.info("End Scraping")


if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_PATH, format="%(asctime)s %(message)s", filemode="w"
    )

    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)

    logger.info("-SCRAPPY start-")
    main()
    logger.info("-SCRAPPY end-")
