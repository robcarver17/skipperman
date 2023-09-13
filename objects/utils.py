import pandas as pd


def data_object_as_dict(some_object) -> dict:
    list_of_attributes = get_list_of_attributes(some_object)

    object_as_dict = dict(
        [(key, getattr(some_object, key)) for key in list_of_attributes]
    )

    return object_as_dict


def create_list_of_objects_from_dataframe(class_of_object, passed_df: pd.DataFrame):

    list_of_objects = [
        create_object_from_df_row(class_of_object=class_of_object, row=row)
        for index, row in passed_df.iterrows()
    ]

    return list_of_objects


def create_object_from_df_row(class_of_object, row: pd.Series):
    row_as_dict = row.to_dict()
    try:
        object = class_of_object(**row_as_dict)
    except:
        list_of_attributes = get_list_of_attributes(some_class=class_of_object)
        raise Exception(
            "Class %s requires elements %s, element %s doesn't match"
            % (str(class_of_object), str(list_of_attributes), str(row_as_dict))
        )

    return object


def get_list_of_attributes(some_class) -> list:
    dict_of_attributes = get_dict_of_class_attributes(some_class)
    return list(dict_of_attributes.keys())


def get_dict_of_class_attributes(some_class) -> dict:
    return some_class.__annotations__
