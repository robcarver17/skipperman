from dataclasses import dataclass
from typing import List

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
)
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utils import similar
from app.objects.exceptions import arg_not_passed, MissingData


@dataclass
class Volunteer(GenericSkipperManObjectWithIds):
    first_name: str
    surname: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name < other.name

    def replace_everything_except_id(self, updated_volunteer: "Volunteer"):
        self.first_name = updated_volunteer.first_name
        self.surname = updated_volunteer.surname

    @classmethod
    def new(cls, first_name: str, surname: str, id: str = arg_not_passed):
        return cls(
            first_name=first_name.strip(" ").title(),
            surname=surname.strip(" ").title(),
            id=id,
        )

    @property
    def name(self):
        return self.first_name.title() + " " + self.surname.title()

    def similarity_of_names(self, other_volunteer: "Volunteer") -> float:
        return similar(self.name, other_volunteer.name)


class ListOfVolunteers(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Volunteer

    def add(self, volunteer: Volunteer):
        try:
            assert volunteer.name not in self.list_of_names()
        except:
            raise Exception("Can't have duplicate volunteer names")
        volunteer_id = self.next_id()
        volunteer.id = volunteer_id
        self.append(volunteer)

    def update_existing_volunteer(
        self, existing_volunteer: Volunteer, updated_volunteer: Volunteer
    ):
        existing_volunteer = self.volunteer_with_id(existing_volunteer.id)
        existing_volunteer.replace_everything_except_id(
            updated_volunteer=updated_volunteer
        )

    def volunteer_with_matching_name(
        self, volunteer_name: str, default=arg_not_passed
    ) -> Volunteer:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=volunteer_name, default=default
        )

    def similar_volunteers(
        self,
        volunteer: Volunteer,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
    ) -> "ListOfVolunteers":
        similar_names = [
            other_volunteer
            for other_volunteer in self
            if other_volunteer.similarity_of_names(volunteer) > name_threshold
        ]

        return ListOfVolunteers(similar_names)

    def sort_by_surname(self):
        return ListOfVolunteers(sorted(self, key=lambda x: x.surname))

    def sort_by_firstname(self):
        return ListOfVolunteers(sorted(self, key=lambda x: x.first_name))

    def volunteer_with_id(self, id: str) -> Volunteer:
        return self.object_with_id(id)


default_volunteer = Volunteer(first_name=" ", surname=" ")
