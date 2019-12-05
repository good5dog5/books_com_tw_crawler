import requests
import time
import lxml.html
from pprint import pprint
from time import sleep
import random
import json 

def xpath0(element, xpath):
    result = element.xpath(xpath)
    # assert len(result) == 1, result
    return result[0]




def get_link(element):
    return xpath0(element, 'a').get('href')

def get_title(element):
    return extract_text(xpath0(element, 'div[2]/h4'))

def get_all_titles(books_list):
    return (get_title(ele) for ele in books_list)

def get_all_links(books_list):
    return (get_link(ele) for ele in books_list)

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


def extract_text(element, joiner=''):
    return joiner.join(element.itertext()).strip()


def with_retry(request_function):
    def function(url, max_retries=32, **kwargs):
        for r in range(max_retries):
            response = request_function(url, **kwargs)
            if response.content and response.content != b'404':
                return response
            sleep(2)
        raise EmptyResponse(url)
    function.__name__ = request_function.__name__
    return function

req_get = with_retry(requests.get)
req_post = with_retry(requests.post)

root      = 'https://www.books.com.tw/web/sys_tdrntb/books/'

UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
              "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
              "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
              )

ua = UAS[random.randrange(len(UAS))]
headers = {'user-agent': ua}

if __name__ == "__main__":


    root_html = req_get(root).content.decode('utf-8')

    root_etree         = lxml.html.fromstring(root_html)
    all_books_list     = root_etree.xpath('/html/body/div[4]/div/div[3]/div[1]/ul/li')
    all_books_url_list = list(get_all_links(all_books_list))

    all_result = dict()

    start = 87
    for i, book_url in enumerate(all_books_url_list[start:]):
        book_html = req_get(book_url, 
                            headers=headers
                            ).content.decode('utf-8')
        print(book_url)
        result = get_attribute_from_book_page(book_html)
        result['rank'] = i+start
        all_result[i+start] = result
        pprint(all_result)
        sleep(10)

        with open('top100_{start}.json'.format(start = str(start)), 'w', encoding='utf-8') as f:
            json.dump(all_result, f, ensure_ascii=False)
