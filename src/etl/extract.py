import time
from typing import Dict, List
import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
from lxml import html

def generate_headers(headers_setting: Dict) -> Dict:
    '''
    Генерирует html заголовки запросов. В данном случае фейковые.
    '''
    # TODO Расширить количество аргументов.

    return Headers(
        browser=headers_setting['browser'],
        os=headers_setting['os'],
        headers=headers_setting['headers']
    ).generate()


def get_page_html(url: str, verify: bool = False, **kwargs) -> BeautifulSoup:
    '''На основе url получает всю html страницы, без потверждения ssl(опционально)'''

    time.sleep(1)
    return BeautifulSoup(requests.get(url, verify=verify, **kwargs).content, 'html.parser')


def get_product_amount_page(url: str,headers: Dict) -> int:
    '''
    Возвращает общее количество страниц для конкретного типа продукта
    | ---
    | url = базовый url страницы конкретного продукта (data['url'])
    | headers = Шапка html запроса в формате словаря.
    | ---
    '''

    def page_count(tree):
        return tree.xpath('//div[@class="ib page-num"]//a[last()]/text()')

    return int(page_count(html.fromstring(requests.get(url, headers=headers).content))[0])


def collect_product_pages(url: str, pages_count: int) -> List[str]:
    """
    *Получает список url страниц с товарами.*
    | ---
    | url = базовый url страницы конкретного продукта (data['url'])
    | pages_count = Общее количество страниц для продукта.
    | ---
    """
    return list(map(lambda x: url + f"{x}/", range(1, pages_count + 1)))


def collect_url_from_page(page_url: str, headers: Dict, sleep: int = 1) -> List[str]:
    '''
    *Получает все url продуктов со страницы(получает список страницы), возвращает список url*
    | ---
    | page_url = url страницы со товармаи
    | headers = Шапка html запроса в формате словаря
    | sleep = Время задержки после запроса
    | ---
    '''

    def get_product_url(tree):
        return tree.xpath("//a[@class='model-short-title no-u no-u']/@href")

    time.sleep(sleep)
    return get_product_url(html.fromstring(requests.get(page_url, headers=headers).content))


def get_product_data(soup: BeautifulSoup) -> Dict[str, str]:
    '''Получает BeautifulSoup объект. Получает имя товара, и таблицу с характеристиками'''

    _ = dict()
    _.update({'Наименование товара': soup.find("div", class_="op1-tt").text})
    # _.update({'Cost': soup.find('div', class_='desc-short-prices').find('a', class_='ib').text})

    def get_loop_data(_: Dict) -> Dict[str,str]:

        for value in soup.find("table", class_="one-col").contents:

            try:
                _.update({value.find("span", class_="gloss").text: value.find("td", class_="val").text})

            except AttributeError:
                continue

        return _

    return get_loop_data(_)


def create_json(urls: List[str]) -> Dict[str, List[Dict[str, str]]]:
    global get_product_data, get_page_html

    def data_list(url):
        data = get_product_data(get_page_html(url))
        data.update({'url': url})
        return data

    return {'SSD': list(map(data_list, urls))}
