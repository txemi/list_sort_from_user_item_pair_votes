import logging
import os
import random

import typeguard

from item import ItemWrapper
from list_sort_from_user_item_pair_votes.csv_helper import _read_csv, write_csv_1


@typeguard.typechecked
def _guess_id_field(rows: list[dict]):
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    keys = []
    for key_in_row in first_row:
        row_values = [row[key_in_row] for row in rows]
        key_can_be_id = all([value is not None and value.isdigit() for value in row_values])
        if key_can_be_id and len(set(row_values)) == len(row_values):
            keys.append(key_in_row)
    if len(keys) == 1:
        return keys[0]
    for preferred in "id", "Const":
        for key in keys:
            if preferred in key:
                return key
    return keys[0]


@typeguard.typechecked
class Items:

    def __init__(self, filename: str, load_csv: bool = True):
        self.__filename = filename
        if load_csv and os.path.exists(filename):
            rows = list(_read_csv(filename))
            self.__wrapped_items = list(map(lambda x: ItemWrapper(x, _guess_id_field(rows)), rows))
        else:
            self.__wrapped_items = []

    def get_wrapped_items_randomized(self):
        random_wrapped_items = self.__wrapped_items[:]
        random.shuffle(random_wrapped_items)
        return random_wrapped_items

    def get_wrapped_items(self):
        return self.__wrapped_items

    def get_item_by_id(self, item_id: int):
        for wrapped_item in self.__wrapped_items:
            if wrapped_item.get_id() == item_id:
                return wrapped_item
        raise NotImplementedError()

    def format(self):
        items_formatted = map(lambda x: x.format_short(), self.__wrapped_items)
        return '\n'.join(items_formatted)

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
        def temp(row):
            assert isinstance(row, ItemWrapper)
            return row.get_data()

        write_csv_1(self.__filename, self.get_field_names(), [temp(row) for row in self.__wrapped_items])

    def get_items(self):
        return self.get_wrapped_items()
