import datetime
import pandas as pd
from difflib import SequenceMatcher

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