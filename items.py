import csv
import logging
import os
import random

import chardet
import typeguard

from item import ItemWrapper


@typeguard.typechecked
def guess_file_encoding(filename: str):
    with open(filename, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(10000))

    encoding = result["encoding"]

    return encoding


@typeguard.typechecked
def read_csv(filename: str):
    # testing autodetection; before: encoding='utf-8'
    with open(filename, mode='r', encoding=guess_file_encoding(filename)) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            yield row


@typeguard.typechecked
def read_csv_random(filename: str):
    row_list = list(read_csv(filename))
    if row_list is None:
        raise Exception()
    random.shuffle(row_list)
    for row in row_list:
        yield row


@typeguard.typechecked
class Items:
    def __init__(self, filename, load_csv=True):
        self.__filename = filename
        if load_csv and os.path.exists(filename):
            self.__wrapped_items = list(map(lambda x: ItemWrapper(x), list(read_csv(filename))))
        else:
            self.__wrapped_items = []

    def get_wrapped_items_randomized(self):
        random_wrapped_items = self.__wrapped_items[:]
        random.shuffle(random_wrapped_items)
        return random_wrapped_items

    def get_wrapped_items(self):
        return self.__wrapped_items

    def get_item_by_id(self, item_id: int):
        for a in self.__wrapped_items:
            if a.get_id() == item_id:
                return a
        raise NotImplementedError()

    def format(self):
        aaa = map(lambda x: x.format_short(), self.__wrapped_items)
        return '\n'.join(aaa)

    def print(self):
        logging.debug("{} begin {} elements".format(self.__class__.__name__, len(self.__wrapped_items)))
        logging.debug(self.format())
        logging.debug("{} end {} elements".format(self.__class__.__name__, len(self.__wrapped_items)))

    def __repr__(self):
        return "size={} {}".format(len(self.__wrapped_items), repr(self.__wrapped_items))

    def __len__(self):
        return len(self.__wrapped_items)

    def get_field_names(self):
        first = self.__wrapped_items[0]
        assert isinstance(first, ItemWrapper)
        data = first.get_data()
        return data.keys()

    def write_csv(self):
        with open(self.__filename, mode='w', encoding='utf-8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.get_field_names())
            writer.writeheader()
            for row in self.__wrapped_items:
                assert isinstance(row, ItemWrapper)
                writer.writerow(row.get_data())

    def get_items(self):
        return self.get_wrapped_items()
