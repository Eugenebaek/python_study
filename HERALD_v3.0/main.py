import asyncio
import time
import aiohttp
import re
from bs4 import BeautifulSoup

BASE_URL = "https://biz.heraldcorp.com/"
SAMPLE_ARTICLE = "https://biz.heraldcorp.com/view.php?ud=20221223000069"
PAGE_LIMIT = 1
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


async def scrape_article(article):
    pass


async def scrape_urls(url, category, subcategory):

    articles = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            body = await response.text()
            data = BeautifulSoup(body, "html.parser")
            links_page = data.find("div", class_="list_l")

            list_head = links_page.find("div", class_="list_head")
            list = links_page.find_all("li")

            if bool(list_head):

                news_slug = list_head.a["href"]
                news_url = f"https://biz.heraldcorp.com/{news_slug}"

                article_date = list_head.find("div", class_="list_date").text
                news_date = article_date.split()[0].replace(".", "")

                headline = list_head.find("div", class_="list_head_title").text

                article_dict = {
                    "sid": category,
                    "sid2": subcategory,
                    "oid": "016",
                    "aid": re.search(r"(?<=ud=).*", news_slug).group(),
                    "news_date": news_date,
                    "category": category,
                    "subcategory": subcategory,
                    "press": "헤럴드경제",
                    "headline": headline,
                    "summary": None,
                    "body_raw": None,
                    "article_date": article_date,
                    "article_editdate": None,
                    "content_url": news_url,
                    "img_url": None,
                }

                articles.append(article_dict)

            for link in list:
                news_slug = link.a["href"]
                news_url = f"https://biz.heraldcorp.com/{news_slug}"

                article_date = link.find("div", class_="l_date").text
                news_date = article_date.split()[0].replace(".", "")

                headline = link.find("div", class_="list_title").text

                article_dict = {
                    "sid": category,
                    "sid2": subcategory,
                    "oid": "016",
                    "aid": re.search(r"(?<=ud=).*", news_slug).group(),
                    "news_date": news_date,
                    "category": category,
                    "subcategory": subcategory,
                    "press": "헤럴드경제",
                    "headline": headline,
                    "summary": None,
                    "body_raw": None,
                    "article_date": article_date,
                    "article_editdate": None,
                    "content_url": news_url,
                    "img_url": None,
                }

                articles.append(article_dict)

            return articles


async def create_article_list():

    tasks = []
    for target in TARGETS:
        for page in range(1, PAGE_LIMIT + 1):
            task = asyncio.create_task(
                scrape_urls(
                    f'{BASE_URL}{target["url"]}&np={str(page)}',
                    target["category"],
                    target["subcategory"],
                )
            )
            tasks.append(task)

    list = await asyncio.gather(*tasks)

    list_flatten = [item for sublist in list for item in sublist]
    return list_flatten


if __name__ == "__main__":
    # Create list of news article
    article_list = asyncio.run(create_article_list())

    # Fetch information of each article
