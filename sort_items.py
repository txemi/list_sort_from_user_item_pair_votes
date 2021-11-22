import bisect
import enum
import functools
import logging

import typeguard

import item as item_package
from item import ItemWrapper
from items import Items
from user_questions import UserVoteUiMaker, VoteUndecidedException


@typeguard.typechecked
class SortStrategy(enum.Enum):
    Random = enum.auto()
    PrioritizeCertainty = enum.auto()


@typeguard.typechecked
def sort_items_from_csv(filename: str, mode: SortStrategy):
    items = Items(filename)
    items.print()
    user_vote_ui_maker = UserVoteUiMaker(filename + ".votes", items)

    @typeguard.typechecked
    def cmp_implementation_func(item1: ItemWrapper, item2: ItemWrapper):
        if item1.get_id() == item2.get_id():
            raise NotImplementedError()
        return user_vote_ui_maker.cmp_query_cache_or_ask_user_implementation(item1, item2)

    if mode == SortStrategy.Random:
        sorted_dict = sorted(items.get_wrapped_items_randomized(), key=functools.cmp_to_key(cmp_implementation_func),
                             reverse=True)
        return sorted_dict
    else:
        sorted_list = Items(filename + ".out.csv", load_csv=False)
        items_prioritized = user_vote_ui_maker.get_items_sorted_by_certainty()
        item_package.cmp_imp = cmp_implementation_func
        items_prioritized.reverse()
        for next_element in items_prioritized:
            logging.debug("Before insort: {}".format(sorted_list))
            bisect.insort(sorted_list.get_items(), next_element)
            logging.debug("After insort: {}".format(sorted_list))
            sorted_list.write_csv()
            not_matching = user_vote_ui_maker.find_votes_not_matching_list(sorted_list)
            if not_matching:
                logging.warning(f"found {len(not_matching)} not matching votes")
        user_vote_ui_maker.get_votes().enrich_items_with_stats(sorted_list)
        sorted_list.write_csv()
        return sorted_list


@typeguard.typechecked
def sort_items_from_csv_loop(filename: str, mode):
    while True:
        logging.debug("{} Loop start".format(__name__))
        try:
            sorted_items = sort_items_from_csv(filename, mode)
            return sorted_items
        except VoteUndecidedException:
            pass
