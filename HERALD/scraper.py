"""
Takes in a url and returns the html contents
"""
import pycurl
from io import BytesIO


class Scraper:
    def __init__(self, url) -> None:
        self.url = url

    def scrape(self, buffer):
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        return body.decode('utf-8')


if __name__ == "__main__":
    buffer = BytesIO()
    test = Scraper(
        'https://biz.heraldcorp.com/list.php?ct=010108000000', buffer)

    print(test.scrape())
