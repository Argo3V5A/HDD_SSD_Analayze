import json
import warnings
from itertools import chain

from src.etl.extract import (collect_product_pages,
                             get_product_amount_page,
                             generate_headers,
                             collect_url_from_page,
                             get_product_data,
                             get_page_html)
from src.imdict import imdict

if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    data = imdict({'URL': 'https://www.e-katalog.ru/list/61/',
                   'DOMAIN': 'https://www.e-katalog.ru'})

    headers = imdict({'browser': "chrome",
                      'os': "win",
                      'headers': True})

    pages_urls = collect_product_pages(data['URL'], get_product_amount_page(data['URL'], generate_headers(headers)))

    all_url_product = list(
        chain(*list(map(collect_url_from_page, pages_urls, [generate_headers(headers)]))))  # Распоковка всех списков

    full_url_path_to_product = list(map(lambda x: data['DOMAIN'] + x, all_url_product))

    with open('ssd_data.json', mode='a', encoding='UTF8') as f:
        for url in full_url_path_to_product:
            temp = get_product_data(get_page_html(url))
            json.dump(temp, f, indent=4, ensure_ascii=False)
            temp.clear()
        f.close()
