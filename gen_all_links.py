#!/usr/bin/env python3
# Jordan huang<good5dog5@gmail.com>

import os
import sys
import requests
import lxml.html
from random import randint
from time import sleep
from fake_useragent import UserAgent

from itertools import cycle
from pprint import pprint
import json


def get_random_user_agent():
    user_agent = UserAgent()
    return user_agent.random


def xpath0(element, xpath):
    result = element.xpath(xpath)
    print(len(result))
    # assert len(result) == 1, result
    return result[0]

# def renew_tor_ip():
#     with Controller.from_port(port = 9051) as controller:
#         controller.authenticate(password="MyStr0n9P#D")
#         controller.signal(Signal.NEWNYM)


def with_retry(request_function):
    def function(url, max_retries=32, **kwargs):
        for r in range(max_retries):
            response = request_function(url, **kwargs)
            if response.content and response.content != b'404':
                # print('response:', response.content)
                return response
            sleep(2)
        raise EmptyResponse(url)
    function.__name__ = request_function.__name__
    return function

req_get = with_retry(requests.get)
req_post = with_retry(requests.post)


def extract_text(element, joiner=''):
    return joiner.join(element.itertext()).strip()

def get_attribute_from_book_page(html):

    document = lxml.html.fromstring(html)
    attr_div = xpath0(document, "//div[@class='type02_p003 clearfix']")
    cate_div = xpath0(document, "//div[@class='mod_b type02_m058 clearfix']")
    pric_div = xpath0(document, "//div[@class='prod_cont_a']")


    def xpath_text(xpath, joiner=''):
        return extract_text(xpath0(document, xpath), joiner=joiner)

    def xpath_int(xpath):
        return extract_int(xpath0(document, xpath))
    
    return {
        'title' : xpath_text('/html/body/div[4]/div/div[1]/div[2]/div[1]'),
        'author': extract_text(xpath0(attr_div, "ul/li[1]/a[1]")),
        'categories': extract_text(xpath0(cate_div, 'div/ul[2]')),
        'orig_price': extract_text(xpath0(pric_div, 'ul/li[1]')),
        'spec_price': extract_text(xpath0(pric_div, 'ul/li[2]'))
    }

def extract_int(element, allow_empty=False):
    text_list = element.xpath('.//text()')
    assert len(text_list) == 1, text_list
    if allow_empty and not text_list[0].strip():
        return None
    return int(text_list[0])

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = lxml.html.fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def extract_multirow_text(element):
    return re.sub(
        r'\n{4,}',
        '\n' * 3,
        '\n'.join(
            s.strip() for s in element.itertext()
        )
    )

def get_link(element):
    return element.xpath('a')[0].get('href')

def get_all_links(books_list):
    return (get_link(ele) for ele in books_list)

root      = 'https://www.books.com.tw/web/sys_tdrntb/books/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

if __name__ == '__main__':


    root_html = req_get(root).content.decode('utf-8')

    root_etree         = lxml.html.fromstring(root_html)
    all_books_list     = root_etree.xpath('/html/body/div[4]/div/div[3]/div[1]/ul/li')
    all_books_url_list = list(get_all_links(all_books_list))
    # print(all_books_url_list)

    all_result = dict()

    for i, book_url in enumerate(all_books_url_list):
        book_html = req_get(book_url, 
                            headers=headers,
                            verify=False
                            ).content.decode('utf-8')
        print(book_url)
        result = get_attribute_from_book_page(book_html)
        result['rank'] = i
        all_result[i] = result
        pprint(all_result)

        with open('top100.json', 'w', encoding='utf-8') as f:
            json.dump(all_result, f, ensure_ascii=False)
        


