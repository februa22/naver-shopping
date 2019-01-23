# -*- coding: utf-8 -*-
import os

from selenium import webdriver

from popularity.popularity import get_html_by_selenium
from popularity.popularity import get_num_productset
from popularity.popularity import get_possible_paging_index
from popularity.popularity import generate_topk_queries
from popularity.popularity import parse_html
from popularity.popularity import parse_produts
from popularity.popularity import URL


def main(flags):
    queries = generate_topk_queries("data/onepiece.top20.txt")
    max_paging_index = 5
    data_dir = "regression/data"
    data_filepath = os.path.join(data_dir, "rank_regression.onepiece.top20.data.tsv")

    with open(data_filepath, 'w', encoding='utf-8') as f:
        for i, query in enumerate(queries, 1):
            params = {'query': query, 'pagingIndex': 1, 'pagingSize': 40}
            html = get_html_by_selenium(DRIVER, URL, params)
            num_productset = get_num_productset(html)
            possible_paging_index = get_possible_paging_index(num_productset)
            possible_paging_index = min(possible_paging_index, max_paging_index)
            print(f'검색어: {query}; 전체 상품 갯수: {num_productset}')

            for paging_index in range(possible_paging_index):
                paging_index += 1
                params = {'query': query, 'pagingIndex': paging_index, 'pagingSize': 80}
                html = get_html_by_selenium(DRIVER, URL, params)
                products = parse_html(html)
                parsed_produts = parse_produts(DRIVER, products)
                for parsed_product in parsed_produts:
                    line = to_string(parsed_product)
                    f.write(f"{line}\t{query}\n")


def to_string(product):
    rank = str(product['rank'])
    reviews = str(product['reviews'])
    date = product['date']
    jjim = str(product['jjim'])
    mall_grade = str(product['mall_grade'])

    date = ''.join(filter(str.isdigit, date))
    return '\t'.join([rank, reviews, date, jjim, mall_grade])


if __name__ == "__main__":
    flags = None

    DRIVER = webdriver.Chrome("resources/chromedriver_win32/chromedriver.exe")
    main(flags)
