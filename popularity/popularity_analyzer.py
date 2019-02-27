# coding=utf-8
import platform
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from user_agent import generate_user_agent


class Query:
    def __init__(self, rank, name, num_unpopular=-1):
        self.rank = rank
        self.name = name
        self.num_unpopular = num_unpopular
        self.score = 0.0

    def set_score(self):
        if self.num_unpopular > 0:
            self.score = self.num_unpopular / self.rank


class PopularityAnalyzer:
    def __init__(self, popularity_json_path):
        self.popularity_json_path = popularity_json_path

    def analyze_popularity(self):
        load_topk_query()
        add_num_unpopular_products()
        add_query_score()
        save()

    def load_topk_query(self):
        if not popularity_json_exists():
            get_and_write_topk_query(k=100)

    def popularity_json_exists(self):
        popularity_json_file = Path(self.popularity_json_path)
        return popularity_json_file.is_file()

    def get_and_write_topk_query(k=100):


if __name__ == "__main__":
    analyzer = PopularityAnalyzer()
    analyzer.analyze_popularity()
