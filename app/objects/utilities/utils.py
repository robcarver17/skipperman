from collections import Counter

from difflib import SequenceMatcher

from itertools import groupby

OPTIMAL_LINE_LENGTH = 20


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def in_x_not_in_y(x: list, y: list) -> list:
    return list(set(x).difference(set(y)))


def in_both_x_and_y(x: list, y: list) -> list:
    return list(set(x).intersection(set(y)))


def union_of_x_and_y(x: list, y: list) -> list:
    return list(set(x).union(set(y)))


def flatten(xss):
    return [x for xs in xss for x in xs]


def print_dict_nicely(label, some_dict: dict) -> str:
    dict_str_list = ["%s: %s" % (key, value) for key, value in some_dict.items()]
    dict_str_list = ", ".join(dict_str_list)

    return label + "- " + dict_str_list


def most_common(some_list: list, default=""):
    if len(some_list) == 0:
        return default
    return Counter(some_list).most_common(1)[0][0]


def we_are_not_the_same(some_list: list) -> bool:
    return len(set(some_list)) > 1


def has_hidden_attribute(object):
    return hasattr(object, "hidden")


def is_protected_object(object):
    return getattr(object, "protected", False)


def print_list(x, name):
    print("%s:" % name)
    for y in x:
        print(str(y))


def percentage_of_x_in_y(idx_of_x, y_has_length) -> int:
    len_y = len(y_has_length)
    if len_y == 0:
        return 100

    return int(100 * float(idx_of_x) / len_y)


def simplify_and_display(some_list, linker=", "):
    if len(some_list) == 0:
        return ""
    unique_list = list(set(some_list))
    if len(unique_list) == 1:
        return str(unique_list[0])

    return linker.join(unique_list)


def all_spaces_or_commas(x: str):
    xx = x.replace(",", "")
    xx = xx.replace(" ", "")
    if len(xx)==0:
        return True
