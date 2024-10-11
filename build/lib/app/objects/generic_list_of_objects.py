from typing import List
import pandas as pd
from app.objects.exceptions import MissingData
from app.objects.generic_objects import GenericSkipperManObject, GenericSkipperManObjectWithIds, \
    get_list_of_attributes


class GenericListOfObjects(list):
    def __init__(self, list_of_objects: List[GenericSkipperManObject]):
        super().__init__(list_of_objects)

    def __repr__(self):
        return str(self.as_df_of_str())

    @classmethod
    def create_empty(cls):
        return cls([])

    @property
    def _object_class_contained(self):
        raise Exception

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        contained_class = get_contained_class(cls)
        list_of_items = create_list_of_objects_from_dataframe(contained_class, df)

        return cls(list_of_items)

    def as_df_of_str(self) -> pd.DataFrame:
        return create_data_frame_given_list_of_objects(self)


def get_contained_class(cls):
    empty_instance = cls.create_empty()
    contained_class = empty_instance._object_class_contained

    return contained_class

class GenericListOfObjectsWithIds(GenericListOfObjects):
    def __init__(self, list_of_objects: List[GenericSkipperManObjectWithIds]):
        super().__init__(list_of_objects)

    def __repr__(self):
        return self.as_str()

    def as_str(self):
        return ", ".join([str(object) for object in self])

    def pop_with_id(self, id):
        index = self.index_of_id(id)
        return self.pop(index)

    def object_with_id(self, id: str):
        index = self.index_of_id(id)

        return self[index]

    def index_of_id(self, id) -> int:
        list_of_ids = self.list_of_ids
        try:
            index = list_of_ids.index(id)
        except ValueError:
            raise MissingData("id %s is missing" % id)

        return index

    @classmethod
    def subset_from_list_of_ids(
        cls, full_list: "GenericListOfObjectsWithIds", list_of_ids: List[str]
    ):
        subset_list = [
            full_list.object_with_id(id) for id in full_list.list_of_ids if id in list_of_ids
        ]

        return cls(subset_list)

    def replace_with_new_object(self, new_object):
        idx = self.index_of_id(new_object.id)
        self[idx] = new_object

    @property
    def list_of_ids(self) -> list:
        return [item.id for item in self]

    def next_id(self) -> str:
        if len(self) == 0:
            return '1'

        max_id = self.max_id()
        next_id = max_id + 1

        return str(next_id)

    def max_id(self) -> int:
        list_of_ids = self.list_of_ids
        list_of_ids_as_int = [int(id) for id in list_of_ids]
        max_id = max(list_of_ids_as_int)

        return max_id


def create_list_of_objects_from_dataframe(class_of_object: GenericSkipperManObject, df: pd.DataFrame):
    list_of_objects = [
        create_object_from_df_row(class_of_object=class_of_object, row=row)
        for index, row in df.iterrows()
    ]

    return list_of_objects


def create_data_frame_given_list_of_objects(list_of_objects: List[GenericSkipperManObject]) -> pd.DataFrame:
    list_of_dicts = [item.as_str_dict() for item in list_of_objects]

    return pd.DataFrame(list_of_dicts)


def create_object_from_df_row(class_of_object: GenericSkipperManObject, row: pd.Series):
    row_as_dict = row.to_dict()

    try:
        object = class_of_object.from_dict_of_str(row_as_dict)
    except Exception as exception:
        raise Exception(
            _error_str_when_creating_object_from_df_row(
                class_of_object=class_of_object, row_as_dict=dict(row_as_dict),
                exception=exception
            )
        )

    return object


def _error_str_when_creating_object_from_df_row(class_of_object, row_as_dict: dict, exception: Exception):
    if getattr(class_of_object, "from_dict_of_str", None) is None:
        return Exception(
            "Class %s requires .from_dict_of_str() method" % (str(class_of_object))
        )
    list_of_attributes = get_list_of_attributes(some_class=class_of_object)
    return Exception(
        "Class %s requires elements %s element %s doesn't match exception %s"
        % (str(class_of_object), str(list_of_attributes), str(row_as_dict), str(exception))
    )

