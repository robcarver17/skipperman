from copy import copy
import datetime
import enum
from enum import EnumMeta
from dataclasses import dataclass
from typing import List
import pandas as pd

from app.objects.utils import (
    create_list_of_objects_from_dataframe,
    data_object_as_dict,
    get_list_of_attributes,
    get_dict_of_class_attributes,
transform_date_into_str,
transform_datetime_into_str,
transform_str_into_datetime,
transform_str_into_date,
clean_up_dict_with_nans
)

KEYS = "Keys"
VALUES = "Values"

class GenericSkipperManObject:
    def __eq__(self, other):
        return self.__hash__()== other.__hash__()

    def __hash__(self):
        list_of_attributes = get_list_of_attributes(self)
        str_dict_repr = "_".join([str(getattr(self, key)) for key in list_of_attributes])
        return hash(str_dict_repr)

    @classmethod
    def create_empty(cls):
        list_of_attributes = get_list_of_attributes(cls)
        dict_of_nones = dict([(attribute, None) for attribute in list_of_attributes])

        return cls(**dict_of_nones)


    @classmethod
    def from_str(cls, object_as_str: str):
        as_list_of_str = object_as_str.split(",")
        as_list_of_key_value_pairs = [key_value_as_str.split(":") for key_value_as_str in as_list_of_str]
        as_dict = dict([(key,value) for key,value in as_list_of_key_value_pairs])

        return cls.from_dict(as_dict)

    def to_str(self)-> str:
        as_str_dict = self.as_str_dict()
        as_list_of_str = ["%s:%s" % (key, value) for key,value in as_str_dict.items()]

        return ",".join(as_list_of_str)

    def to_df_of_str(self) -> pd.DataFrame:
        as_str_dict = self.as_str_dict()
        return pd.DataFrame({KEYS: as_str_dict.keys(), VALUES: as_str_dict.values()})

    @classmethod
    def from_df_of_str(self, df: pd.DataFrame):
        new_df = df.drop(KEYS, axis=1)
        new_df.index = df[KEYS]
        as_dict = new_df.squeeze().to_dict()

        return self.from_dict(as_dict)

    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()
        _transform_class_dict_into_str_dict(self, as_dict)

        return as_dict

    def as_dict(self) -> dict:
        return data_object_as_dict(self)

    @classmethod
    def from_dict(cls, dict_with_str):
        class_instance = get_class_instance_from_str_dict(cls, dict_with_str)

        return class_instance


class GenericSkipperManObjectWithIds(GenericSkipperManObject):
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self) -> str:
        raise NotImplemented


def _transform_class_dict_into_str_dict(
    some_class_instance: GenericSkipperManObjectWithIds, class_dict: dict
):
    ## don't need to check attributes match is guaranteed
    list_of_attributes = get_list_of_attributes(some_class_instance)

    for attribute_name in list_of_attributes:
        attribute = getattr(some_class_instance, attribute_name)
        class_dict[attribute_name] = _transform_class_instance_into_string(attribute)


def _transform_class_instance_into_string(class_instance):
    if isinstance(class_instance, datetime.date):
        return transform_date_into_str(class_instance)
    elif isinstance(class_instance, datetime.datetime):
        return transform_datetime_into_str(class_instance)
    elif isinstance(class_instance, enum.Enum):
        return class_instance.name
    elif isinstance(class_instance, bool):
        if class_instance:
            return TRUE
        else:
            return FALSE
    else:
        return str(class_instance)


TRUE = "TRUE_VALUE"
FALSE = "FALSE_VALUE"


def get_class_instance_from_str_dict(some_class, dict_with_str: dict):
    dict_with_str = clean_up_dict_with_nans(dict_with_str)
    dict_of_attributes = get_dict_of_class_attributes(some_class)

    for attribute, object_class in dict_of_attributes.items():
        string = dict_with_str[attribute]
        dict_with_str[attribute] = _transform_string_into_class_instance(
            object_class, string
        )

    return some_class(**dict_with_str)


def _transform_string_into_class_instance(object_class, string):
    if object_class is datetime.date:
        return transform_str_into_date(string)
    elif object_class is datetime.datetime:
        return transform_str_into_datetime(string)
    elif type(object_class) is EnumMeta:
        return object_class[string]
    elif object_class is bool:
        return string == TRUE

    ## this will work for non strings eg floats
    return object_class(string)


class GenericListOfObjects(list):
    def __init__(self, list_of_objects: List[GenericSkipperManObject]):
        super().__init__(list_of_objects)

    def __repr__(self):
        return str(self.to_df())


    @classmethod
    def create_empty(cls):
        return cls([])

    @property
    def _object_class_contained(self):
        raise Exception

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        empty_instance = cls.create_empty()
        contained_class = empty_instance._object_class_contained
        list_of_items = create_list_of_objects_from_dataframe(contained_class, df)

        return cls(list_of_items)

    def to_df(self) -> pd.DataFrame:
        list_of_dicts = [item.as_dict() for item in self]

        return pd.DataFrame(list_of_dicts)

    def to_df_of_str(self) -> pd.DataFrame:
        list_of_dicts = [item.as_str_dict() for item in self]

        return pd.DataFrame(list_of_dicts)


class GenericListOfObjectsWithIds(GenericListOfObjects):
    def __init__(self, list_of_objects: List[GenericSkipperManObjectWithIds]):
        super().__init__(list_of_objects)

    def pop_with_id(self, id):
        index = self.index_of_id(id)
        return self.pop(index)

    def object_with_id(self, id: str):
        index = self.index_of_id(id)

        return self[index]

    def index_of_id(self, id) -> int:
        list_of_ids = self.list_of_ids
        index = list_of_ids.index(id)

        return index

    @classmethod
    def subset_from_list_of_ids(
        cls, full_list: "GenericListOfObjectsWithIds", list_of_ids: list
    ):
        subset_list = [full_list.has_id(id) for id in list_of_ids]

        return cls(subset_list)

    def replace_with_new_object(self, new_object):
        idx = self.index_of_object_with_id(new_object.id)
        self[idx] = new_object

    def has_id(self, id: str):
        idx = self.index_of_object_with_id(id)
        return self[idx]

    def index_of_object_with_id(self, id: str):
        list_of_ids = self.list_of_ids
        try:
            idx = list_of_ids.index(id)
        except ValueError:
            raise Exception("id %s not in list" % id)

        return idx

    @property
    def list_of_ids(self) -> list:
        return [item.id for item in self]


    def next_id(self) -> str:
        if len(self) == 0:
            return 1
        list_of_ids = self.list_of_ids
        list_of_ids_as_int = [int(id) for id in list_of_ids]
        max_id = max(list_of_ids_as_int)
        next_id = max_id + 1

        return str(next_id)
