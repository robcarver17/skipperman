import datetime
import enum
from enum import EnumMeta

import pandas as pd

from app.objects.utils import (
    transform_date_into_str,
    transform_datetime_into_str,
    clean_up_dict_with_nans,
    clean_up_dict_with_weird_floats_for_id,
    transform_str_or_datetime_into_date,
    transform_str_into_datetime,
    dict_as_str,
    dict_from_str,
)

KEYS = "Keys"
VALUES = "Values"


class GenericSkipperManObject:
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        list_of_attributes = get_list_of_attributes(self)
        str_dict_repr = "_".join(
            [str(getattr(self, key)) for key in list_of_attributes]
        )
        return hash(str_dict_repr)

    @classmethod
    def create_empty(cls):
        list_of_attributes = get_list_of_attributes(cls)
        dict_of_nones = dict([(attribute, None) for attribute in list_of_attributes])

        return cls(**dict_of_nones)

    def as_df_of_str(self) -> pd.DataFrame:
        as_str_dict = self.as_str_dict()
        return pd.DataFrame({KEYS: as_str_dict.keys(), VALUES: as_str_dict.values()})

    @classmethod
    def from_df_of_str(self, df: pd.DataFrame):
        new_df = df.drop(KEYS, axis=1)
        new_df.index = df[KEYS]
        as_dict = new_df.squeeze().to_dict()

        return self.from_dict_of_str(as_dict)

    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()
        transform_class_dict_into_str_dict(self, as_dict)

        return as_dict

    def as_dict(self) -> dict:
        return data_object_as_dict(self)

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        class_instance = get_class_instance_from_str_dict(cls, dict_with_str)

        return class_instance


def transform_class_instance_into_string(class_instance):
    if isinstance(class_instance, datetime.date):
        return transform_date_into_str(class_instance)
    elif isinstance(class_instance, datetime.datetime):
        return transform_datetime_into_str(class_instance)
    elif isinstance(class_instance, enum.Enum):
        return class_instance.name
    elif isinstance(class_instance, bool):
        return from_bool_to_str(class_instance)
    elif isinstance(class_instance, dict):
        return dict_as_str(class_instance)
    else:
        return str(class_instance)


TRUE = "TRUE_VALUE"
FALSE = "FALSE_VALUE"


def from_bool_to_str(class_instance: bool) -> str:
    if class_instance:
        return TRUE
    else:
        return FALSE


ITEM_SEPERATOR = ","
KEY_VALUE_SEPERATOR = ":"


def get_class_instance_from_str_dict(some_class, dict_with_str: dict):
    dict_with_str = clean_up_dict_with_nans(dict_with_str)
    dict_with_str = clean_up_dict_with_weird_floats_for_id(dict_with_str)
    dict_of_attributes = get_dict_of_class_attributes(some_class)

    for attribute, object_class in dict_of_attributes.items():
        string = dict_with_str[attribute]
        dict_with_str[attribute] = transform_string_into_class_instance(
            object_class, string
        )

    return some_class(**dict_with_str)


def transform_string_into_class_instance(object_class, string):
    if object_class is datetime.date:
        return transform_str_or_datetime_into_date(string)
    elif object_class is datetime.datetime:
        return transform_str_into_datetime(string)
    elif type(object_class) is EnumMeta:
        return object_class[string]
    elif object_class is bool:
        return from_str_to_bool(string)
    elif object_class is dict:
        return dict_from_str(string)

    ## this will work for non strings eg floats
    return object_class(string)


def from_str_to_bool(string: str) -> bool:
    return string == TRUE


def data_object_as_dict(some_object) -> dict:
    list_of_attributes = get_list_of_attributes(some_object)

    object_as_dict = dict(
        [(key, getattr(some_object, key)) for key in list_of_attributes]
    )

    return object_as_dict


def get_list_of_attributes(some_class) -> list:
    dict_of_attributes = get_dict_of_class_attributes(some_class)
    return list(dict_of_attributes.keys())


def get_dict_of_class_attributes(some_class) -> dict:
    return some_class.__annotations__


def transform_class_dict_into_str_dict(
    some_class_instance: GenericSkipperManObject, class_dict: dict
):
    ## don't need to check attributes match is guaranteed
    list_of_attributes = get_list_of_attributes(some_class_instance)

    for attribute_name in list_of_attributes:
        attribute = getattr(some_class_instance, attribute_name)
        class_dict[attribute_name] = transform_class_instance_into_string(attribute)


class GenericSkipperManObjectWithIds(GenericSkipperManObject):
    @property
    def id(self) -> str:
        raise NotImplemented
