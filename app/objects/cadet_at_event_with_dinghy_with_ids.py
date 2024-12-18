from dataclasses import dataclass
from typing import List

from app.objects.boat_classes import ListOfBoatClasses
from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.utils import make_id_as_int_str

NO_PARTNER_REQUIRED = "Singlehander"
NOT_ALLOCATED = "Unallocated"
NO_PARTNERSHIP_LIST = [NOT_ALLOCATED, NO_PARTNER_REQUIRED]


def no_partnership_given_partner_id_or_str(partnership_str: str):
    return partnership_str in NO_PARTNERSHIP_LIST


def valid_partnership_given_partner_id_or_str(partnership_str: str):
    return not no_partnership_given_partner_id_or_str(partnership_str)


@dataclass
class CadetAtEventWithBoatClassAndPartnerWithIds(GenericSkipperManObject):
    cadet_id: str
    boat_class_id: str
    sail_number: str
    day: Day
    partner_cadet_id: str = NO_PARTNER_REQUIRED

    def has_partner(self):
        return valid_partnership_given_partner_id_or_str(self.partner_cadet_id)

    def __eq__(self, other):
        sail_number = make_id_as_int_str(self.sail_number)
        other_sail_number = make_id_as_int_str(other.sail_number)

        return (
            self.cadet_id == other.cadet_id
            and self.boat_class_id == other.boat_class_id
            and sail_number == other_sail_number
            and self.partner_cadet_id == other.partner_cadet_id
        )

    def clear_partner(self):
        self.partner_cadet_id = NOT_ALLOCATED


UNCHANGED = "unchanged"
WAS_INVALID_NOW_INVALID_CHANGED = "invalid_changed"
WAS_INVALID_NOW_VALID = "was_invalid_now_valid"
WAS_VALID_NOW_INVALID = "was_valid_now_invalid"
WAS_VALID_NOW_VALID_CHANGED = "valid_changed"


