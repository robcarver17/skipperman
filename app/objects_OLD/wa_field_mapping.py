from dataclasses import dataclass

from app.objects_OLD.utils import in_x_not_in_y, in_both_x_and_y
from app.objects_OLD.generic_list_of_objects import GenericListOfObjects
from app.objects_OLD.generic_objects import GenericSkipperManObject

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
