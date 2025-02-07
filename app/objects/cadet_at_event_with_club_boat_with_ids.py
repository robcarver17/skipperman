from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data, arg_not_passed, MissingData
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds, get_unique_object_with_attr_in_list, \
    get_idx_of_unique_object_with_attr_in_list
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
        idx = self.index_of_item_for_cadet_id_on_day(cadet_id=cadet_id, day=day, default=None)
        if idx is None:
            return

        self.pop(idx)

    def index_of_item_for_cadet_id_on_day(self, cadet_id: str, day: Day, default=arg_not_passed) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default

        )

    def item_for_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> CadetAtEventWithClubDinghyWithId:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default
        )



NO_CLUB_BOAT = ""
