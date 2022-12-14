from bs4 import BeautifulSoup
from io import BytesIO
from collections import deque
import pandas as pd
import logging
import re
import time
import json
import numpy as np
from scraper import Scraper


def NAVER_parser() -> pd.DataFrame:
    NAVER_links_DF = pd.DataFrame()
    with open('links.txt', 'w') as f:

        for category in range(100, 106):
            for page in range(1, 11):
                NAVER_page_buffer = BytesIO()
                NAVER_links_page = Scraper(
                    f'news.naver.com/main/mainNews.naver?sid1={category}&date=%2000:00:00&page={page}')
                NAVER_links_page_data_raw = NAVER_links_page.scrape(
                    NAVER_page_buffer)
                NAVER_links_page_data_json = json.loads(
                    NAVER_links_page_data_raw)
                NAVER_links_data_raw = NAVER_links_page_data_json['airsResult']
                NAVER_links_data_json = json.loads(NAVER_links_data_raw)

                NAVER_links = NAVER_links_data_json['result'][f'{category}']

                for item in NAVER_links:
                    f.write(
                        f"https://n.news.naver.com/mnews/article/{item['officeId']}/{item['articleId']}?sid={item['sectionId']}\n")

                time.sleep(2)


def main():
    NAVER_parser()


if __name__ == "__main__":
    main()
