# coding=utf-8
import argparse
import sys

from bs4 import BeautifulSoup
from selenium import webdriver

from popularity import get_html_by_selenium

URL = "https://datalab.naver.com/shoppingInsight/sCategory.naver"
FLAGS = None
DRIVER = None


def main():
    num_query = FLAGS.num_query
    topk_filepath = FLAGS.topk_filepath

    DRIVER.implicitly_wait(3)
    DRIVER.get(URL)

    # Set category to 패션의류 > 여성의류
    DRIVER.find_element_by_xpath("//div[@class='set_period category']/div[2]/span").click()
    DRIVER.find_element_by_xpath("//a[@data-cid='50000167']").click()

    # Set period to 주간
    DRIVER.find_element_by_xpath("//div[@class='select w4']/span").click()
    DRIVER.find_element_by_xpath("//div[@class='select w4']/ul/li[2]/a").click()

    # Click 조회하기
    DRIVER.find_element_by_xpath("//div[@class='section_instie_area space_top']/div[@class='section insite_inquiry']/div[@class='step_form']/a").click()

    rank_top1000_list_element = DRIVER.find_elements_by_xpath("//ul[@class='rank_top1000_list']/li")
    rank_top1000_data = {"category": "여성의류"}
    rank_top1000_list = []
    for element in rank_top1000_list_element:
        query = element.find_element_by_tag_name("a").text.strip().split("\n")[1]
        rank_top1000_list.append(query)
    rank_top1000_data["rank_top1000_list"] = rank_top1000_list

    print(rank_top1000_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=sys.argv[0] + " description")
    parser.add_argument("--num_query", type=int, default=10, help="검색어 갯수 (default: 10)")
    parser.add_argument("--topk_filepath", type=str, default="", help="인기검색어목록 파일경로")
    parser.add_argument("--chromedrive_path", type=str, default="", help="Chrome Drive Path for Selenium")
    
    try:
        FLAGS = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    DRIVER = webdriver.Chrome(FLAGS.chromedrive_path)
    main()