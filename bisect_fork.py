"""Bisection algorithms."""


def insort_right_1(a, x, lo=0, hi=None, *, key=None, mid_func=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if key is None:
        lo = bisect_right_1(a, x, lo, hi, mid_func=mid_func)
    else:
        lo = bisect_right_1(a, key(x), lo, hi, key=key)
    a.insert(lo, x)


def bisect_right_1(a, x, lo=0, hi=None, *, key=None, mid_func=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    while lo < hi:
        if mid_func is None:
            mid = (lo + hi) // 2
        else:
            mid = mid_func(a, lo, hi)
        if x < (a[mid] if key is None else key(a[mid])):
            hi = mid
        else:
            lo = mid + 1

    return lo


def insort_left(a, x, lo=0, hi=None, *, key=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the left of the leftmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if key is None:
        lo = bisect_left(a, x, lo, hi)
    else:
        lo = bisect_left(a, key(x), lo, hi, key=key)
    a.insert(lo, x)


def bisect_left(a, x, lo=0, hi=None, *, key=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    while lo < hi:
        mid = (lo + hi) // 2
        if (a[mid] if key is None else key(a[mid])) < x:
            lo = mid + 1
        else:
            hi = mid

    return lo


# Create aliases
bisect = bisect_right_1
insort = insort_right_1
