# -*- coding: utf-8 -*-
import os

from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression


class RankRegression:
    def __init__(self, flags):
        self.flags = flags
        self.model = LinearRegression()

    @property
    def dataset_filepath(self):
        # data_dir = self.flags.data_dir
        data_dir = "regression/data"
        return os.path.join(data_dir, "rank_regression.onepiece.10.data.tsv")

    def train(self):
        inputs, targets = self._get_or_generate_datasets()
        self.model = self.model.fit(inputs, targets)

    def predict(self, data):
        return self.model.predict(data)

    def _get_or_generate_datasets(self):
        inputs, targets = txt_tab_iterator(self.dataset_filepath)
        return inputs, targets

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
        data = [int(v) for v in data]
        inputs.append(data[1:])
        targets.append(data[0])
    return inputs, targets


def main():
    rank_regression = RankRegression(None)
    rank_regression.train()
    rank_regression.show_scatter()


if __name__ == "__main__":
    main()
