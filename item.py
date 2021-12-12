import typeguard

from common_utils import common_repr


class MainFields:

    def __init__(self, id_, description):
        self.id = id_
        self.description = description


# TODO: find more elegant way to inject behaviour
cmp_imp = None


@typeguard.typechecked
class ItemWrapper:
    def __init__(self, item_data: dict, id_field: str):
        self.__data = item_data
        self.__id_field_name = id_field

    def format_description(self):
        # TODO: guess description
        if "Grupo" in self.__data and "Práctica" in self.__data:
            return self.__data["Grupo"] + "->" + self.__data["Práctica"]
        if "Title" in self.__data and "URL" in self.__data:
            return self.__data["Title"] + "(" + self.__data["Year"] + ") " + self.__data["URL"]
        raise NotImplementedError()

    def format_short(self):
        return str(self.get_id()) + ":" + self.format_description()

    def __lt__(self, other):
        return cmp_imp(self, other) < 0

    def __cmp__(self, other):
        return cmp_imp(self, other)

    def get_id(self):
        return int(self.__data.get(self.__id_field_name))

    def get_main_fields(self) -> MainFields:
        return MainFields(self.get_id(), self.format_description())

    def __repr__(self):
        return common_repr(self, f"{self.format_short()}")

    def match_id(self, item_id):
        if self.get_id() == item_id:
            return True
        return False

    def get_data(self):
        return self.__data

    def update(self, key, value):
        self.__data[key] = value
