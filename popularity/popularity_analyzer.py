#!/usr/bin/env python
# coding=utf-8
import datetime
import json
import locale
import platform
import sys
from urllib.parse import quote_plus
from urllib.parse import urlencode

from selenium import webdriver
from user_agent import generate_user_agent

SHOPPING_INSIGHT_URL = "https://datalab.naver.com/shoppingInsight/sCategory.naver"
SHOPPING_SEARCH_URL = 'https://search.shopping.naver.com/search/all.nhn'
MALL_GRADES_TO_ID = {"플래티넘": 6, "프리미엄": 5, "빅파워": 4, "파워": 3, "새싹": 2, "씨앗": 1}
MALL_GRADES_TO_STR = {6: "플래티넘", 5: "프리미엄", 4: "빅파워", 3: "파워", 2: "새싹", 1: "씨앗"}
MAX_PAGING_INDEX = 3
NUM_REVIEWS = 5
NUM_JJIM = 10
MAX_MALL_GRADE = 1
locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')


class Query:
    def __init__(self, rank, name):
        self.query_rank = int(rank) if not isinstance(rank, int) else rank
        self.query_name = name
        self.num_unpopular = {'씨앗': 0, '새싹': 0, '파워': 0, '빅파워': 0, '프리미엄': 0, '플래티넘': 0}
        self.unpopular_ranks = {'씨앗': [], '새싹': [], '파워': [], '빅파워': [], '프리미엄': [], '플래티넘': []}
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
        self.driver.quit()

    def _load_topk_query(self, k=100):
        print("Starting _load_topk_query...")
        self.driver.get(SHOPPING_INSIGHT_URL)

        # Set category to 패션의류 > 여성의류
        self.driver.find_element_by_xpath("//div[@class='set_period category']/div[2]/span").click()
        self.driver.find_element_by_xpath("//a[@data-cid='50000167']").click()
        
        # Set category to 패션의류 > 여성의류 > 재킷
        # 니트 --> 50000805
        # 코트 --> 50000813
        # 재킷 --> 50000815
        # 스커트 --> 50000808
        # self.driver.find_element_by_xpath("//div[@class='set_period category']/div[3]/span").click()
        # self.driver.find_element_by_xpath("//a[@data-cid='50000808']").click()

        # Set period to 주간
        self.driver.find_element_by_xpath("//div[@class='select w4']/span").click()
        self.driver.find_element_by_xpath("//div[@class='select w4']/ul/li[2]/a").click()

        # 조회하기 click
        self.driver.find_element_by_xpath("//div[@class='section_instie_area space_top']/div[@class='section insite_inquiry']/div[@class='step_form']/a").click()

        k = 5  # default: 5
        for i in range(k):
            if i != 0:
                self.driver.find_element_by_xpath("//a[@class='btn_page_next']").click()
                self.driver.implicitly_wait(3)

            rank_topk_list_element = self.driver.find_elements_by_xpath("//ul[@class='rank_top1000_list']/li")
            for j, element in enumerate(rank_topk_list_element):
                rank, name = element.find_element_by_tag_name("a").text.strip().split("\n")
                self.rank_topk.append(Query(rank, name))

    def _add_num_unpopular(self):
        print("Starting _add_num_unpopular...")
        for query_instance in self.rank_topk:
            try:
                self._count_num_unpopular(query_instance)
            except Exception as e:
                print(e)
                pass

    def _count_num_unpopular(self, query_instance):
        print(f"\t_count_num_unpopular({query_instance.query_name})")
        num_productset = get_num_productset(self.driver, query_instance.query_name)
        possible_paging_index = get_possible_paging_index(num_productset)
        possible_paging_index = min(possible_paging_index, MAX_PAGING_INDEX)

        for paging_index in range(possible_paging_index):
            self._count_num_unpopular_in_a_page(query_instance, paging_index + 1)

    def _count_num_unpopular_in_a_page(self, query_instance, paging_index):
        query = query_instance.query_name
        params = {'query': query, 'pagingIndex': paging_index, 'pagingSize': 80}
        params_encoded = urlencode(params, quote_via=quote_plus)
        url = f'{SHOPPING_SEARCH_URL}?{params_encoded}'
        self.driver.get(url)
        self.driver.implicitly_wait(3)
        current_window = self.driver.current_window_handle

        # 판매처가 한개
        try:
            goods_list_with_a_mall = self.driver.find_elements_by_xpath('//li[@class="_itemSection"]')
        except Exception as e:
            print('//li[@class="_itemSection"] not found.')
            print(e)
        else:
            goods_list_with_a_mall = filter_by_num_reviews_and_jjim(goods_list_with_a_mall)
            for li in goods_list_with_a_mall:
                try:
                    mall_grade = li.find_element_by_xpath('.//a[@class="btn_detail _btn_mall_detail"]').get_attribute('data-mall-grade').strip()
                except Exception as e:
                    print(e)
                    mall_grade = '씨앗'
                num_unpopular = query_instance.num_unpopular[mall_grade]
                query_instance.num_unpopular[mall_grade] = num_unpopular + 1
                # Get rank
                data_expose_rank = int(li.get_attribute('data-expose-rank'))
                # Get date
                date = li.find_element_by_xpath('.//span[@class="date"]').text.strip()[4:]
                query_instance.unpopular_ranks[mall_grade].append((data_expose_rank, date))
        
        # 판매처가 여러개
        try:
            goods_list_with_malls = self.driver.find_elements_by_xpath('//li[@class="_model_list _itemSection"]')
        except Exception as e:
            print('//li[@class="_model_list _itemSection"] not found.')
            print(e)
        else:
            goods_list_with_malls = filter_by_num_reviews_and_jjim(goods_list_with_malls)
            for li in goods_list_with_malls:
                data_expose_rank = int(li.get_attribute('data-expose-rank'))
                date = li.find_element_by_xpath('.//span[@class="date"]').text.strip()[4:]
                li.find_element_by_xpath('.//a[@class="btn_compare"]').click()

                try:
                    # self.driver.switch_to.window(self.driver.window_handles[1])
                    new_window = [window for window in self.driver.window_handles if window != current_window][0]
                    self.driver.switch_to.window(new_window)
                    self.driver.implicitly_wait(3)
                    jjim = 0
                    jjim_elements = self.driver.find_elements_by_xpath('//a[@class="sico_zzim_txt _jjim "]/em')
                    for element in jjim_elements:
                        jjim_text = element.text.strip()
                        jjim += locale.atoi(jjim_text)
                except Exception as e:
                    print(e)
                    jjim = 0
                if jjim <= NUM_JJIM:
                    mall_grade = 1
                    try:
                        mall_grade_elements = self.driver.find_elements_by_xpath('//a[@class="_btn_mall_detail _noadd"]')
                        for element in mall_grade_elements:
                            mall_grade_text = element.get_attribute("data-mall-grade")
                            mall_grade = max(mall_grade, MALL_GRADES_TO_ID[mall_grade_text])
                    except Exception as e:
                        print(e)
                        pass
                    mall_grade_text = MALL_GRADES_TO_STR[mall_grade]
                    num_unpopular = query_instance.num_unpopular[mall_grade_text]
                    query_instance.num_unpopular[mall_grade_text] = num_unpopular + 1
                    query_instance.unpopular_ranks[mall_grade_text].append((data_expose_rank, date))

                # Close new window
                # new_window = [window for window in self.driver.window_handles if window != current_window][0]
                # self.driver.switch_to.window(new_window)
                self.driver.close()
                self.driver.switch_to.window(current_window)

    def _add_query_score(self):
        print("Starting _add_query_score...")
        for query_instance in self.rank_topk:
            print(f"\t{query_instance.query_name}")
            rank = query_instance.query_rank
            num_unpopular = query_instance.num_unpopular['씨앗']
            score = num_unpopular / rank
            query_instance.score = score

    def save(self):
        now = datetime.datetime.now()
        print(f"Saving popularity to {self.popularity_json_path} ...")
        results = {
            "category": self.category,
            "date_time": now.strftime('%Y-%m-%d %H:%M:%S'),
            "target_pages": MAX_PAGING_INDEX * 2
        }
        results["rank_topk"] = [query.__dict__ for query in self.rank_topk]
        with open(self.popularity_json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(results, ensure_ascii=False, indent=4))


def get_chromedriver():
    system_name = platform.system()
    suffix = 'Windows.exe' if system_name == 'Windows' else system_name
    chromedriver_path = f'resources/chromedriver_{suffix}'
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


def filter_by_num_reviews_and_jjim(goods_list):
    goods_list_filtered = []
    if goods_list:
        for li in goods_list:
            # 리뷰수 필터
            try:
                review_text = li.find_element_by_xpath('.//a[@class="graph"]/em').text.strip()
                review = locale.atoi(review_text)
            except Exception as e:
                print(e)
                review = 0
            if review > NUM_REVIEWS:
                continue

            # 찜수 필터
            try:
                jjim_text = li.find_element_by_xpath('.//a[@class="jjim _jjim"]/em').text.strip()
                jjim = locale.atoi(jjim_text)
            except Exception as e:
                print(e)
                jjim = 0
            if jjim > NUM_JJIM:
                continue

            goods_list_filtered.append(li)
    return goods_list_filtered


if __name__ == "__main__":
    chromedriver = get_chromedriver()
    popularity_json_path = "popularity.json"
    analyzer = PopularityAnalyzer(chromedriver, popularity_json_path)
    analyzer.analyze_popularity()
    analyzer.save()
