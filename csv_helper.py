import csv
import random
from typing import Iterable

import chardet
import typeguard


@typeguard.typechecked
def guess_file_encoding(filename: str):
    # testing autodetection; before: encoding='utf-8'
    with open(filename, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(10000))

    encoding = result["encoding"]

    return encoding


@typeguard.typechecked
def _read_csv(filename: str):
    with open(filename, mode='r', encoding=guess_file_encoding(filename)) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            yield row


@typeguard.typechecked
def read_csv_random(filename: str):
    csv_items = list(_read_csv(filename))
    if csv_items is None:
        raise Exception()
    random.shuffle(csv_items)
    for randomized_item in csv_items:
        yield randomized_item


@typeguard.typechecked
def write_csv_1(filename: str, column_names: Iterable[str], items: list[dict]):
    with open(filename, mode='w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        for row in items:
            assert isinstance(row, dict)
            try:
                writer.writerow(row)
            except:
                raise