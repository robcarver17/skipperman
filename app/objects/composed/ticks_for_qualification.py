from typing import Dict, List

from app.objects.composed.ticks_in_dicts import TickSubStagesAsDict
from app.objects.utilities.exceptions import missing_data
from app.objects.qualifications import Qualification
from app.objects.ticks import (
    DictOfTicksWithItem,
    ListOfTickListItemsAndTicksForSpecificCadet,
    Tick,
    full_tick,
    half_tick,
    tick_as_str,
)
from app.objects.substages import TickSubStage, TickSheetItem, ListOfTickSheetItems


class DictOfCadetIdsWithTickListItemsForCadetId(
    Dict[str, ListOfTickListItemsAndTicksForSpecificCadet]
):
    def get_dict_of_ticks_with_items_for_cadet_id_adding_if_required(
        self, cadet_id: str
    ) -> DictOfTicksWithItem:
        list_of_ticks_for_cadet = self.list_of_ticks_for_cadet_id_adding_if_required(
            cadet_id
        )
        return list_of_ticks_for_cadet.dict_of_ticks_with_items()

    def update_tick(self, cadet_id: str, new_tick: Tick, tick_item: TickSheetItem):
        list_of_ticks_for_cadet = self.list_of_ticks_for_cadet_id_adding_if_required(
            cadet_id
        )
        list_of_ticks_for_cadet.update_tick(new_tick=new_tick, tick_item=tick_item)

    def list_of_ticks_for_cadet_id_adding_if_required(
        self, cadet_id: str
    ) -> ListOfTickListItemsAndTicksForSpecificCadet:
        list_of_ticks = self.get(cadet_id, missing_data)
        if list_of_ticks is missing_data:
            list_of_ticks = ListOfTickListItemsAndTicksForSpecificCadet([])
            self[cadet_id] = list_of_ticks

        return list_of_ticks


class DictOfTickSheetItemsAndTicksForCadet(Dict[TickSheetItem, Tick]):
    def percentage_complete(self) -> float:
        full_ticks = [1.0 for tick in self.list_of_ticks if tick == full_tick]
        half_ticks = [0.5 for tick in self.list_of_ticks if tick == half_tick]

        total_Ticks = float(len(self.list_of_ticks))
        if total_Ticks ==0:
            return 0.0

        return 100.0 * (sum(full_ticks) + sum(half_ticks)) / total_Ticks

    @classmethod
    def from_dict_of_ticks_and_qualifications(
        cls,
        list_of_tick_sheet_items: ListOfTickSheetItems,
        dict_of_ticks_with_items: DictOfTicksWithItem,
        already_qualified: bool,
    ):
        raw_dict = {}
        for tick_sheet_item in list_of_tick_sheet_items:
            if already_qualified:
                raw_dict[tick_sheet_item] = full_tick
            else:
                raw_dict[tick_sheet_item] = dict_of_ticks_with_items.get_tick_with_id(
                    tick_sheet_item.id
                )

        return cls(raw_dict)

    @property
    def list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        return ListOfTickSheetItems(list(self.keys()))

    @property
    def list_of_ticks(self) -> List[Tick]:
        return list(self.values())

    def update_tick(self, new_tick: Tick, tick_item: TickSheetItem):
        self[tick_item] = new_tick

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

    @classmethod
    def from_dict_of_ticks_and_qualifications(
        cls,
        tick_substages_as_dict: TickSubStagesAsDict,
        dict_of_ticks_with_items: DictOfTicksWithItem,
        qualification: Qualification,
        already_qualified: bool = False,
    ):
        raw_dict = {}
        for tick_sub_stage, list_of_tick_sheet_items in tick_substages_as_dict.items():
            raw_dict[tick_sub_stage] = (
                DictOfTickSheetItemsAndTicksForCadet.from_dict_of_ticks_and_qualifications(
                    dict_of_ticks_with_items=dict_of_ticks_with_items,
                    list_of_tick_sheet_items=list_of_tick_sheet_items,
                    already_qualified=already_qualified,
                )
            )

        return cls(
            raw_dict,
            already_qualified=already_qualified,
            qualification=qualification,
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

    def update_tick(self, new_tick: Tick, tick_item: TickSheetItem):
        substage_for_tick = self.substage_for_tick(tick_item)
        ticks_for_substage = self[substage_for_tick]
        ticks_for_substage.update_tick(tick_item=tick_item, new_tick=new_tick)

    def substage_for_tick(self, tick_item: TickSheetItem) -> TickSubStage:
        matching_substages = [
            substage
            for substage in self.substages
            if substage.id == tick_item.substage_id
        ]
        try:
            assert len(matching_substages) == 1
        except:
            raise Exception("Zero or more than one matching substages")

        return matching_substages[0]

    @property
    def substages(self):
        return list(self.keys())

    @property
    def already_qualified(self) -> bool:
        return self._already_qualified

    @property
    def qualification(self) -> Qualification:
        return self._qualification
