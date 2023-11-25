from collections import defaultdict
import datetime
import math
from dataclasses import dataclass

import pandas as pd
from difflib import SequenceMatcher
from app.objects.constants import arg_not_passed

DATE_FORMAT_STRING = "%Y/%m/%d"


def transform_date_from_str(date_str: str) -> datetime.date:
    if type(date_str) is datetime.date:
        return date_str

    return datetime.datetime.strptime(date_str, DATE_FORMAT_STRING).date()


def transform_str_from_date(date: datetime.date) -> str:
    if type(date) is str:
        return date

    return datetime.date.strftime(date, DATE_FORMAT_STRING)


def data_object_as_dict(some_object) -> dict:
    list_of_attributes = get_list_of_attributes(some_object)

    object_as_dict = dict(
        [(key, getattr(some_object, key)) for key in list_of_attributes]
    )

    return object_as_dict


def create_list_of_objects_from_dataframe(class_of_object, df: pd.DataFrame):

    list_of_objects = [
        create_object_from_df_row(class_of_object=class_of_object, row=row)
        for index, row in df.iterrows()
    ]

    return list_of_objects


def create_object_from_df_row(class_of_object, row: pd.Series):
    row_as_dict = row.to_dict()

    try:
        object = class_of_object.from_dict(row_as_dict)
    except:
        raise Exception(
            _error_str_when_creating_object_from_df_row(
                class_of_object=class_of_object, row_as_dict=dict(row_as_dict)
            )
        )

    return object


def _error_str_when_creating_object_from_df_row(class_of_object, row_as_dict: dict):
    if getattr(class_of_object, "from_dict", None) is None:
        return Exception(
            "Class %s requires .from_dict() method" % (str(class_of_object))
        )
    list_of_attributes = get_list_of_attributes(some_class=class_of_object)
    return Exception(
        "Class %s requires elements %s element %s doesn't match"
        % (str(class_of_object), str(list_of_attributes), str(row_as_dict))
    )


def get_list_of_attributes(some_class) -> list:
    dict_of_attributes = get_dict_of_class_attributes(some_class)
    return list(dict_of_attributes.keys())


def get_dict_of_class_attributes(some_class) -> dict:
    return some_class.__annotations__


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


@dataclass
class SingleDiff:
    old_value: object
    new_value: object


class DictOfDictDiffs(dict):
    def __str__(self):
        return string_of_dict_diffs(self)


def create_dict_of_dict_diffs(dict_old: dict, dict_new: dict, comparing_fields: list = arg_not_passed ) -> DictOfDictDiffs:
    # dict
    # throws exception if missing or added fields
    if comparing_fields is arg_not_passed:
        keys_old = list(dict_old.keys())
        keys_new = list(dict_new.keys())
        try:
            assert set(keys_old) == set(keys_new)
        except:
            raise Exception("Have to have matching keys to automatically see differences")
        comparing_fields = keys_new

    dict_of_diffs = {}
    for key in comparing_fields:
        old_value = dict_old[key]
        new_value = dict_new[key]
        if old_value != new_value:
            dict_of_diffs[key] = SingleDiff(old_value=old_value, new_value=new_value)

    return DictOfDictDiffs(dict_of_diffs)


def string_of_dict_diffs(dict_of_diffs: DictOfDictDiffs) -> str:
    full_string = [
        "For %s, old value is %s new value is %s"
        % (key, diff.old_value, diff.new_value)
        for key, diff in dict_of_diffs.items()
    ]
    return "\n".join(full_string)


def clean_up_dict_with_nans(some_dict) -> dict:
    for key, value in some_dict.items():
        try:
            if math.isnan(value):
                some_dict[key] = ""
        except:
            ## another type
            pass
    return some_dict


def list_duplicate_indices(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return [locs for locs in tally.values()
                            if len(locs)>1]

