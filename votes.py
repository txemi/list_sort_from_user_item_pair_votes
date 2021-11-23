import csv
import functools
import logging
from typing import Optional

import typeguard

from common_utils import common_repr
from item import ItemWrapper
from items import Items
from vote import ItemPairVote
from vote import ItemPairVoteKey


@typeguard.typechecked
class VotesCache:
    def __init__(self, items: Items):
        self.__votes = {}  # type: dict[ItemPairVoteKey, ItemPairVote]
        self.__items = items  # type: Items

    def add(self, x: ItemWrapper, y: ItemWrapper, choice: Optional[ItemWrapper], timestamp: float = None):
        assert typeguard.check_argument_types()
        new_vote = ItemPairVote(x, y, choice, timestamp)
        new_key = new_vote.get_key()
        assert isinstance(new_key, ItemPairVoteKey)
        if new_key in self.__votes:
            self.__votes[new_key].addVote(new_vote)
            pass
        else:
            self.__votes[new_key] = ItemPairVote(x, y, choice)

    def get(self, x: ItemWrapper, y: ItemWrapper) -> Optional[ItemPairVote]:
        key = ItemPairVote.get_key_static(x, y)
        if key in self.__votes:
            return self.__votes[key]
        return None

    def format(self):
        return "\n".join(map(lambda x: x.format(), self.__votes.values()))

    def print(self) -> None:
        logging.debug("{} {} elements begin".format(self.__class__.__name__, len(self.__votes)))
        logging.debug(self.format())
        logging.debug("{} {} elements end".format(self.__class__.__name__, len(self.__votes)))

    def save_to_csv_file(self, filename):
        votes = self.__votes.values()
        votes_dicts = list(map(lambda x: x.build_dict_for_csv(), votes))

        csv_columns = ItemPairVote.CsvFieldNames.csv_headers
        dict_data = votes_dicts
        csv_file = filename

        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)

    def get_elements_with_known_votes(self):
        items = set()
        have_unknown = set()
        for vote in self.__votes.values():
            items.add(vote.get_item_1())
            items.add(vote.get_item_2())

            if vote.is_unknown():
                have_unknown.add(vote.get_item_1())
                have_unknown.add(vote.get_item_2())

        return items - have_unknown, have_unknown

    def get_item_uncertainty(self, item1: ItemWrapper):
        return sum(1 for vote in self.__votes.values() if vote.contains_item_id(item1.get_id()) and vote.is_uncertain())

    def get_item_certainty(self, item1: ItemWrapper):
        return sum(1 for vote in self.__votes.values() if vote.contains_item_id(item1.get_id()) and vote.is_certain())

    def items_certainty_rank_comparator_lt(self, item1: ItemWrapper, item2: ItemWrapper):
        item1_un = self.get_item_uncertainty(item1)
        item2_un = self.get_item_uncertainty(item2)
        if item1_un > item2_un:
            return True
        if item2_un > item1_un:
            return False
        item1_cer = self.get_item_certainty(item1)
        item2_cer = self.get_item_certainty(item2)
        if item1_cer < item2_cer:
            return True
        if item1_cer > item2_cer:
            return False
        return False

    def items_certainty_rank_comparator(self, item1: ItemWrapper, item2: ItemWrapper):
        item1_un = self.get_item_uncertainty(item1)
        item2_un = self.get_item_uncertainty(item2)
        if item1_un > item2_un:
            return -1
        if item1_un < item2_un:
            return 1
        item1_cer = self.get_item_certainty(item1)
        item2_cer = self.get_item_certainty(item2)
        if item1_cer < item2_cer:
            return -1
        if item1_cer > item2_cer:
            return 1
        return 0

    def get_items_sorted_by_certainty(self):
        parent_self = self

        def items_certainty_rank_comparator_1(item1: ItemWrapper, item2: ItemWrapper):
            return parent_self.items_certainty_rank_comparator(item1, item2)

        return sorted(self.__items.get_wrapped_items(), key=functools.cmp_to_key(items_certainty_rank_comparator_1))

    def get_items_from_ids(self, item1_id: int, item2_id: int):
        bigger = self.__items.get_item_by_id(item1_id)
        smaller = self.__items.get_item_by_id(item2_id)
        return bigger, smaller

    def get_vote_from_pair(self, bigger_id: int, smaller_id: int) -> Optional[ItemPairVote]:
        if len(self.__votes) == 0:
            return None
        bigger, smaller = self.get_items_from_ids(bigger_id, smaller_id)
        smaller = self.__items.get_item_by_id(smaller_id)
        uu = self.get(bigger, smaller)
        return uu

    def add_vote_from_ids(self, bigger_id, smaller_id, timestamp: float):
        vote = self.get_vote_from_pair(bigger_id, smaller_id)
        assert vote is None
        bigger, smaller = self.get_items_from_ids(bigger_id, smaller_id)
        self.add(bigger, smaller, bigger, timestamp)

    def load_from_csv(self, filename):
        with open(filename, newline='', encoding='utf-8-sig') as csvfile:
            spamreader = csv.DictReader(csvfile)
            for row in spamreader:
                bigger_id = int(row[ItemPairVote.CsvFieldNames.item1_id])
                smaller_id = int(row[ItemPairVote.CsvFieldNames.item2_id])
                choice = row[ItemPairVote.CsvFieldNames.choice]
                if ItemPairVote.CsvFieldNames.timestamp in row:
                    timestamp = float(row[ItemPairVote.CsvFieldNames.timestamp])
                else:
                    timestamp = None
                found = self.get_vote_from_pair(bigger_id, smaller_id)
                if found is None:
                    self.add_vote_from_ids(bigger_id, smaller_id, timestamp)
                else:
                    bigger, smaller = self.get_items_from_ids(bigger_id, smaller_id)
                    found.add(bigger, smaller, choice, timestamp)
        pass

    def __repr__(self):
        return common_repr(f"{len(self.__votes)} elements")

    def find_votes_not_matching_list(self, items: Items):
        not_matches = []
        for vote in self.__votes.values():
            if not vote.matches_list(items):
                not_matches.append(vote)
        return not_matches

    def enrich_items_with_stats(self, items: Items):
        votes_not_matching = self.find_votes_not_matching_list(items)
        for item in items.get_wrapped_items():
            cer = self.get_item_certainty(item)
            un = self.get_item_uncertainty(item)
            for vnm in votes_not_matching:
                raise NotImplementedError()
            item.update("cer", cer)
            item.update("un", un)

    def has_certain_vote(self, item1, item2):
        found_in_cache = self.get(item1, item2)
        if found_in_cache is not None:
            return True
        return False
