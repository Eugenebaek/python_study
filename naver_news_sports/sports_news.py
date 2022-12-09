# -*- coding: utf-8 -*-
from tendo import singleton
import loguru
from time import sleep
from datetime import datetime
import datetime as dt
import requests
import re
from bs4 import BeautifulSoup
import zmq
from db_mongo.mongo import MongoDB

class Sports:
    def __init__(self):
        self.db_connetion = MongoDB()
        self.conn = self.db_connetion.mongodb_primary()
        self.LOGGER = loguru.logger.bind(name='service')
        self.harder = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        self.socket = self.zmq_connct()


    def zmq_connct(self):
        context = zmq.Context()
        perser = context.socket(zmq.PUSH)
        perser.connect("tcp://127.0.0.1:5008")
        return perser


    def category_list(self):
        category = {'kbaseball':'야구','wbaseball':'해외야구','kfootball':'축구','wfootball':'해외축구',
            'basketball':'농구','volleyball':'배구','golf':'골프','general':'일반'}
        return category


    def url_list(self):
        category = self.category_list()
        c_key = [i for i in category.keys()]
        for i in range(len(c_key)):
            categ = c_key[i]
            url = f'https://sports.news.naver.com/{categ}/news/list?isphoto=N&page=1'
            res = requests.get(url, headers=self.harder).json()['list']
            self.insert_mongo(res, categ)
            sleep(0.5)
        return i

    def main_crawler(self, news, categ):
        spt_list = {}
        oid = news['oid']
        aid = news['aid']
        spt_list['oid'] = oid 
        spt_list['aid'] = aid
        spt_list['sid'] = categ
        spt_list['sid2'] = '999'
        spt_list['_id'] = news['oid'] + news['aid']
        spt_list['news_date'] = news['datetime'].split(' ')[0].replace('.','')
        spt_list['category'] = self.category_list()[categ]
        spt_list['subcategory'] = '최신뉴스' 
        spt_list['press'] = news['officeName'] 
        spt_list['headline'] = news['title'] 
        spt_list['summary'] = news['subContent']
        spt_list['img_url'] = news['thumbnail']
        spt_list['content_url'] = f'https://sports.news.naver.com/news?oid={oid}&aid={aid}'
        spt_list['insertTime'] = str(datetime.now())
        sleep(2)
        rex = requests.get(spt_list['content_url'],headers=self.harder)
        body_soup = BeautifulSoup(rex.content, 'lxml')
        spt_list['body_raw'] = f'{body_soup}'
        newstime = body_soup.find('div',attrs={'class':'info'})
        try :
            intime = newstime.select('span')[0].text.strip().replace('오전','AM').replace('오후','PM')
        except :
            intime = body_soup.find('span',attrs={'class':'media_end_head_info_datestamp_time _ARTICLE_DATE_TIME'}).text.strip().replace('오전','AM').replace('오후','PM')
        art_time = re.sub(r'[가-힇]','',intime).strip()
        spt_list['article_date'] = dt.datetime.strptime(art_time, '%Y.%m.%d. %p %I:%M').strftime('%Y.%m.%d %H:%M')

        try : 
            entime = newstime.select('span')[1].text.strip().replace('오전','AM').replace('오후','PM')
            end_time = re.sub(r'[가-힇]','',entime).strip()
            spt_list['article_editdate'] = dt.datetime.strptime(end_time, '%Y.%m.%d. %p %I:%M').strftime('%Y.%m.%d %H:%M')
        except : 
            spt_list['article_editdate'] = None
        return spt_list


    def mongo_data(self,sports_list):
        mongo_data = {'_id' : sports_list['_id'],
                            'sid' : sports_list['sid'],
                            'sid2' : sports_list['sid2'],
                            'oid' : sports_list['oid'],
                            'aid' : sports_list['aid'],
                            'news_date' : sports_list['news_date'],
                            'category' : sports_list['category'],
                            'subcategory' : sports_list['subcategory'],
                            'press' : sports_list['press'],
                            'headline' : sports_list['headline'],
                            'summary' : sports_list['summary'],
                            'body_raw' : sports_list['body_raw'],
                            'article_date' : sports_list['article_date'],
                            'article_editdate' : sports_list['article_editdate'],
                            'content_url' : sports_list['content_url'],
                            'img_url' : sports_list['img_url'],
                            'insertTime' : sports_list['insertTime'],
                            }
        return mongo_data

    def insert_mongo(self,res,categ):
        count = 0
        for news in res:
            spt_list = self.main_crawler(news,categ)
            mongo_data = self.mongo_data(spt_list)
            ids1 = spt_list['_id']
            ## 중복처리
            try:
                self.db_connetion.mongodb_connaction(mongo_data, self.conn)
                self.socket.send_pyobj(mongo_data)
                self.LOGGER.info(f'sports_news Mongo Insert : {ids1}')
                sleep(1)
            except Exception as ee:
                    self.LOGGER.error(ee)
                    count += 1
                    print('count : ',count)
                    if count == 3:
                        return news
        return news

def Main():
    main = Sports()
    try :
        main.url_list()
    except Exception as ee:
        LOGGER.error(ee)

if __name__ == '__main__':
    
    me = singleton.SingleInstance()
    times = datetime.today().strftime("%Y%m%d")
    log_format = '[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{process: >5}] [{level.name:>5}] <level>{message}</level>'
    
    loguru.logger.add(
        sink=f'./logs/sports_news_{times}.log',
        format=log_format,
        enqueue=True,
        level='INFO'.upper(),
        rotation='10 MB',
    )
    LOGGER = loguru.logger.bind(name='service')
    LOGGER.info("Sports News started...")
    
    ## Main Start
    Main()