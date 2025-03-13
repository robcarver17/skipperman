from dataclasses import dataclass

from app.objects.exceptions import arg_not_passed, missing_data
from app.objects.utils import in_x_not_in_y, in_both_x_and_y
from app.objects.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
)
from app.objects.generic_objects import GenericSkipperManObject

SKIPPERMAN_FIELD_COLUMN_VALUE = "skipperman_field"
WA_FIELD_COLUMN_KEY = "wa_field"


@dataclass
class WAFieldMap(GenericSkipperManObject):
    skipperman_field: str
    wa_field: str


class ListOfWAFieldMappings(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return WAFieldMap

    def delete_mapping(self, skipperman_field: str):
        mapping_pair = self.mapping_pair_for_skipperman_field(
            skipperman_field=skipperman_field, default=missing_data
        )
        if mapping_pair is missing_data:
            raise Exception("Can't delete %s as not in mapping list" % skipperman_field)
        print("delting %s" % mapping_pair)
        self.remove(mapping_pair)

    def mapping_pair_for_skipperman_field(
        self, skipperman_field: str, default=arg_not_passed
    ) -> WAFieldMap:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="skipperman_field",
            attr_value=skipperman_field,
            default=default,
        )

    def add_new_mapping(self, skipperman_field: str, wa_field: str):
        if skipperman_field in self.list_of_skipperman_fields:
            raise Exception("Skipperman field %s already exists" % skipperman_field)
        if wa_field in self.list_of_wa_fields:
            raise Exception("WA field %s already exists" % wa_field)

        self.append(WAFieldMap(skipperman_field=skipperman_field, wa_field=wa_field))

    def sort_by_skipperman_field(self):
        self.sort(key=lambda item: item.skipperman_field)

    def matching_wa_fields(self, list_of_wa_fields: list):
        return in_both_x_and_y(list_of_wa_fields, self.list_of_wa_fields)

    def wa_fields_missing_from_list(self, list_of_wa_fields: list):
        return in_x_not_in_y(x=self.list_of_wa_fields, y=list_of_wa_fields)

    def wa_fields_missing_from_mapping(self, list_of_wa_fields: list):
        return in_x_not_in_y(x=list_of_wa_fields, y=self.list_of_wa_fields)

    def skipperman_field_given_wa_field(self, wa_field: str):
        list_of_wa_fields = self.list_of_wa_fields
        list_of_skipperman_fields = self.list_of_skipperman_fields

        return list_of_skipperman_fields[list_of_wa_fields.index(wa_field)]

    @property
    def list_of_wa_fields(self):
        return [wa_field_map.wa_field for wa_field_map in self]

    @property
    def list_of_skipperman_fields(self):
        return [wa_field_map.skipperman_field for wa_field_map in self]
