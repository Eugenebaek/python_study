"""
Takes in a url and returns the contents
"""
import pycurl
from io import BytesIO
import json


class Scraper:
    def __init__(self, url) -> None:
        self.url = url

    def scrape(self, buffer):
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        return body.decode('cp949')


if __name__ == "__main__":
    buffer = BytesIO()
    test = Scraper(
        'news.naver.com/main/mainNews.naver?sid1=100&date=%2000:00:00&page=1')

    res = test.scrape(buffer)

    res_json = json.loads(res)

    res_list = res_json['airsResult']

    res_list_json = json.loads(res_list)

    res_list_res = res_list_json['result']

    for item in res_list_res['100']:
        print(item['sectionId'], item['articleId'], item['officeId'])
