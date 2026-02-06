from typing import Dict, List

from app.objects.qualifications import Qualification
from app.objects.substages import (
    TickSubStage,
    ListOfTickSheetItems,
)


class TickSubStagesAsDict(Dict[TickSubStage, ListOfTickSheetItems]):
    def substage_names(self):
        list_of_substages = list(self.keys())
        return [substage.name for substage in list_of_substages]

    @property
    def list_of_tick_sheet_items_for_this_qualification(self) -> ListOfTickSheetItems:
        list_of_items = []
        for list_of_tick_sheet_items_for_substage in self.values():
            list_of_items += list_of_tick_sheet_items_for_substage

        return ListOfTickSheetItems(list_of_items)

    @property
    def list_of_substage_names_aligned_to_tick_sheet_items(self) -> List[str]:
        all_substage_names = []
        for tick_substage, dict_of_tick_sheet_items in self.items():
            all_substage_names += [tick_substage.name] * len(dict_of_tick_sheet_items)

        return all_substage_names


class QualificationsAndTickItemsAsDict(Dict[Qualification, TickSubStagesAsDict]):

    def list_of_substage_names(self):
        list_of_substage_names = []
        for tick_substages_dict in self.values():
            substage_names = tick_substages_dict.substage_names()
            list_of_substage_names += substage_names

        return list(set(list_of_substage_names))

