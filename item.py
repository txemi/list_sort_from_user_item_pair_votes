import typeguard


class MainFields:

    def __init__(self, id_, description):
        self.id = id_
        self.description = description


cmp_imp = None


@typeguard.typechecked
class ItemWrapper:
    def __init__(self, item_data: dict):
        self.__data = item_data

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
        # TODO: guess id
        if "id" in self.__data:
            return int(self.__data.get("id"))
        if "Const" in self.__data:
            a = self.__data.get("Const")
            return int(a)
        raise NotImplementedError()

    def get_main_fields(self) -> MainFields:
        return MainFields(self.get_id(), self.format_description())

    def __repr__(self):
        type_ = type(self)
        module = type_.__module__
        qualname = type_.__qualname__
        return f"<{module}.{qualname} {self.format_short()} object at {hex(id(self))}>"

    def match_id(self, item_id):
        if self.get_id() == item_id:
            return True
        return False

    def get_data(self):
        return self.__data
