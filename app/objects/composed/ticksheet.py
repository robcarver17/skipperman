from typing import Dict, List

from app.objects.composed.cadets_with_qualifications import (
    DictOfQualificationsForCadets,
    QualificationsForCadet,
)
from app.objects.composed.ticks_for_qualification import (
    DictOfCadetIdAndTicksWithItems,
    TicksForQualification,
)

from app.objects.qualifications import Qualification, ListOfQualifications

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.composed.ticks_in_dicts import QualificationsAndTickItemsAsDict

from app.objects.ticks import Tick, DictOfTicksWithItem
from app.objects.substages import TickSheetItem, ListOfTickSheetItems


## ticksheet
# only for some cadets
# dict of ticks & qualifications


class DictOfCadetsAndTicksWithinQualification(Dict[Cadet, TicksForQualification]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, TicksForQualification],
        qualification: Qualification,
        list_of_tick_sheet_items_for_this_qualification: ListOfTickSheetItems,
        list_of_substage_names_aligned_to_tick_sheet_items: List[str],
    ):
        super().__init__(raw_dict)
        self._qualification = qualification
        self._list_of_tick_sheet_items_for_this_qualification = (
            list_of_tick_sheet_items_for_this_qualification
        )
        self._list_of_substage_names_aligned_to_tick_sheet_items = (
            list_of_substage_names_aligned_to_tick_sheet_items
        )

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def qualification(self) -> Qualification:
        return self._qualification

    @property
    def list_of_substage_names_aligned_to_tick_sheet_items(self) -> List[str]:
        return self._list_of_substage_names_aligned_to_tick_sheet_items

    @property
    def list_of_tick_sheet_items_for_this_qualification(self) -> ListOfTickSheetItems:
        return self._list_of_tick_sheet_items_for_this_qualification

    def subset_for_list_of_cadets(self, list_of_cadets: ListOfCadets):
        return DictOfCadetsAndTicksWithinQualification(
            dict([(cadet, self[cadet]) for cadet in list_of_cadets]),
            qualification=self.qualification,
            list_of_tick_sheet_items_for_this_qualification=self.list_of_tick_sheet_items_for_this_qualification,
            list_of_substage_names_aligned_to_tick_sheet_items=self.list_of_substage_names_aligned_to_tick_sheet_items,
        )


class QualificationsAndTicksForCadet(Dict[Qualification, TicksForQualification]):
    @classmethod
    def from_dict_of_ticks_and_qualifications(
        cls,
        dict_of_ticks_with_items: DictOfTicksWithItem,
        qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict,
        qualifications_for_cadet: QualificationsForCadet,
    ):
        raw_dict = {}
        for (
            qualification,
            tick_substages_as_dict,
        ) in qualifications_and_tick_items_as_dict.items():
            already_qualified = qualifications_for_cadet.is_cadet_qualified(
                qualification
            )
            raw_dict[qualification] = (
                TicksForQualification.from_dict_of_ticks_and_qualifications(
                    tick_substages_as_dict=tick_substages_as_dict,
                    dict_of_ticks_with_items=dict_of_ticks_with_items,
                    already_qualified=already_qualified,
                    qualification=qualification,
                )
            )

        return cls(raw_dict)

    def update_tick(self, new_tick: Tick, tick_item: TickSheetItem):
        qualification = self.qualification_given_tick_item(tick_item)
        ticks_for_qualification = self[qualification]
        ticks_for_qualification.update_tick(tick_item=tick_item, new_tick=new_tick)

    def qualification_given_tick_item(self, tick_item: TickSheetItem):
        return self.list_of_qualifications.object_with_id(tick_item.stage_id)

    @property
    def list_of_qualifications(self):
        return ListOfQualifications(list(self.keys()))


class DictOfCadetsWithQualificationsAndTicks(
    Dict[Cadet, QualificationsAndTicksForCadet]
):
    def __init__(
        self,
        raw_dict: Dict[Cadet, QualificationsAndTicksForCadet],
        qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict,
        dict_of_cadet_id_and_ticks_with_items: DictOfCadetIdAndTicksWithItems,
    ):
        super().__init__(raw_dict)
        self._dict_of_cadet_id_and_ticks_with_items = (
            dict_of_cadet_id_and_ticks_with_items
        )
        self._qualifications_and_tick_items_as_dict = (
            qualifications_and_tick_items_as_dict
        )

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def dict_of_cadet_id_and_ticks_with_items(self) -> DictOfCadetIdAndTicksWithItems:
        return self._dict_of_cadet_id_and_ticks_with_items

    @property
    def qualifications_and_tick_items_as_dict(self) -> QualificationsAndTickItemsAsDict:
        return self._qualifications_and_tick_items_as_dict

    def subset_for_qualification(
        self, qualification: Qualification
    ) -> DictOfCadetsAndTicksWithinQualification:
        return DictOfCadetsAndTicksWithinQualification(
            dict(
                [
                    (cadet, qualifications_and_ticks_for_cadet[qualification])
                    for cadet, qualifications_and_ticks_for_cadet in self.items()
                ]
            ),
            qualification=qualification,
            list_of_substage_names_aligned_to_tick_sheet_items=self.qualifications_and_tick_items_as_dict[
                qualification
            ].list_of_substage_names_aligned_to_tick_sheet_items,
            list_of_tick_sheet_items_for_this_qualification=self.qualifications_and_tick_items_as_dict[
                qualification
            ].list_of_tick_sheet_items_for_this_qualification,
        )

    def update_tick(self, cadet: Cadet, new_tick: Tick, tick_item: TickSheetItem):
        ## have to modify underlying data so stored properly
        self.dict_of_cadet_id_and_ticks_with_items.update_tick(
            cadet=cadet, new_tick=new_tick, tick_item=tick_item
        )
        tick_items_for_cadet = self[cadet]
        tick_items_for_cadet.update_tick(tick_item=tick_item, new_tick=new_tick)


def compose_dict_of_cadets_with_qualifications_and_ticks(
    list_of_cadet_ids: List[str],
    list_of_cadets: ListOfCadets,
    qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict,
    dict_of_cadet_id_and_ticks_with_items: DictOfCadetIdAndTicksWithItems,
    dict_of_qualifications_for_all_cadets: DictOfQualificationsForCadets,
) -> DictOfCadetsWithQualificationsAndTicks:
    raw_dict = {}
    for cadet_id in list_of_cadet_ids:
        cadet = list_of_cadets.cadet_with_id(cadet_id)
        dict_of_ticks_with_items = (
            dict_of_cadet_id_and_ticks_with_items.get_for_cadet_id(cadet_id)
        )
        qualifications_for_cadet = (
            dict_of_qualifications_for_all_cadets.qualifications_for_cadet(cadet)
        )
        qualifications_and_ticks_for_cadet = QualificationsAndTicksForCadet.from_dict_of_ticks_and_qualifications(
            dict_of_ticks_with_items=dict_of_ticks_with_items,
            qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
            qualifications_for_cadet=qualifications_for_cadet,
        )
        raw_dict[cadet] = qualifications_and_ticks_for_cadet

    return DictOfCadetsWithQualificationsAndTicks(
        raw_dict=raw_dict,
        dict_of_cadet_id_and_ticks_with_items=dict_of_cadet_id_and_ticks_with_items,
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
    )
