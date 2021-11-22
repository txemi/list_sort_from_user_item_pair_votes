import logging
import os
import pickle
import sys
from typing import Optional

import typeguard

from config import fail_on_vote_undecide
from item import ItemWrapper
from items import Items
from votes import VotesCache


class VoteUndecidedException(Exception):
    pass


@typeguard.typechecked
def _question(item1: ItemWrapper, item2: ItemWrapper):
    assert item1.get_id() != item2.get_id()
    while True:
        sys.stdout.write(
            "Witch one rate higher? 1:<<<{0}>>> , 2:<<<{1}>>> n:cannot say?".format(item1.format_short(),
                                                                                    item2.format_short()))
        if True:
            choice = input().lower()
        else:
            choice = True

        if choice == '2':
            # arg1<arg2
            bigger = item2
            break
        elif choice == '1':
            # arg1>arg2
            bigger = item1
            break
        elif choice == 'n':
            # arg1>arg2
            bigger = None
            break
        else:
            sys.stdout.write(f"bad answer {choice}")
    return bigger


@typeguard.typechecked
def _get_cmp_ret(item1: ItemWrapper, item2: ItemWrapper, choice: Optional[ItemWrapper]):
    if choice is item2:
        ret = -1
    elif choice is item1:
        # arg1>arg2
        ret = 1
    elif choice is None:
        if fail_on_vote_undecide:
            raise VoteUndecidedException()
        else:
            ret = 0
    else:
        raise Exception()
    return ret


@typeguard.typechecked
class UserVoteUiMaker:
    def __load_from_pickle(self, filename):
        with open(filename, 'rb') as file:
            logging.debug("loading previous cache")
            self.__votes = pickle.load(file)
            assert isinstance(self.__votes, VotesCache)
            self.__votes.print()

    def __save_to_file(self):
        with open(self.__pickle_filename(), 'wb') as file:
            pickle.dump(self.__votes, file)
        self.__votes.save_to_csv_file(self.__csv_filename())

    def __pickle_filename(self):
        return self.__filename_base + ".pickle"

    def __csv_filename(self):
        return self.__filename_base + ".csv"

    def __init__(self, filename, items: Items):
        self.__filename_base = filename
        if os.path.exists((self.__pickle_filename())):
            self.__load_from_pickle(self.__pickle_filename())
        else:
            self.__votes = VotesCache(items)
        if os.path.exists(self.__csv_filename()):
            self.__votes.load_from_csv(self.__csv_filename())

    def cmp_query_cache_or_ask_user_implementation(self, item1: ItemWrapper, item2: ItemWrapper):
        # return 1 if a > b else 0 if a == b else -1
        found_in_cache = self.__votes.get(item1, item2)
        if found_in_cache is not None:
            bigger = found_in_cache.get_choice()
        else:
            bigger = _question(item1, item2)
            if not (bigger is None or isinstance(bigger, ItemWrapper)):
                raise Exception()
            self.__votes.add(item1, item2, bigger)
            self.__save_to_file()

        ret = _get_cmp_ret(item1, item2, bigger)
        return ret

    def get_elements_with_known_votes(self):
        known, unknown = self.__votes.get_elements_with_known_votes()
        return known, unknown

    def get_items_sorted_by_certainty(self):
        return self.__votes.get_items_sorted_by_certainty()

    def find_votes_not_matching_list(self, items) -> list:
        return self.__votes.find_votes_not_matching_list(items)

    def get_votes(self):
        return self.__votes
