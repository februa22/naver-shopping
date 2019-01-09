# coding=utf-8
import argparse
import os
import sys
from urllib.parse import urlencode, quote_plus

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

URL = 'https://search.shopping.naver.com/search/all.nhn'
FLAGS = None
DRIVER = webdriver.Chrome('C:\\Users\\22feb\\Downloads\\chromedriver_win32\\chromedriver.exe')


def get_html(url, params=None):
    html = ""
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        html = resp.text
    return html


def get_html_by_selenium(driver, url, params):
    params_encoded = urlencode(params, quote_via=quote_plus)
    driver.get(f'{URL}?{params_encoded}')
    return driver.page_source


def parse_html(html):
    """ 
    판매처가 여러개인 상품: `{"class": "_model_list _itemSection"}`
    판매처가 하나인 상품: `{"class": "_itemSection"}`
    기획 상품: `{"class": "exception _itemSection"}`
    """
    soup = BeautifulSoup(html, 'html.parser')
    goods_list = soup.find("ul", {"class": "goods_list"}).find_all(
        "li", {"class": "_itemSection"})
    for goods in goods_list:
        if allowed_class(goods['class']):
            yield goods


def allowed_class(product_classes):
    if 'ad' in product_classes:
        return False
    if 'exception' in product_classes:
        return False
    return True


def parse_produts(products):
    for product in products:
        parsed_product = dict()

        parsed_product['rank'] = int(product['data-expose-rank'])
        info_soup = product.find("div", {"class": "info"})
        tit_soup = info_soup.find("a", {"class": "tit"})
        parsed_product['title'] = tit_soup.text.strip()
        etc_soup = info_soup.find("span", {"class": "etc"})
        date_soup = etc_soup.find("span", {"class": "date"})
        review_soup = etc_soup.find("a", {"class": "graph"})
        parsed_product['date'] = date_soup.text.strip() if date_soup else ''
        parsed_product['reviews'] = review_soup.find("em").text if review_soup else '0'
        parsed_product['reviews'] = int(parsed_product['reviews'].replace(',', ''))
        yield parsed_product


def generate_topk_queries(topk_filepath):
    for line in open(topk_filepath, encoding='utf-8'):
        line = line.strip()
        query = ''.join(filter(str.isalpha, line))
        yield query


def get_num_productset(html):
    soup = BeautifulSoup(html, 'html.parser')
    productset_soup = soup.find("a", {"class": "_productSet_total"})
    productset = productset_soup.text.strip()
    productset = ''.join(filter(str.isdigit, productset))
    return int(productset)


def get_possible_paging_index(num_productset, paging_size=80):
    return (num_productset // paging_size) + 1


def main():
    summary_path = None
    if FLAGS['query'] == 'all':
        if FLAGS['topk_filepath']:
            queries = generate_topk_queries(FLAGS['topk_filepath'])
            summary_path = make_summary_path(FLAGS['topk_filepath'],
                                             FLAGS['max_paging_index'],
                                             FLAGS['num_reviews'])
        else:
            raise AttributeError('검색어가 "all"인 경우 인기검색어목록 파일이 필요합니다.')
    else:
        queries = [FLAGS['query']]
    
    max_paging_index = (FLAGS['max_paging_index'] // 2) + 1

    summary = {}

    for i, query in enumerate(queries, 1):
        params = {'query': query, 'pagingIndex': 1, 'pagingSize': 40}
        # html = get_html(URL, params)
        html = get_html_by_selenium(DRIVER, URL, params)
        num_productset = get_num_productset(html)
        possible_paging_index = get_possible_paging_index(num_productset)
        possible_paging_index = min(possible_paging_index, max_paging_index)
        print(f'[{i}] 검색어: {query}; 전체 상품 갯수: {num_productset}')

        num_unpopular_products = 0
        for paging_index in range(possible_paging_index):
            paging_index += 1
            params = {'query': query, 'pagingIndex': paging_index, 'pagingSize': 80}
            # html = get_html(URL, params)
            html = get_html_by_selenium(DRIVER, URL, params)
            num_productset = get_num_productset(html)
            products = parse_html(html)
            parsed_produts = parse_produts(products)
            for product in parsed_produts:
                if product['reviews'] < FLAGS['num_reviews']:
                    # print(f'  {product}')
                    num_unpopular_products += 1
        print(f"리뷰 갯수가 {FLAGS['num_reviews']}개 미만인 상품은 총 {num_unpopular_products}개 입니다.")
        print('=' * 20)
        summary[query] = num_unpopular_products
    print(summary.items())
    write_summary(summary, summary_path)


def make_summary_path(path, max_paging_index, num_reviews):
    """
    Args:
    path -- `data/knits.top100.txt`
    max_paging_index -- `6`
    num_reviews -- `5`

    Returns:
    summary_path -- `summary/knits.top100.summary.paging6.review5.txt
    """
    _, tail = os.path.split(path)
    filename, file_extension = os.path.splitext(tail)
    summary_filename = f'{filename}.summary.paging{max_paging_index}.review{num_reviews}.{file_extension}'
    return os.path.join('summary', summary_filename)


def write_summary(summary, summary_path):
    if summary_path:
        head = ['검색순위', '검색어', '판매점수 낮은 상품 갯수']
        with open(summary_path, mode='w', encoding='utf-8') as f:
            f.write(f'{head[0]}, {head[1]}, {head[2]}\n')
            for i, (k, v) in enumerate(summary.items(), 1):
                f.write(f'{str(i)}, {k}, {str(v)}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=sys.argv[0] + " description")
    parser.add_argument('--query', type=str, default="all", required=False, help='검색어 (default: "all")')
    parser.add_argument('--topk_filepath', type=str, default="", required=False, help='검색어가 "all"인 경우에 사용하는 인기검색어목록 파일경로')
    parser.add_argument('--num_reviews', type=int, default=5, help='리뷰 갯수가 이 숫자보다 작은 상품만 조회합니다.')
    parser.add_argument('--max_paging_index', type=int, default=3, help='최대 페이지 갯수 (defalut: 3)')
    
    try:
        FLAGS = vars(parser.parse_args())
    except:
        parser.print_help()
        sys.exit(0)
    main()
