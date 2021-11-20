# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import logging

from sort_items import SortStrategy
from sort_items import sort_items_from_csv_loop

if __name__ == '__main__':
    logging.basicConfig(format="%(module)s:%(filename)s:%(funcName)s:%(message)s", level=logging.DEBUG)
    logging.debug('logger configured')
    filename = 'items.csv'
    strategy = SortStrategy.Advanced
    sortedDict = sort_items_from_csv_loop(filename, strategy)
