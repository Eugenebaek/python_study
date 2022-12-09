# -*- coding: utf-8 -*-
import configparser
import loguru
import pymongo
import urllib
import re
from bs4 import BeautifulSoup



config = configparser.ConfigParser()
config.read('./config/config.conf', encoding='UTF8')
config_mob = config['MongoDB']
host = config_mob['hostname1']
port = config_mob['port']
username = urllib.parse.quote_plus(config_mob['username'])
password = urllib.parse.quote_plus(config_mob['password'])
conn = pymongo.MongoClient(f'mongodb://{username}:{password}@{host}:{port}/')
db = conn[config_mob['db_name']]
collection = db[config_mob['table_name']]
db2 = conn[config_mob['db_name2']]
collection2 = db2[config_mob['table_name2']]


def perser(data):
    list1 = []
    ids = data['_id']
    loguru.logger.info(f'start : {ids}')

    nsbody = data['body_raw']
    ns = BeautifulSoup(nsbody, 'lxml')
    n_1 = ns.find('div',attrs={'id':'container'})
    n_2 = ns.find('div',attrs={'id':'contents'})
    if n_1 == None:
        n_text = n_2
        ng = n_text.find('div',attrs={'id':'dic_area'})
        try : 
            n_rn = n_text.find('span',attrs={'class':'byline_s'}).text
        except:
            n_rn = 'None'
    else:
        n_text = n_1
        ng = n_text.find('div',attrs={'id':'newsEndContents'})
        try :
            n_rn = ng.find('p',attrs={'class':'byline'}).text
        except:
            n_rn = 'None'
    try :
        ng.find('strong').extract()
    except:
        pass
    try :
        ns = ng.find_all('span')
        for i in range(len(ns)):
            ng.find('span',attrs={'class':'end_photo_org'}).extract()
    except:
        pass
    try:
        ns = ng.find_all('div')
        for i in range(len(ns)):
            ng.find('div').extract()
    except:
        pass
    try:
        ns = ng.find_all('p')
        for i in range(len(ns)):
            ng.find('p').extract()
    except:
        pass
    
    for text in ng:
        new_text = text.text.replace('\xa0',' ').replace('* ','').replace('# ','').strip()
        ## http or https 제거
        new_text = re.sub(r'[a-z]+://[a-z0-9.-_]+','',new_text).replace('()','')
        ## 이메일 제거
        new_text = re.sub(r'[a-z]+@[a-z0-9.-_]+.com','',new_text).replace('()','')
        new_text = re.sub(r'[a-z]+@[a-z0-9.-_]+.co.kr','',new_text).replace('()','')
        ## 문자열 사이의 불필요한 unicode를 제거하십시오.
        new_text1 = new_text.replace(r'\xa0', r' ') \
            .replace(r'\u200b', r'').replace(r'\u3000', r'  ') \
            .replace(r'\ufeff', r'').replace(r'\ue3e2', r'..') \
            .replace(r'\x7f', r'').replace(r'\u2009', r' ') \
            .replace(r'\xad', r' ').replace(r'\uec36', r'...')
            
        ## unknown token    
        unk_t1 = unknwon_token_replace(new_text1)
        unk_text1 = remove_left_string(unk_t1)
        unk_e = remove_line_end_strings1(unk_text1)
        list1.append(unk_e)

    
    listx = ''.join(list1)
    data['content'] = data.pop('body_raw')
    data['content'] = listx
    data['summary'] = listx[:300]
    data['reporter_name'] = re.sub(r'[^가-힇]','',n_rn).replace('@','').strip()
    data['import_result'] = 'N'
    data['search_result'] = 'N'
    
    try : 
        print(data)
        collection2.insert_one(data)
        loguru.logger.info(f'{ids} pre insert')
    except Exception as error:
        loguru.logger.error(error)
        
    finally:
        loguru.logger.info('Sports_News End')
    
    return text
        
        
# unknown token을 문자로 치환
unknown_token_list = [
    ['比', '대비 '],
    ['韓', '한국 '],
    ['美', '미국 '],
    ['日', '일본 '],
    ['株', '주'],
    ['證', '증권'],
    ['銀', '은행'],
    ['…', ', '],
    ['`', '\''],
    ['“', '\"'],
    ['”', '\"'],
    ['‘', '\''],
    ['’', '\''],
    ['↑', '상승'],
    ['↓', '하락'],
    ['△', ','],
    ['▲', ','],
    ['▶', ','],
    ['▷', ','],
    ['→', ','],
    ['ㆍ', ','],
    ['百', '백화점'],
    ['重', '중공업'],
    ['外','외']
]        
pattern_unknown_token_replace = [re.compile(unknown_token[0]) for unknown_token in unknown_token_list]  
def unknwon_token_replace(text):
    for index, pattern_func in enumerate(pattern_unknown_token_replace):
        text = pattern_func.sub(unknown_token_list[index][1], text)
    return text

# 왼쪽부터 시작하여 특정string이 나오면 해당 위치까지 remove
# 왼쪽부터 시작하여 특정string이 나오면 해당 위치까지 remove
remove_left_string_list = [
    r'기자 =',
    r'기자］',
    r'기자] ',  # 위의 것과 다른 경우임
    r'기자]',
    r'기자\) ',
    r'기자',
    r'기자 ',
    r'재배포 금지',
    r'배포금지',
    # r' 기자 (.+)\@(.+).com',
    # r' 기자 (.+)\@(.+).co.kr',
    # r'(.+)\@(.+).com',
    # r'(.+)\@(.+).co.kr',
    # r'http://(.+)',
    # r'https://(.+)',
    r'/사진(.+) ',
    r'\[사진(.+)\]',
    r'\[사진\] (.+)',
    r'\[사진\](.+)',
    r'\[사진 =(.+)\]',
    r'\(사진제공=(.+)\)',
    r'\(사진=(.+)\)',
    r'사진\|(.+)',
    r'사진 \|(.+)',
    r'사진=(.+)',
    r'사진 = (.+)'
]
pattern_remove_left_string_list = [re.compile(remove_left_string) for remove_left_string in remove_left_string_list]
def remove_left_string(text):
    for index, pattern_func in enumerate(pattern_remove_left_string_list):
        matchObj = pattern_func.search(text)
        if matchObj == None:
            continue
        text = text[matchObj.end():]
    return text


# 특정 string이 문장의 index = 0부터 같을 경우 해당 위치까지 remove
remove_line_end_strings = [
    r'-\w+증권',
    r'-\w+證',
    r'-SK',
    r'-IBK',
    r'\/사진'
]
pattern_remove_line_end_strings = [re.compile(remove_line_start) for remove_line_start in remove_line_end_strings]

def remove_line_end_strings1(text):
    for index, pattern_func in enumerate(pattern_remove_line_end_strings):
        matchObj = pattern_func.search(text)
        if matchObj == None:
            continue
        if matchObj.end() != len(text):
            continue
        text = text[:matchObj.start()]
    return text


find1 = collection.find_one({'_id':'4450000087277'})
perser(find1)
# for i in find1:
    # perser(i)
    