class ListOfCadetAtEventWithBoatClassAndPartnerWithIds(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithBoatClassAndPartnerWithIds


    def update_boat_info_for_cadet_and_partner_at_event_on_day(
        self, cadet_at_event_with_dinghy: CadetAtEventWithBoatClassAndPartnerWithIds
    ):
        cadet_id = cadet_at_event_with_dinghy.cadet_id
        self.update_boat_for_cadet_on_day(
            cadet_id=cadet_id,
            sail_number=cadet_at_event_with_dinghy.sail_number,
            boat_class_id=cadet_at_event_with_dinghy.boat_class_id,
            day=cadet_at_event_with_dinghy.day,
        )
        self.modify_two_handed_partnership(
            cadet_id=cadet_id,
            day=cadet_at_event_with_dinghy.day,
            new_two_handed_partner_id=cadet_at_event_with_dinghy.partner_cadet_id,
        )

    def modify_two_handed_partnership(
        self, cadet_id: str, new_two_handed_partner_id: str, day: Day
    ):
        how_changed = self.how_has_partnership_id_changed(
            cadet_id=cadet_id,
            new_two_handed_partner_id=new_two_handed_partner_id,
            day=day,
        )
        if how_changed == UNCHANGED:
            pass
        elif how_changed == WAS_INVALID_NOW_INVALID_CHANGED:
            ## change only this cadet, change of state from singlehanded to not allocated or reverse
            self.add_two_handed_partner_to_existing_cadet(
                cadet_id=cadet_id, partner_id=new_two_handed_partner_id, day=day
            )
        elif how_changed == WAS_VALID_NOW_VALID_CHANGED:
            self.remove_two_handed_partner_from_existing_partner_of_cadet(
                cadet_id=cadet_id, day=day
            )
            self.create_two_handed_partnership(
                cadet_id=cadet_id,
                new_two_handed_partner_id=new_two_handed_partner_id,
                day=day,
            )
        elif how_changed == WAS_VALID_NOW_INVALID:
            self.remove_two_handed_partner_from_existing_partner_of_cadet(
                cadet_id=cadet_id, day=day
            )
            self.remove_two_handed_partner_from_existing_cadet(
                cadet_id=cadet_id, day=day
            )
        elif how_changed == WAS_INVALID_NOW_VALID:
            self.create_two_handed_partnership(
                cadet_id=cadet_id,
                new_two_handed_partner_id=new_two_handed_partner_id,
                day=day,
            )
        else:
            raise Exception("Shouldn't get here!")

    def create_two_handed_partnership(
        self, cadet_id: str, new_two_handed_partner_id: str, day: Day
    ):
        self.add_two_handed_partner_to_existing_cadet(
            cadet_id=cadet_id, partner_id=new_two_handed_partner_id, day=day
        )

        ## second cadet might not exist, this ensures they do
        first_cadet = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        self.update_boat_for_cadet_on_day(
            cadet_id=first_cadet.partner_cadet_id,
            sail_number=first_cadet.sail_number,
            boat_class_id=first_cadet.boat_class_id,
            day=day,
        )
        self.add_two_handed_partner_to_existing_cadet(
            cadet_id=new_two_handed_partner_id, partner_id=cadet_id, day=day
        )

    def add_two_handed_partner_to_existing_cadet(self, cadet_id, partner_id, day: Day):
        cadet_in_data = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        cadet_in_data.partner_cadet_id = partner_id

    def remove_two_handed_partner_from_existing_partner_of_cadet(
        self, cadet_id, day: Day
    ):
        cadet_in_data = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        partner_id = cadet_in_data.partner_cadet_id
        self.clear_boat_details_from_existing_cadet_id(partner_id, day=day)

    def clear_boat_details_from_existing_cadet_id(self, cadet_id: str, day: Day):
        idx = self.idx_of_item_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if idx is missing_data:
            return
        self.pop(idx)

    def remove_two_handed_partner_from_existing_cadet(self, cadet_id, day: Day):
        cadet_in_data = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        cadet_in_data.clear_partner()

    def how_has_partnership_id_changed(
        self, cadet_id: str, new_two_handed_partner_id: str, day: Day
    ) -> str:
        ## Changes only apply to the first cadet
        original_cadet = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        original_partner_id = original_cadet.partner_cadet_id

        if original_partner_id == new_two_handed_partner_id:
            return UNCHANGED

        was_valid = valid_partnership_given_partner_id_or_str(original_partner_id)
        now_valid = valid_partnership_given_partner_id_or_str(new_two_handed_partner_id)

        if was_valid and now_valid:
            return WAS_VALID_NOW_VALID_CHANGED
        elif was_valid and not now_valid:
            return WAS_VALID_NOW_INVALID
        elif not was_valid and now_valid:
            return WAS_INVALID_NOW_VALID
        elif not was_valid and not now_valid:
            return WAS_INVALID_NOW_INVALID_CHANGED
        else:
            raise Exception("Shouldn't get here")

    def update_boat_for_cadet_on_day(
        self, cadet_id: str, boat_class_id: str, sail_number: str, day: Day
    ):
        object_with_id = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if object_with_id is missing_data:
            self.add_boat_for_no_existing_cadet(
                cadet_id=cadet_id,
                boat_class_id=boat_class_id,
                sail_number=sail_number,
                day=day,
            )
        else:
            object_with_id.boat_class_id = boat_class_id
            object_with_id.sail_number = sail_number

    def add_boat_for_no_existing_cadet(
        self, cadet_id: str, boat_class_id: str, sail_number: str, day: Day
    ):
        self.append(
            CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=cadet_id,
                boat_class_id=boat_class_id,
                sail_number=sail_number,
                day=day,
            )
        )

    def idx_of_item_with_cadet_id_on_day(self, cadet_id: str, day: Day):
        item = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item is missing_data:
            return missing_data

        return self.index(item)

    def cadet_partner_id_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=missing_data
    ) -> str:
        item = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item is missing_data:
            return default

        return item.partner_cadet_id

    def sail_number_for_cadet_id(
        self, cadet_id: str, day: Day, default=missing_data
    ) -> str:
        item = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item is missing_data:
            return default

        return item.sail_number

    def dinghy_id_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=missing_data
    ) -> str:
        item = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item is missing_data:
            return default

        return item.boat_class_id

    def object_with_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=missing_data
    ) -> CadetAtEventWithBoatClassAndPartnerWithIds:
        list_of_items = [
            item for item in self if item.cadet_id == cadet_id and item.day == day
        ]
        if len(list_of_items) == 0:
            return default
        if len(list_of_items) > 1:
            raise Exception("Can only have one dinghy per cadet per day")

        return list_of_items[0]

    def unique_list_of_cadet_ids(self):
        ## unique
        return list(set([item.cadet_id for item in self]))

    def list_of_boat_class_ids(self):
        ## not unique
        return [item.boat_class_id for item in self]

    def list_of_partner_ids_excluding_not_valid(self) -> List[str]:
        return [
            object.partner_cadet_id
            for object in self
            if valid_partnership_given_partner_id_or_str(object.partner_cadet_id)
        ]

    def unique_sorted_list_of_boat_class_ids(
        self, all_boat_classes: ListOfBoatClasses
    ) -> List[str]:
        return [
            object.id
            for object in all_boat_classes
            if object.id in self.list_of_boat_class_ids()
        ]


