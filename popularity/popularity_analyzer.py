#!/usr/bin/env python
# coding=utf-8
import json
import platform
import sys
from urllib.parse import quote_plus
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver
from user_agent import generate_user_agent

SHOPPING_INSIGHT_URL = "https://datalab.naver.com/shoppingInsight/sCategory.naver"
SHOPPING_SEARCH_URL = 'https://search.shopping.naver.com/search/all.nhn'
MALL_GRADES = {"플래티넘": 6, "프리미엄": 5, "빅파워": 4, "파워": 3, "새싹": 2, "씨앗": 1}


class Query:
    def __init__(self, rank, name):
        self.query_rank = rank
        self.query_name = name
        self.num_unpopular = 0
        self.score = 0.0

    def set_score(self):
        if self.num_unpopular > 0:
            self.score = self.num_unpopular / self.query_rank


class PopularityAnalyzer:
    """
    {
        "category": "",
        "score": 0.0,
        "rank_topk": [
            {
                "query_rank": 0,
                "query_name": "",
                "num_unpopular": 0,
                "score": 0.0
            }
        ]
    }
    """
    def __init__(self, driver, popularity_json_path):
        self.driver = driver
        self.popularity_json_path = popularity_json_path

        self.category = "여성의류"
        self.score = 0.0
        self.rank_topk = []

    def analyze_popularity(self):
        self._load_topk_query()
        self._add_num_unpopular()
        self._add_query_score()

    def _load_topk_query(self, k=100):
        print("Starting _load_topk_query...")
        self.driver.get(SHOPPING_INSIGHT_URL)

        # Set category to 패션의류 > 여성의류
        self.driver.find_element_by_xpath("//div[@class='set_period category']/div[2]/span").click()
        self.driver.find_element_by_xpath("//a[@data-cid='50000167']").click()

        # Set period to 주간
        self.driver.find_element_by_xpath("//div[@class='select w4']/span").click()
        self.driver.find_element_by_xpath("//div[@class='select w4']/ul/li[2]/a").click()

        # 조회하기 click
        self.driver.find_element_by_xpath("//div[@class='section_instie_area space_top']/div[@class='section insite_inquiry']/div[@class='step_form']/a").click()

        k = 1  # default: 5
        for i in range(k):
            if i != 0:
                self.driver.find_element_by_xpath("//a[@class='btn_page_next']").click()
                self.driver.implicitly_wait(3)

            rank_topk_list_element = self.driver.find_elements_by_xpath("//ul[@class='rank_top1000_list']/li")
            for element in rank_topk_list_element:
                rank, name = element.find_element_by_tag_name("a").text.strip().split("\n")
                self.rank_topk.append(Query(rank, name))

    def _add_num_unpopular(self, max_paging_index=1):
        print("Starting _add_num_unpopular...")
        num_reviews = 5
        num_jjim = 10
        max_mall_grade = 1
        for query_instance in self.rank_topk:
            query = query_instance.query_name
            print(f"\t{query}")
            num_productset = get_num_productset(self.driver, query)
            possible_paging_index = get_possible_paging_index(num_productset)
            possible_paging_index = min(possible_paging_index, max_paging_index)

            num_unpopular = 0
            for paging_index in range(possible_paging_index):
                paging_index += 1
                params = {'query': query, 'pagingIndex': paging_index, 'pagingSize': 80}
                html = get_html_by_selenium(self.driver, SHOPPING_SEARCH_URL, params)
                products = parse_html(html)
                parsed_produts = parse_produts(self.driver, products)
                for product in parsed_produts:
                    if product['reviews'] < num_reviews and product['jjim'] < num_jjim and product['mall_grade'] < (max_mall_grade + 1):
                        # print(f'  {product}')
                        num_unpopular += 1
            
            query_instance.num_unpopular = num_unpopular

    def _add_query_score(self):
        print("Starting _add_query_score...")
        for query_instance in self.rank_topk:
            print(f"\t{query_instance.query_name}")
            rank = query_instance.query_rank
            num_unpopular = query_instance.num_unpopular
            score = num_unpopular / rank
            query_instance.score = score

    def save(self):
        print(f"Saving popularity to {self.popularity_json_path} ...")
        results = {"category": self.category, "score": 0.0}
        results["rank_topk"] = [query.__dict__ for query in self.rank_topk]
        with open(self.popularity_json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(results, ensure_ascii=False, indent=4))


