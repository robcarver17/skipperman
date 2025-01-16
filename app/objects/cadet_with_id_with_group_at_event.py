from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.groups import unallocated_group_id


@dataclass
class CadetIdWithGroup(GenericSkipperManObjectWithIds):
    cadet_id: str
    group_id: str
    day: Day


class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup


    def remove_group_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        self.update_group_for_cadet_on_day(
            cadet_id=cadet_id, day=day,
            chosen_group_id=unallocated_group_id
        )

    def update_group_for_cadet_on_day(
        self, cadet_id: str, day: Day,  chosen_group_id: str
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
        idx = self.index(item_with_cadet_id_and_day)
        if item_with_cadet_id_and_day.group_id == chosen_group_id:
            pass
        if chosen_group_id == unallocated_group_id:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            self[idx] = CadetIdWithGroup(cadet_id=cadet_id, group_id=chosen_group_id, day=day)

    def _update_group_for_new_cadet(self, cadet_id: str,  day: Day,  chosen_group_id: str):
        if chosen_group_id == unallocated_group_id:
            return ## we don't store unallocated

        self.append(
            CadetIdWithGroup(cadet_id=cadet_id, group_id=chosen_group_id, day=day)
        )


    def cadet_is_allocated_to_group_on_day(self, cadet_id: str, day: Day) -> bool:
        item = self.item_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        return not item is missing_data

    def item_with_cadet_id_on_day(self, cadet_id: str, day: Day) -> CadetIdWithGroup:
        items = [item for item in self if item.cadet_id == cadet_id and item.day == day]
        if len(items) == 0:
            return missing_data
        elif len(items) > 1:
            raise Exception("dupilicate groups")
        else:
            return items[0]

    @property
    def list_of_ids(self) -> list:
        return [item.cadet_id for item in self]



CADET_NAME = "cadet"
GROUP_STR_NAME = "group"
