from dataclasses import dataclass

from app.objects.day_selectors import Day
from app.objects.exceptions import arg_not_passed, MissingData
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds, get_unique_object_with_attr_in_list
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.groups import unallocated_group_id
from build.lib.app.objects.exceptions import MultipleMatches


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
        idx = self.index(item_with_cadet_id_and_day)
        if item_with_cadet_id_and_day.group_id == chosen_group_id:
            pass
        if chosen_group_id == unallocated_group_id:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            ## replace
            self[idx] = CadetIdWithGroup(
                cadet_id=cadet_id, group_id=chosen_group_id, day=day
            )

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

    def item_with_cadet_id_on_day(self, cadet_id: str, day: Day, default=arg_not_passed) -> CadetIdWithGroup:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default
        )

    @property
    def list_of_cadet_ids(self) -> list:
        return [item.cadet_id for item in self]


