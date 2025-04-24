from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import missing_data, arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_multiple_attr_in_list,
    get_unique_object_with_multiple_attr_in_list,
)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObject,
    get_class_instance_from_str_dict,
)
from app.objects.partners import (
    NO_PARTNER_REQUIRED_STR,
    NOT_ALLOCATED_STR,
)
from app.objects.utilities.utils import make_id_as_int_str
from app.objects.boat_classes import NO_BOAT_CLASS_ID


@dataclass
class CadetAtEventWithBoatClassAndPartnerWithIds(GenericSkipperManObject):
    cadet_id: str
    day: Day
    sail_number: str = ""
    partner_cadet_id: str = NO_PARTNER_REQUIRED_STR
    boat_class_id: str = NO_BOAT_CLASS_ID

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
        self.partner_cadet_id = NOT_ALLOCATED_STR

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        class_instance = get_class_instance_from_str_dict(cls, dict_with_str)
        class_instance.sail_number = make_id_as_int_str(class_instance.sail_number)

        return class_instance


class ListOfCadetAtEventWithBoatClassAndPartnerWithIds(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithBoatClassAndPartnerWithIds

    def allocate_partner_for_cadet_on_day(self, cadet_id, partner_id, day: Day):
        object_with_id = self.object_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=missing_data
        )
        if object_with_id is missing_data:
            self.modify_partnership_status_for_new_cadet(
                cadet_id=cadet_id, partner_id=partner_id, day=day
            )
        else:
            object_with_id.partner_cadet_id = partner_id

    def modify_partnership_status_for_new_cadet(self, cadet_id, partner_id, day: Day):
        self.append(
            CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=cadet_id, day=day, partner_cadet_id=partner_id
            )
        )

    def clear_boat_details_from_existing_cadet_id(self, cadet_id: str, day: Day):
        idx = self.idx_of_item_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=missing_data
        )
        if idx is missing_data:
            return

        self.pop(idx)

    def remove_two_handed_partner_from_existing_cadet(self, cadet_id, day: Day):
        cadet_in_data = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        cadet_in_data.clear_partner()

    def update_boat_and_sail_number_for_cadet_on_day(
        self, cadet_id: str, boat_class_id: str, sail_number: str, day: Day
    ):
        object_with_id = self.object_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=missing_data
        )
        if object_with_id is missing_data:
            self.add_boat_class_and_sail_number_with_no_existing_entry(
                cadet_id=cadet_id,
                boat_class_id=boat_class_id,
                sail_number=sail_number,
                day=day,
            )
        else:
            self.modify_boat_class_and_sail_number_for_existing_entry(
                cadet_id=cadet_id,
                day=day,
                boat_class_id=boat_class_id,
                sail_number=sail_number,
            )

    def add_boat_class_and_sail_number_with_no_existing_entry(
        self, cadet_id: str, boat_class_id: str, sail_number: str, day: Day
    ):
        self.append(
            CadetAtEventWithBoatClassAndPartnerWithIds(
                cadet_id=cadet_id,
                boat_class_id=boat_class_id,
                sail_number=sail_number,
                day=day,
                ## partner will be added later
            )
        )

    def modify_boat_class_and_sail_number_for_existing_entry(
        self, cadet_id: str, boat_class_id: str, sail_number: str, day: Day
    ):
        object_with_id = self.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        object_with_id.sail_number = sail_number
        object_with_id.boat_class_id = boat_class_id

    def object_with_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> CadetAtEventWithBoatClassAndPartnerWithIds:
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )

    def idx_of_item_with_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ):
        return get_idx_of_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )
