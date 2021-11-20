import logging
import time
from typing import Optional

import typeguard

import common_utils
from item import ItemWrapper


@typeguard.typechecked
class ItemPairVoteKey:
    def __init__(self, item1: ItemWrapper, item2: ItemWrapper):
        self.__item1 = item1
        self.__item2 = item2

    def build_key(self):
        return tuple(sorted((self.__item1.get_id(), self.__item2.get_id())))

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ItemPairVoteKey):
            key1 = self.build_key()
            key2 = other.build_key()
            cmp_result = key1 == key2
            return cmp_result
        return False

    def __hash__(self):
        return hash(self.build_key())

    def __repr__(self):
        type_ = type(self)
        module = type_.__module__
        qualname = type_.__qualname__
        return f"<{module}.{qualname} {self.build_key()} object at {hex(id(self))}>"


@typeguard.typechecked
class ItemPairVote:
    def __init__(self, item1: ItemWrapper, item2: ItemWrapper, choice: Optional[ItemWrapper], timestamp: float = None):
        self.__item1 = item1
        self.__item2 = item2
        self.__choice = choice
        if timestamp is None:
            self.__timestamp = time.time()
        else:
            self.__timestamp = timestamp
        self.check_integrity()

    def get_key(self):
        return self.get_key_static(self.__item1, self.__item2)

    @staticmethod
    def get_key_static(x: ItemWrapper, y: ItemWrapper) -> ItemPairVoteKey:
        return ItemPairVoteKey(x, y)

    def get_choice(self) -> Optional[ItemWrapper]:
        return self.__choice

    def format(self):
        if self.__choice is None:
            return "{} ? {}".format(self.__item1.format_short(), self.__item2.format_short())
        elif self.__choice == self.__item1:
            return "{} > {}".format(self.__item1.format_short(), self.__item2.format_short())
        elif self.__choice == self.__item2:
            return "{} > {}".format(self.__item2.format_short(), self.__item1.format_short())

        raise NotImplementedError()

    class CsvFieldNames:
        item1_id = "bigger_id"
        item1_desc = "bigger_desc"
        choice = "vote"
        item2_id = "smaller_id"
        item2_desc = "smaller_desc"
        timestamp = "timestamp"
        csv_headers = (item1_id, item1_desc, choice, item2_id, item2_desc, timestamp)

    def build_dict_for_csv(self):
        item1_main_fields = self.__item1.get_main_fields()
        item2_main_fields = self.__item2.get_main_fields()
        if self.__choice is None:
            return {self.CsvFieldNames.item1_id: item1_main_fields.id,
                    self.CsvFieldNames.item1_desc: item1_main_fields.description,
                    self.CsvFieldNames.choice: "?",
                    self.CsvFieldNames.item2_id: item2_main_fields.id,
                    self.CsvFieldNames.item2_desc: item2_main_fields.description,
                    self.CsvFieldNames.timestamp: self.__timestamp}
        elif self.__choice is self.__item1:
            return {self.CsvFieldNames.item1_id: item1_main_fields.id,
                    self.CsvFieldNames.item1_desc: item1_main_fields.description,
                    self.CsvFieldNames.choice: ">",
                    self.CsvFieldNames.item2_id: item2_main_fields.id,
                    self.CsvFieldNames.item2_desc: item2_main_fields.description,
                    self.CsvFieldNames.timestamp: self.__timestamp}
        elif self.__choice is self.__item2:
            return {self.CsvFieldNames.item1_id: item2_main_fields.id,
                    self.CsvFieldNames.item1_desc: item2_main_fields.description,
                    self.CsvFieldNames.choice: ">",
                    self.CsvFieldNames.item2_id: item1_main_fields.id,
                    self.CsvFieldNames.item2_desc: item1_main_fields.description,
                    self.CsvFieldNames.timestamp: self.__timestamp}
        raise NotImplementedError()

    def get_item_1(self):
        return self.__item1

    def get_item_2(self):
        return self.__item2

    def get_bigger(self):
        return self.__choice

    def get_smaller(self):
        if self.__choice is self.__item2:
            return self.__item1
        if self.__choice is self.__item1:
            return self.__item2
        raise NotImplementedError()

    def __match1(self, item1: ItemWrapper, item2: ItemWrapper, choice, timestamp: float) -> bool:
        if choice != ">":
            return False
        if self.get_bigger() is None:
            return False
        if item1.get_id() != self.get_bigger().get_id():
            return False
        if item2.get_id() != self.get_smaller().get_id():
            return False
        if self.__timestamp != timestamp:
            return False
        return True

    def check_integrity(self):
        assert self.__item1.get_id() != self.__item2.get_id()

    def __match2(self, item1: ItemWrapper, item2: ItemWrapper, choice, timestamp: float) -> bool:
        self.check_integrity()
        if choice != "?":
            return False
        if self.__choice is not None:
            return False
        if item1.get_id() not in (self.__item1.get_id(), self.__item2.get_id()):
            return False
        if item2.get_id() not in (self.__item1.get_id(), self.__item2.get_id()):
            return False
        if self.__timestamp != float(timestamp):
            return False
        return True

    def add(self, bigger: ItemWrapper, smaller: ItemWrapper, choice, timestamp: float):
        if self.__match1(bigger, smaller, choice, timestamp):
            return
        if self.__match2(bigger, smaller, choice, timestamp):
            return
        raise NotImplementedError()

    def __repr__(self):
        return common_utils.common_repr(self, f"{self.format()}")

    def is_known(self):
        return self.__choice is not None

    def is_unknown(self):
        return self.__choice is None

    def contains_item_id(self, item_id):

        if self.__item2.match_id(item_id):
            return True
        if self.__item1.match_id(item_id):
            return True

        return False

    def is_certain(self):
        return self.__choice is not None

    def is_uncertain(self):
        return self.__choice is None

    def matches_list(self, items)-> bool:
        if self.__choice is None:
            return True
        bigger = self.get_bigger()
        smaller = self.get_smaller()
        try:
            bigger_index = items.index(bigger)
        except:
            return True
        try:
            smaller_index = items.index(smaller)
        except:
            return True
        if not bigger_index > smaller_index:
            logging.warning(f"broke integrity in {len(items)} item list: {self}")
            return False
        return True