def common_repr(object1, message):
    type_ = type(object1)
    module = type_.__module__
    qualname = type_.__qualname__
    return f"<{module}.{qualname} {message}, object at {hex(id(object1))}>"


def xor(a, b):
    return bool(a) != bool(b)