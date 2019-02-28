#!/usr/bin/env python
# coding=utf-8
import platform
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from user_agent import generate_user_agent

SHOPPING_INSIGHT_URL = "https://datalab.naver.com/shoppingInsight/sCategory.naver"
SHOPPING_SEARCH_URL = 'https://search.shopping.naver.com/search/all.nhn'


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
        self.driver.get(SHOPPING_INSIGHT_URL)

        # Set category to 패션의류 > 여성의류
        self.driver.find_element_by_xpath("//div[@class='set_period category']/div[2]/span").click()
        self.driver.find_element_by_xpath("//a[@data-cid='50000167']").click()

        # Set period to 주간
        self.driver.find_element_by_xpath("//div[@class='select w4']/span").click()
        self.driver.find_element_by_xpath("//div[@class='select w4']/ul/li[2]/a").click()

        # 조회하기 click
        self.driver.find_element_by_xpath("//div[@class='section_instie_area space_top']/div[@class='section insite_inquiry']/div[@class='step_form']/a").click()

        k = 5
        for i in range(k):
            if i != 0:
                self.driver.find_element_by_xpath("//a[@class='btn_page_next']").click()
                self.driver.implicitly_wait(3)

            rank_topk_list_element = self.driver.find_elements_by_xpath("//ul[@class='rank_top1000_list']/li")
            for element in rank_topk_list_element:
                rank, name = element.find_element_by_tag_name("a").text.strip().split("\n")
                self.rank_topk.append(Query(rank, name))

    def _add_num_unpopular(self):
        pass

    def _add_query_score(self):
        pass

    def save(self):
        results = {"category": self.category, "score": 0.0}
        results["rank_topk"] = [query.__dict__ for query in self.rank_topk]
        print(results)


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


if __name__ == "__main__":
    chromedriver = get_chromedriver()
    popularity_json_path = ""
    analyzer = PopularityAnalyzer(chromedriver, popularity_json_path)
    analyzer.analyze_popularity()
    analyzer.save()

