from bs4 import BeautifulSoup
from datetime import datetime
import re
import pandas as pd
import requests
# config, process, log
import configparser
from tendo import singleton
import logging
import urllib.request

class newscrawling:

    def __init__(self):
        self.url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=101&sid2=259'
        self.hader = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
        self.res = requests.get(self.url, headers=self.hader)
        self.soup = BeautifulSoup(self.res.content, 'lxml')
        self.temp = self.soup.find('div', attrs={'class':'content'})
        self.temp2 = self.temp.find_all('li')
            
    def main(self):
        logger.info('Main Start')
        try:
            temp2 = self.temp2
            hader = self.hader
            self.news_dict_list = []
            for i in temp2:
                main_news = {}
                newu = i.find('a')
                news = i.find('dd')
                main_news['news_today'] = datetime.today().strftime("%Y%m%d")
                
                main_news['news_url'] = newu['href']
                surl = main_news['news_url'].split('&')
                
                main_news['news_oid'] = re.sub(r'[^0-9]','',surl[4])
                main_news['news_press'] = news.text.replace('\n','|').split('|')[2]
                main_news['news_aid'] = re.sub(r'[^0-9]','',surl[5])
                
                body_url = main_news['news_url']
                body_res = requests.get(body_url, headers=hader)
                body_soup = BeautifulSoup(body_res.content, 'lxml')
                body_temp1 = body_soup.find('span', attrs={'class':'t11'})
                body_temp = body_soup.find('div', attrs={'class':'_article_body_contents article_body_contents'})
                
                main_news['news_header'] = body_soup.find('h3').text    
                main_news['news_summary'] = news.text.replace('\n','|').split('|')[1]
                main_news['article_date'] = body_temp1.text
                main_news['news_body'] = body_temp.text.replace('\n','').strip()
                
                self.news_dict_list.append(main_news)
            logger.info('Main End')
            return self.news_dict_list
        except Exception as ee:
            logger.error(f"Main Error : {ee}")       
    
    def csv_save(self):
        try:
            logger.info('CSV_save Start')
            npd = pd.DataFrame(self.news_dict_list)
            npd.to_csv('news_main.csv', encoding='utf-8-sig')
            logger.info('CSV_save End')
        except Exception as ee:
            logger.error(f"CSV_save Error : {ee}")
        
        return npd


if __name__ == '__main__':
    start = newscrawling()
    me = singleton.SingleInstance()
    config = configparser.ConfigParser()
    config.read('config.conf', encoding='UTF8')
    config_df = config['DEFAULT']
    
    Log_Format = '%(levelname)s %(asctime)s - %(message)s'
    ## filename , filemode : a 내용추가 // w 새로 쓰기, format : Log 작성 내용 , level : 로그 레벨
    logging.basicConfig(filename = "logfile.log", filemode = "a", format = Log_Format, level = logging.INFO)
    logger = logging.getLogger()
 
    start.main()
    start.csv_save()



