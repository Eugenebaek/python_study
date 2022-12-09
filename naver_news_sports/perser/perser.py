# -*- coding: utf-8 -*-
from tendo import singleton
import loguru
from datetime import datetime
import re
from bs4 import BeautifulSoup
import zmq

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from db_mongo.mongo import MongoDB


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
            ng.find('span').extract()
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
        # print(data)
        db_connetion.mongodb_connaction_pre(data, db)
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


if __name__ == '__main__':
    
    me = singleton.SingleInstance()
    times = datetime.today().strftime("%Y%m%d")
    
    log_format = '[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{process: >5}] [{level.name:>5}] <level>{message}</level>'
    
    loguru.logger.add(
        sink=f'./logs/sports_perser_{times}.log',
        format=log_format,
        enqueue=True,
        level='INFO'.upper(),
        rotation='10 MB',
    )
    LOGGER = loguru.logger.bind(name='service')
    LOGGER.info("sports perser started")
    
    db_connetion = MongoDB()
    db = db_connetion.mongodb_primary()
    
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:5008")
    while True:
        data = receiver.recv_pyobj()
        perser(data)
    