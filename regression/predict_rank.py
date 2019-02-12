# -*- coding: utf-8 -*-
import datetime
import os

from matplotlib import pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor


now = datetime.datetime.now()


class RankRegression:
    def __init__(self, flags):
        self.flags = flags
        # self.model = DecisionTreeRegressor()
        # self.model = RandomForestRegressor(n_estimators=2000)
        self.model = GradientBoostingRegressor(n_estimators=2000)

    @property
    def dataset_filepath(self):
        # data_dir = self.flags.data_dir
        data_dir = "regression/data"
        return os.path.join(data_dir, "rank_regression.onepiece.1.data.tsv")

    def train(self):
        inputs, targets = self._get_or_generate_datasets()
        self.model = self.model.fit(inputs, targets)

    def predict(self, data):
        return self.model.predict(data)

    def _get_or_generate_datasets(self):
        inputs, targets = txt_tab_iterator(self.dataset_filepath)
        return inputs, targets

    def print_score(self):
        inputs, targets = self._get_or_generate_datasets()
        score = self.model.score(inputs, targets)
        print(f"train-set score: {str(score)}")
        print(f"possible: {str(self.model.predict([[0, 1, 10, 1]]))}")
        print(f"possible: {str(self.model.predict([[1, 1, 10, 1]]))}")
        print(f"possible: {str(self.model.predict([[10, 1, 10, 1]]))}")
        print(f"possible: {str(self.model.predict([[10, 2, 10, 1]]))}")
        print(f"possible: {str(self.model.predict([[10, 1, 10, 3]]))}")

    def show_scatter(self):
        inputs, targets = self._get_or_generate_datasets()
        predictions = self.predict(inputs)
        plt.scatter(targets, predictions)
        plt.xlabel("Targets")
        plt.ylabel("Predictions")
        plt.title("Relations")
        plt.show()


def txt_line_iterator(path):
    for line in open(path, encoding='utf-8'):
        yield line.strip()


def txt_tab_iterator(path):
    inputs = []
    targets = []
    for line in txt_line_iterator(path):
        data = line.split('\t')
        data[2] = (now.year - int(data[2][:4])) * 12 + (now.month - int(data[2][4:])) + 1
        data = [int(v) for v in data]
        inputs.append(data[1:])
        targets.append(data[0])
    print(f"INPUTS: {inputs[:5]}")
    print(f"TARGETS: {targets[:5]}")
    return inputs, targets


def main():
    rank_regression = RankRegression(None)
    rank_regression.train()
    rank_regression.print_score()
    rank_regression.show_scatter()


if __name__ == "__main__":
    main()