def get_chromedriver():
    chromedriver_path = f'resources/chromedriver_{platform.system()}'
    # chromedriver_path = 'resources/chromedriver_win32/chromedriver.exe'
    print(f'chromedriver_path={chromedriver_path}')

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_argument('lang=ko_KR')
    options.add_argument('no-sandbox')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument(f'user-agent={generate_user_agent()}')

    chromedriver = webdriver.Chrome(chromedriver_path, options=options)
    chromedriver.implicitly_wait(3)
    return chromedriver


def get_num_productset(driver, query):
    params = {'query': query, 'pagingIndex': 1, 'pagingSize': 40}
    params_encoded = urlencode(params, quote_via=quote_plus)
    url = f'{SHOPPING_SEARCH_URL}?{params_encoded}'
    driver.get(url)

    productset = driver.find_element_by_xpath("//a[@class='_productSet_total']").text.strip()
    productset = ''.join(filter(str.isdigit, productset))
    return int(productset)


def get_possible_paging_index(num_productset, paging_size=80):
    return (num_productset // paging_size) + 1


def get_html_by_selenium(driver, url, params=None):
    if params:
        params_encoded = urlencode(params, quote_via=quote_plus)
        driver.get(f'{url}?{params_encoded}')
    else:
        driver.get(url)
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


def parse_produts(driver, products):
    for product in products:
        parsed_product = dict()

        parsed_product['rank'] = int(product['data-expose-rank'])
        info_soup = product.find("div", {"class": "info"})
        tit_soup = info_soup.find("a", {"class": "tit"})
        parsed_product['title'] = tit_soup.text.strip()
        etc_soup = info_soup.find("span", {"class": "etc"})
        date_soup = etc_soup.find("span", {"class": "date"})
        parsed_product['date'] = date_soup.text.strip() if date_soup else ''
        review_soup = etc_soup.find("a", {"class": "graph"})
        parsed_product['reviews'] = review_soup.find("em").text if review_soup else '0'
        parsed_product['reviews'] = int(parsed_product['reviews'].replace(',', ''))
        jjim_soup = info_soup.find("a", {"class": "jjim"})
        parsed_product['jjim'] = jjim_soup.find("em").text if jjim_soup else '0'
        parsed_product['jjim'] = parsed_product['jjim'] if parsed_product['jjim'] else '0'
        try:
            parsed_product['jjim'] = int(parsed_product['jjim'].replace(',', ''))
        except ValueError:
            print(parsed_product['jjim'])
            raise
        parsed_product['mall_grade'] = parse_mall_grade(driver, product)
        yield parsed_product


def parse_mall_grade(driver, product):
    info_soup = product.find("div", {"class": "info"})
    info_mall_soup = product.find("div", {"class": "info_mall"})
    mall_txt_soup = info_mall_soup.find("p", {"class": "mall_txt"})

    mall_list_url = btn_compare_exists(info_soup)
    if mall_list_url:
        html = get_html_by_selenium(driver, mall_list_url)
        soup = BeautifulSoup(html, "html.parser")
        price_diff_soup = soup.find("div", {"id": "section_price_list"})
        mall_detail_soups = price_diff_soup.find_all("a", {"class": "_btn_mall_detail"})
        mall_grades = [1]
        if mall_detail_soups:
            for mall_detail_soup in mall_detail_soups:
                data_mall_grade = mall_detail_soup["data-mall-grade"]
                if data_mall_grade:
                    mall_grades.append(mall_grade_to_number(data_mall_grade))
        mall_grade = max(mall_grades)
    else:
        data_mall_grade = mall_txt_soup.find("a", {"class": "_btn_mall_detail"})["data-mall-grade"]
        if data_mall_grade:
           mall_grade = mall_grade_to_number(data_mall_grade)
        else:
            mall_grade = 1
    return mall_grade


def btn_compare_exists(info_soup):
    btn_compare_soup = info_soup.find("a", {"class": "btn_compare"})
    if btn_compare_soup:
        return btn_compare_soup["href"]
    else:
        return None


def mall_grade_to_number(data_mall_grade):
    data_mall_grade = data_mall_grade.strip()
    return MALL_GRADES.get(data_mall_grade, 1)


if __name__ == "__main__":
    chromedriver = get_chromedriver()
    popularity_json_path = "popularity.json"
    analyzer = PopularityAnalyzer(chromedriver, popularity_json_path)
    analyzer.analyze_popularity()
    analyzer.save()
