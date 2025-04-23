from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.exceptions import arg_not_passed
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.groups import unallocated_group_id
from app.objects.generic_list_of_objects import (
    get_unique_object_with_multiple_attr_in_list,
    get_idx_of_unique_object_with_multiple_attr_in_list,
)
from app.objects.generic_list_of_objects import get_idx_of_multiple_object_with_multiple_attr_in_list

@dataclass
class CadetIdWithGroup(GenericSkipperManObjectWithIds):
    cadet_id: str
    group_id: str
    day: Day


class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup

    def delete_cadet_with_id_from_event(self, cadet_id:str):
        while True:
            list_of_idx =get_idx_of_multiple_object_with_multiple_attr_in_list(self, dict_of_attributes={'cadet_id': cadet_id})
            if len(list_of_idx)==0:
                break
            self.pop(list_of_idx[0])

    def remove_group_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        self.update_group_for_cadet_on_day(
            cadet_id=cadet_id, day=day, chosen_group_id=unallocated_group_id
        )

    def update_group_for_cadet_on_day(
        self, cadet_id: str, day: Day, chosen_group_id: str
    ):
        if self.cadet_is_allocated_to_group_on_day(cadet_id=cadet_id, day=day):
            self._update_group_for_existing_cadet_id_on_day(
                cadet_id=cadet_id, chosen_group_id=chosen_group_id, day=day
            )
        else:
            self._update_group_for_new_cadet(
                cadet_id=cadet_id, chosen_group_id=chosen_group_id, day=day
            )

    def _update_group_for_existing_cadet_id_on_day(
        self, cadet_id: str, day: Day, chosen_group_id: str
    ):
        item_with_cadet_id_and_day = self.item_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day
        )
        idx = self.idx_of_item_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item_with_cadet_id_and_day.group_id == chosen_group_id:
            pass
        elif chosen_group_id == unallocated_group_id:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            ## replace
            item_with_cadet_id_and_day.group_id = chosen_group_id

    def _update_group_for_new_cadet(
        self, cadet_id: str, day: Day, chosen_group_id: str
    ):
        if chosen_group_id == unallocated_group_id:
            return  ## we don't store unallocated

        self.append(
            CadetIdWithGroup(cadet_id=cadet_id, group_id=chosen_group_id, day=day)
        )

    def cadet_is_allocated_to_group_on_day(self, cadet_id: str, day: Day) -> bool:
        item = self.item_with_cadet_id_on_day(cadet_id=cadet_id, day=day, default=None)
        return item is not None

    def item_with_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> CadetIdWithGroup:
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )

    def idx_of_item_with_cadet_id_on_day(
        self, cadet_id: str, day: Day, default=arg_not_passed
    ) -> int:
        return get_idx_of_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"cadet_id": cadet_id, "day": day},
            default=default,
        )

    @property
    def list_of_cadet_ids(self) -> list:
        return [item.cadet_id for item in self]
