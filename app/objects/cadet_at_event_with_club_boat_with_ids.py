from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObject


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
        self.delete_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day)
        self.append(
            CadetAtEventWithClubDinghyWithId(
                cadet_id=cadet_id, club_dinghy_id=club_dinghy_id, day=day
            )
        )

    def delete_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        ## allowed to fail
        idx = self.index_of_item_for_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if idx is missing_data:
            return

        self.pop(idx)

    def index_of_item_for_cadet_id_on_day(self, cadet_id: str, day: Day) -> int:
        item = self.item_for_cadet_id_on_day(
            cadet_id=cadet_id, day=day, default=missing_data
        )
        if item is missing_data:
            return missing_data

        return self.index(item)

    def item_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=missing_data
    ) -> CadetAtEventWithClubDinghyWithId:
        list_of_items = [
            item for item in self if item.cadet_id == cadet_id and item.day == day
        ]
        if len(list_of_items) == 0:
            return default
        if len(list_of_items) > 1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

NO_CLUB_BOAT = ""
