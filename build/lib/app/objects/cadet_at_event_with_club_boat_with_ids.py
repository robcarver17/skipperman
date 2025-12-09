from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    index_not_found,
    get_unique_object_with_multiple_attr_in_list,
    get_idx_of_unique_object_with_multiple_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.club_dinghies import no_club_dinghy_id


@dataclass
class CadetAtEventWithClubDinghyWithId(GenericSkipperManObject):
    cadet_id: str
    club_dinghy_id: str
    day: Day


class ListOfCadetAtEventWithIdAndClubDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithClubDinghyWithId

    def update_allocation_for_cadet_on_day(
        self, cadet_id: str, day: Day, club_dinghy_id: str
    ):
        if self.has_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day):
            self._update_existing_allocation_for_cadet_on_day(
                cadet_id=cadet_id, day=day, club_dinghy_id=club_dinghy_id
            )
        else:
            self._add_new_allocation_for_cadet_on_day(
                cadet_id=cadet_id, day=day, club_dinghy_id=club_dinghy_id
            )

    def _update_existing_allocation_for_cadet_on_day(
        self, cadet_id: str, day: Day, club_dinghy_id: str
    ):
        item = self.item_for_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if club_dinghy_id == no_club_dinghy_id:
            self.delete_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day)

        item.club_dinghy_id = club_dinghy_id

    def _add_new_allocation_for_cadet_on_day(
        self, cadet_id: str, day: Day, club_dinghy_id: str
    ):
        if club_dinghy_id == no_club_dinghy_id:
            return

        self.append(
            CadetAtEventWithClubDinghyWithId(
                cadet_id=cadet_id, club_dinghy_id=club_dinghy_id, day=day
            )
        )

    def has_allocation_for_cadet_on_day(self, cadet_id: str, day: Day) -> bool:
        idx = self.index_of_item_for_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=index_not_found
        )
        return not (idx is index_not_found)

    def delete_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        ## allowed to fail
        idx = self.index_of_item_for_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=index_not_found
        )
        if idx is index_not_found:
            return

        self.pop(idx)

    def index_of_item_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> int:
        return get_idx_of_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )

    def item_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> CadetAtEventWithClubDinghyWithId:
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )
