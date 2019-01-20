# -*- coding: utf-8 -*-
import os

from selenium import webdriver

from popularity.popularity import get_html_by_selenium
from popularity.popularity import DRIVER
from popularity.popularity import URL
from popularity.popularity import get_num_productset
from popularity.popularity import get_possible_paging_index
from popularity.popularity import parse_html
from popularity.popularity import parse_produts


def main(flags):
    query = "봄원피스"
    max_paging_index = 2
    data_dir = "regression/data"

    params = {'query': query, 'pagingIndex': 1, 'pagingSize': 40}
    html = get_html_by_selenium(DRIVER, URL, params)
    num_productset = get_num_productset(html)
    possible_paging_index = get_possible_paging_index(num_productset)
    possible_paging_index = min(possible_paging_index, max_paging_index)
    print(f'검색어: {query}; 전체 상품 갯수: {num_productset}')

    data_filepath = os.path.join(data_dir, "rank_regression.onepiece.10.data.tsv")
    with open(data_filepath, 'w', encoding='utf-8') as f:
        for paging_index in range(possible_paging_index):
            paging_index += 1
            params = {'query': query, 'pagingIndex': paging_index, 'pagingSize': 80}
            # html = get_html(URL, params)
            html = get_html_by_selenium(DRIVER, URL, params)
            products = parse_html(html)
            parsed_produts = parse_produts(products)
            for parsed_product in parsed_produts:
                line = to_string(parsed_product)
                f.write(f"{line}\n")


def to_string(product):
    rank = str(product['rank'])
    reviews = str(product['reviews'])
    date = product['date']
    jjim = str(product['jjim'])

    date = ''.join(filter(str.isdigit, date))
    return '\t'.join([rank, reviews, date, jjim])


if __name__ == "__main__":
    flags = None

    DRIVER = webdriver.Chrome("resources/chromedriver_win32/chromedriver.exe")
    main(flags)
