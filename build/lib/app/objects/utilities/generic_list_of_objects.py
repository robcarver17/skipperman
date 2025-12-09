from typing import List
import pandas as pd
from app.objects.utilities.exceptions import (
    MissingData,
    arg_not_passed,
    MultipleMatches,
)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObject,
    GenericSkipperManObjectWithIds,
    get_list_of_attributes,
)


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

    def list_of_names(self):
        return [item.name for item in self]


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

    def object_with_id(self, id: str, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_value=id, attr_name="id", default=default
        )

    def index_of_id(self, id: str, default=arg_not_passed) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self, attr_value=id, attr_name="id", default=default
        )

    def subset_from_list_of_ids_retaining_order(self, list_of_ids: List[str]):
        subset_list = [
            object_in_list
            for object_in_list in self
            if object_in_list.id in list_of_ids
        ]

        return self.__class__(subset_list)

    @property
    def list_of_ids(self) -> list:
        return [item.id for item in self]

    def next_id(self) -> str:
        if len(self) == 0:
            return "1"

        max_id = self.max_id()
        next_id = max_id + 1

        return str(next_id)

    def max_id(self) -> int:
        list_of_ids = self.list_of_ids
        list_of_ids_as_int = [int(id) for id in list_of_ids]
        max_id = max(list_of_ids_as_int)

        return max_id


def get_unique_object_with_attr_in_list(
    some_list: list, attr_value, attr_name="id", default=arg_not_passed
):
    idx = get_idx_of_unique_object_with_attr_in_list(
        some_list=some_list,
        attr_value=attr_value,
        attr_name=attr_name,
        default=index_not_found,
    )
    if idx is index_not_found:
        if default is arg_not_passed:
            raise MissingData("%s = %s not found" % (attr_name, attr_value))
        else:
            return default

    return some_list[idx]


def get_idx_of_unique_object_with_attr_in_list(
    some_list: list, attr_value, attr_name="id", default=arg_not_passed
):
    list_of_idx = [
        idx
        for idx, object_in_list in enumerate(some_list)
        if getattr(object_in_list, attr_name) == attr_value
    ]
    if len(list_of_idx) == 0:
        if default is arg_not_passed:
            raise MissingData("%s = %s not found" % (attr_name, attr_value))
        else:
            return default

    elif len(list_of_idx) > 1:
        raise MultipleMatches("Multiple matches for %s=%s" % (attr_name, attr_value))
    else:
        return list_of_idx[0]


def get_unique_object_with_multiple_attr_in_list(
    some_list: list, dict_of_attributes: dict, default=arg_not_passed
):
    idx = get_idx_of_unique_object_with_multiple_attr_in_list(
        some_list=some_list,
        dict_of_attributes=dict_of_attributes,
        default=index_not_found,
    )
    if idx is index_not_found:
        if default is arg_not_passed:
            raise MissingData(
                "One or more of attributes not found %s" % str(dict_of_attributes)
            )
        else:
            return default

    return some_list[idx]


def get_idx_of_unique_object_with_multiple_attr_in_list(
    some_list: list, dict_of_attributes: dict, default=arg_not_passed
):
    list_of_idx = get_idx_of_multiple_object_with_multiple_attr_in_list(
        some_list=some_list, dict_of_attributes=dict_of_attributes
    )
    if len(list_of_idx) == 0:
        if default is arg_not_passed:
            raise MissingData(
                "One or more of attributes not found %s" % str(dict_of_attributes)
            )
        else:
            return default

    elif len(list_of_idx) > 1:
        raise MultipleMatches("Multiple matches for %s" % str(dict_of_attributes))
    else:
        return list_of_idx[0]


def get_subset_of_list_that_matches_multiple_attr(
    some_list: list, dict_of_attributes: dict
):
    list_of_idx = get_idx_of_multiple_object_with_multiple_attr_in_list(
        some_list=some_list, dict_of_attributes=dict_of_attributes
    )
    return [some_list[idx] for idx in list_of_idx]


def get_idx_of_multiple_object_with_multiple_attr_in_list(
    some_list: list, dict_of_attributes: dict
) -> List[int]:
    list_of_idx = [
        idx
        for idx, object_in_list in enumerate(some_list)
        if matches_attributes(object_in_list, dict_of_attributes=dict_of_attributes)
    ]

    return list_of_idx


def matches_attributes(object_in_list, dict_of_attributes: dict) -> bool:
    for attr_name, attr_value in dict_of_attributes.items():
        attr_in_object = getattr(object_in_list, attr_name)
        if attr_in_object != attr_value:
            return False

    return True


index_not_found = object()


def create_list_of_objects_from_dataframe(
    class_of_object: GenericSkipperManObject, df: pd.DataFrame
):
    list_of_objects = [
        create_object_from_df_row(class_of_object=class_of_object, row=row)
        for index, row in df.iterrows()
    ]

    return list_of_objects


def create_data_frame_given_list_of_objects(
    list_of_objects: List[GenericSkipperManObject],
) -> pd.DataFrame:
    list_of_dicts = [item.as_str_dict() for item in list_of_objects]

    return pd.DataFrame(list_of_dicts)


def create_object_from_df_row(class_of_object: GenericSkipperManObject, row: pd.Series):
    row_as_dict = row.to_dict()

    try:
        object = class_of_object.from_dict_of_str(row_as_dict)
    except Exception as exception:
        raise Exception(
            _error_str_when_creating_object_from_df_row(
                class_of_object=class_of_object,
                row_as_dict=dict(row_as_dict),
                exception=exception,
            )
        )

    return object


def _error_str_when_creating_object_from_df_row(
    class_of_object, row_as_dict: dict, exception: Exception
):
    if getattr(class_of_object, "from_dict_of_str", None) is None:
        return Exception(
            "Class %s requires .from_dict_of_str() method" % (str(class_of_object))
        )
    list_of_attributes = get_list_of_attributes(some_class=class_of_object)
    return Exception(
        "Class %s requires elements %s element %s doesn't match exception %s"
        % (
            str(class_of_object),
            str(list_of_attributes),
            str(row_as_dict),
            str(exception),
        )
    )
