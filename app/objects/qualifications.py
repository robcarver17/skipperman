import datetime
from dataclasses import dataclass
from typing import List

from app.objects.utilities.generic_list_of_objects import (
    get_idx_of_unique_object_with_attr_in_list,
    get_unique_object_with_attr_in_list,
    get_unique_object_with_multiple_attr_in_list,
    get_idx_of_multiple_object_with_multiple_attr_in_list,
)

from app.objects.utilities.exceptions import (
    arg_not_passed,
    missing_data,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObject,
    GenericSkipperManObjectWithIds,
)


@dataclass
class Qualification(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ListOfQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Qualification

    def qualification_given_id(self, qualification_id: str, default=arg_not_passed):
        return self.object_with_id(qualification_id, default=default)

    def qualification_given_name(self, name: str, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=name, default=default
        )


@dataclass
class CadetWithIdAndQualification(GenericSkipperManObject):
    cadet_id: str
    qualification_id: str
    date: datetime.date
    awarded_by: str


class ListOfCadetsWithIdsAndQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetWithIdAndQualification

    def sort_by_date(self):
        return ListOfCadetsWithIdsAndQualifications(
            sorted(self, key=lambda object: object.date, reverse=True)
        )

    def cadet_has_qualification(self, cadet_id:str, qualification_id: str):
        existing_item = get_unique_object_with_multiple_attr_in_list(
            self, dict_of_attributes=dict(cadet_id=cadet_id, qualification_id=qualification_id),
            default=missing_data
        )

        if existing_item is missing_data:
            return False

        return True

class NoQualifications:
    def name(self):
        return "No qualification"


no_qualifications = NoQualifications()
