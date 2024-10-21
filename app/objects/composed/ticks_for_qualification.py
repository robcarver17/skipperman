from typing import Dict, List

from app.objects.cadets import Cadet
from app.objects.composed.ticks_in_dicts import TickSubStagesAsDict
from app.objects.qualifications import Qualification
from app.objects.ticks import DictOfTicksWithItem, ListOfCadetIdsWithTickListItemIds, Tick, full_tick, \
    half_tick, tick_as_str
from app.objects.substages import TickSubStage, TickSheetItem, ListOfTickSheetItems


class DictOfCadetIdAndTicksWithItems(Dict[str, DictOfTicksWithItem]):
    def __init__(self, raw_dict, dict_of_cadet_ids_with_tick_list_items_for_cadet_id: Dict[str, ListOfCadetIdsWithTickListItemIds]):
        super().__init__(raw_dict)
        self._dict_of_cadet_ids_with_tick_list_items_for_cadet_id = dict_of_cadet_ids_with_tick_list_items_for_cadet_id

    @property
    def dict_of_cadet_ids_with_tick_list_items_for_cadet_id(self) -> Dict[str, ListOfCadetIdsWithTickListItemIds]:
        return self._dict_of_cadet_ids_with_tick_list_items_for_cadet_id

    def update_tick(self, cadet: Cadet, new_tick: Tick,  tick_item: TickSheetItem):
        ## have to modify underlying data so stored properly, don't actually have to modify this object as only intermediate
        tick_list_items_for_cadet = self.dict_of_cadet_ids_with_tick_list_items_for_cadet_id[cadet.id]
        tick_list_items_for_cadet.update_tick(cadet=cadet, new_tick=new_tick, tick_item=tick_item)

    def get_for_cadet_id(self, cadet_id: str) -> DictOfTicksWithItem:
        return self.get(cadet_id, DictOfTicksWithItem())


def compose_dict_of_tick_list_items_with_cadet_id_as_key(dict_of_cadet_ids_with_tick_list_items_for_cadet_id,
                                                            list_of_cadet_ids: list) -> DictOfCadetIdAndTicksWithItems:


    raw_dict = {}
    for cadet_id in list_of_cadet_ids:
        list_of_cadet_ids_with_tick_list_items_for_cadet_id = dict_of_cadet_ids_with_tick_list_items_for_cadet_id[cadet_id]
        for cadet_with_tick_list_items in list_of_cadet_ids_with_tick_list_items_for_cadet_id:
            raw_dict[str(cadet_with_tick_list_items.cadet_id)] = cadet_with_tick_list_items.dict_of_ticks_with_items

    return DictOfCadetIdAndTicksWithItems(raw_dict=raw_dict,
                                          dict_of_cadet_ids_with_tick_list_items_for_cadet_id=dict_of_cadet_ids_with_tick_list_items_for_cadet_id)


class DictOfTickSheetItemsAndTicksForCadet(Dict[TickSheetItem, Tick]):
    def percentage_complete(self) -> float:
        full_ticks = [1.0 for tick in self.list_of_ticks if tick == full_tick]
        half_ticks = [0.5 for tick in self.list_of_ticks if tick == half_tick]

        total_Ticks = float(len(self.list_of_ticks))

        return 100.0*(sum(full_ticks) + sum(half_ticks)) / total_Ticks


    @classmethod
    def from_dict_of_ticks_and_qualifications(cls, list_of_tick_sheet_items: ListOfTickSheetItems,
                                              dict_of_ticks_with_items: DictOfTicksWithItem,
                                              already_qualified: bool
                                              ):

        raw_dict = {}
        for tick_sheet_item in list_of_tick_sheet_items:
            if already_qualified:
                raw_dict[tick_sheet_item] = full_tick
            else:
                raw_dict[tick_sheet_item] = dict_of_ticks_with_items.get_tick_with_id(tick_sheet_item.id)

        return cls(raw_dict)

    @property
    def list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        return ListOfTickSheetItems(list(self.keys()))

    @property
    def list_of_ticks(self) -> List[Tick]:
        return list(self.values())

    def update_tick(self, new_tick: Tick,  tick_item: TickSheetItem):
        self[tick_item] = new_tick

    def as_dict_of_str(self):
        return dict([tick_item.name, tick_as_str(tick)] for tick_item, tick in self.items())


class TicksForQualification(Dict[TickSubStage, DictOfTickSheetItemsAndTicksForCadet]):
    def __init__(self, raw_dict: Dict[TickSubStage, DictOfTickSheetItemsAndTicksForCadet],
                 qualification: Qualification,
                 already_qualified: bool = False):
        super().__init__(raw_dict)
        self._already_qualified = already_qualified
        self._qualification = qualification

    @classmethod
    def from_dict_of_ticks_and_qualifications(cls, tick_substages_as_dict: TickSubStagesAsDict,
                                              dict_of_ticks_with_items: DictOfTicksWithItem,
                                              qualification: Qualification,
                                              already_qualified: bool = False
                                              ):
        raw_dict = {}
        for tick_sub_stage, list_of_tick_sheet_items in tick_substages_as_dict.items():
            raw_dict[tick_sub_stage] = DictOfTickSheetItemsAndTicksForCadet.from_dict_of_ticks_and_qualifications(
                dict_of_ticks_with_items=dict_of_ticks_with_items,
                list_of_tick_sheet_items=list_of_tick_sheet_items,
                already_qualified=already_qualified
            )

        return cls(raw_dict, already_qualified=already_qualified, qualification=qualification,
)


    def current_tick(self, tick_item: TickSheetItem) -> Tick:
        return self.all_tick_sheet_items_and_ticks()[tick_item]

    def percentage_qualified(self):
        if self.already_qualified:
            return 100.0

        all_ticks_and_items = self.all_tick_sheet_items_and_ticks()
        return all_ticks_and_items.percentage_complete()

    def all_tick_sheet_items_and_ticks(self) ->DictOfTickSheetItemsAndTicksForCadet:
        starting_dict ={}
        for dict_of_items_and_ticks in self.values():
            starting_dict.update(dict_of_items_and_ticks)

        return DictOfTickSheetItemsAndTicksForCadet(starting_dict)

    def update_tick(self, new_tick: Tick,  tick_item: TickSheetItem):
        substage_for_tick = self.substage_for_tick(tick_item)
        ticks_for_substage = self[substage_for_tick]
        ticks_for_substage.update_tick(tick_item=tick_item, new_tick=new_tick)

    def substage_for_tick(self, tick_item: TickSheetItem) -> TickSubStage:
        matching_substages = [substage for substage in self.substages if substage.id ==tick_item.substage_id]
        try:
            assert len(matching_substages)==1
        except:
            raise Exception("Zero or more than one matching substages")

        return matching_substages[0]

    @property
    def substages(self):
        return list(self.keys())

    @property
    def already_qualified(self)-> bool:
        return self._already_qualified

    @property
    def qualification(self) -> Qualification:
        return self._qualification
