from typing import Dict, List

from app.objects.qualifications import Qualification
from app.objects.ticks import (
    Tick,
    full_tick,
    half_tick,
    tick_as_str,
)
from app.objects.substages import TickSubStage, TickSheetItem, ListOfTickSheetItems


class DictOfTickSheetItemsAndTicksForCadet(Dict[TickSheetItem, Tick]):
    def percentage_complete(self) -> float:
        full_ticks = [1.0 for tick in self.list_of_ticks if tick == full_tick]
        half_ticks = [0.5 for tick in self.list_of_ticks if tick == half_tick]

        total_Ticks = float(len(self.list_of_ticks))
        if total_Ticks == 0:
            return 0.0

        return 100.0 * (sum(full_ticks) + sum(half_ticks)) / total_Ticks


    @property
    def list_of_ticks(self) -> List[Tick]:
        return list(self.values())

    @property
    def list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        return ListOfTickSheetItems(list(self.keys()))

    def as_dict_of_str(self):
        return dict(
            [tick_item.name, tick_as_str(tick)] for tick_item, tick in self.items()
        )


class TicksForQualification(Dict[TickSubStage, DictOfTickSheetItemsAndTicksForCadet]):
    def __init__(
        self,
        raw_dict: Dict[TickSubStage, DictOfTickSheetItemsAndTicksForCadet],
        qualification: Qualification,
        already_qualified: bool = False,
    ):
        super().__init__(raw_dict)
        self._already_qualified = already_qualified
        self._qualification = qualification

    @property
    def dict_of_substages_and_ticksheet_items(self) -> Dict[TickSubStage, ListOfTickSheetItems]:
        return dict(
            [
                (substage, ticks_for_cadets.list_of_tick_sheet_items)
                for substage, ticks_for_cadets in self.items()
            ]
        )

    def current_tick(self, tick_item: TickSheetItem) -> Tick:
        return self.all_tick_sheet_items_and_ticks()[tick_item]

    def percentage_qualified(self):
        if self.already_qualified:
            return 100.0

        all_ticks_and_items = self.all_tick_sheet_items_and_ticks()
        return all_ticks_and_items.percentage_complete()

    def all_tick_sheet_items_and_ticks(self) -> DictOfTickSheetItemsAndTicksForCadet:
        starting_dict = {}
        for dict_of_items_and_ticks in self.values():
            starting_dict.update(dict_of_items_and_ticks)

        return DictOfTickSheetItemsAndTicksForCadet(starting_dict)


    @property
    def substages(self):
        return list(self.keys())

    @property
    def already_qualified(self) -> bool:
        return self._already_qualified

    @property
    def qualification(self) -> Qualification:
        return self._qualification
