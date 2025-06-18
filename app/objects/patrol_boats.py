from dataclasses import dataclass
from typing import List

from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import (
    arg_not_passed, missing_data,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_unique_object_with_attr_in_list,
get_unique_object_with_multiple_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list, GenericListOfObjects,
get_subset_of_list_that_matches_multiple_attr
)
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds, GenericSkipperManObject

NO_BOAT = "NO_BOAT"
NO_BOAT_ID = str(-9999)


@dataclass
class PatrolBoat(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.hidden == other.hidden

    @property
    def is_empty(self):
        return self.name == NO_BOAT

    @classmethod
    def create_empty(cls):
        return cls(NO_BOAT, hidden=False, id=NO_BOAT_ID)


no_patrol_boat = PatrolBoat.create_empty()


class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return PatrolBoat

    def sort_from_other_list_of_boats(self, other_list_of_boats: "ListOfPatrolBoats"):
        return self.subset_from_list_of_ids_retaining_order(
            other_list_of_boats.list_of_ids
        )

    def replace(self, existing_patrol_boat: PatrolBoat, new_patrol_boat: PatrolBoat):
        object_idx = self.idx_given_name(existing_patrol_boat.name)
        new_patrol_boat.id = existing_patrol_boat.id
        self[object_idx] = new_patrol_boat

    def boat_given_id(self, patrol_boat_id: str, default=arg_not_passed):
        if patrol_boat_id == no_patrol_boat.id:
            return no_patrol_boat

        return self.object_with_id(patrol_boat_id, default=default)

    def boat_given_name(
        self, patrol_boat_name: str, default=arg_not_passed
    ) -> PatrolBoat:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="name",
            attr_value=patrol_boat_name,
            default=default,
        )

    def idx_given_name(self, patrol_boat_name: str, default=arg_not_passed) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="name",
            attr_value=patrol_boat_name,
            default=default,
        )

    def add(self, patrol_boat_name: str):
        try:
            assert patrol_boat_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate patrol boat %s already exists" % patrol_boat_name
            )
        patrol_boat = PatrolBoat(name=patrol_boat_name, hidden=False)
        patrol_boat.id = self.next_id()

        self.append(patrol_boat)

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))


@dataclass
class PatrolBoatLabelAtEvent(GenericSkipperManObject):
    event_id: str
    day: Day
    boat_id: str
    label: str

class ListOfPatrolBoatLabelsAtEvents(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return PatrolBoatLabelAtEvent

    def copy_patrol_boat_labels_across_event(self, event_id:str,
                                                                             days_in_event: List[Day],
                                                                             overwrite: bool = False):

        list_of_boat_ids = self.unique_set_of_boat_ids_at_event(event_id)
        for boat_id in list_of_boat_ids:
            self.copy_patrol_boat_labels_across_event_for_boat(event_id=event_id,
                                                               boat_id=boat_id,
                                                               days_in_event=days_in_event,
                                                               overwrite=overwrite)

    def unique_set_of_boat_ids_at_event(self, event_id) -> List[str]:
        subset = get_subset_of_list_that_matches_multiple_attr(
            self, dict(event_id=event_id)
        )
        boat_ids = [boat_label.boat_id for boat_label in subset]

        return list(set(boat_ids))

    def copy_patrol_boat_labels_across_event_for_boat(self, event_id:str,
                                                      boat_id: str,
                                                                             days_in_event: List[Day],
                                                                             overwrite: bool = False):
        earliest_label = self.earliest_label_for_boat_at_event(
            event_id=event_id,
            days_in_event=days_in_event,
            boat_id=boat_id
        )
        if earliest_label is missing_data:
            return

        for day in days_in_event:
            existing_label = self.get_label(event_id=event_id, boat_id=boat_id, day=day, default='')

            if len(existing_label)>0:
                if not overwrite:
                    continue

            self.add_or_modify(event_id=event_id, day=day, boat_id=boat_id, label=earliest_label)


    def earliest_label_for_boat_at_event(self, event_id: str, boat_id: str, days_in_event: List[Day]):
        for day in days_in_event:
            existing_label = self.get_label(event_id=event_id, boat_id=boat_id, day=day, default='')
            if len(existing_label)==0:
                continue
            else:
                return existing_label

        return missing_data

    def unique_set_of_labels(self) -> List[str]:
        labels = [boat_label.label for boat_label in self]

        return list(set(labels))


    def unique_set_of_labels_at_event_on_day(self, event_id, day: Day) -> List[str]:
        subset = get_subset_of_list_that_matches_multiple_attr(
            self, dict(event_id=event_id, day=day)
        )
        subset_labels = [boat_label.label for boat_label in subset]

        return list(set(subset_labels))

    def add_or_modify(self, event_id, boat_id, day: Day, label: str):
        existing_label = self.get_patrol_boat_label(event_id=event_id, boat_id=boat_id, day=day, default=missing_data)
        if existing_label is missing_data:
            self._add(event_id=event_id, boat_id=boat_id, label=label, day=day)
        else:
            existing_label.label = label

    def _add(self, event_id, boat_id, day: Day, label: str):
        self.append(PatrolBoatLabelAtEvent(event_id=event_id, boat_id=boat_id, label=label, day=day))

    def get_label(self, event_id: str, boat_id: str, day: Day, default="") -> str:
        patrol_boat_label = self.get_patrol_boat_label(event_id=event_id, boat_id=boat_id, day=day, default=missing_data)
        if patrol_boat_label is missing_data:
            return default
        return patrol_boat_label.label

    def get_patrol_boat_label(self, event_id: str, boat_id: str, day: Day, default) -> PatrolBoatLabelAtEvent:
        return get_unique_object_with_multiple_attr_in_list(
            self,
            dict(event_id=event_id, boat_id=boat_id, day=day),
            default=default
        )


RIVER_SAFETY = "River safety"
LAKE_SAFETY = "Lake safety"


def get_location_for_boat(patrol_boat: PatrolBoat) -> str:
    if 'lake' in patrol_boat.name.lower():
        return LAKE_SAFETY
    else:
        return RIVER_SAFETY
