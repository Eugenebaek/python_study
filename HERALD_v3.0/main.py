import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup

BASE_URL = "https://biz.heraldcorp.com/"
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


async def scrape_urls(url):

    page_urls = []

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
                page_urls.append(news_url)

            for link in list:
                news_slug = link.a["href"]
                news_url = f"https://biz.heraldcorp.com/{news_slug}"
                page_urls.append(news_url)

            return page_urls


async def create_url_list():

    tasks = []
    for target in TARGETS:
        for page in range(1, PAGE_LIMIT + 1):
            task = asyncio.create_task(
                scrape_urls(f'{BASE_URL}{target["url"]}&np={str(page)}')
            )
            tasks.append(task)

    list = await asyncio.gather(*tasks)

    list_flatten = [item for sublist in list for item in sublist]
    return list_flatten


if __name__ == "__main__":
    # Create list of news article URLs
    url_list = asyncio.run(create_url_list())
