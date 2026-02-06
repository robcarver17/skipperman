from typing import Dict, List

from app.objects.composed.ticks_for_qualification import (
    TicksForQualification,
)

from app.objects.qualifications import Qualification

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.substages import ListOfTickSheetItems, TickSheetItem, TickSubStage


class DictOfCadetsAndTicksWithinQualification(Dict[Cadet, TicksForQualification]):
    def __init__(self, raw_dict: Dict[Cadet, TicksForQualification], qualification: Qualification):
        super().__init__(raw_dict)
        self._qualification = qualification

    @property
    def qualification(self) -> Qualification:
        return self._qualification

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    def subset_for_list_of_cadets(self, list_of_cadets: ListOfCadets):
        return DictOfCadetsAndTicksWithinQualification(
            dict([(cadet, self[cadet]) for cadet in list_of_cadets]),
            self.qualification
        )

    @property
    def list_of_tick_sheet_items_for_this_qualification(self) -> ListOfTickSheetItems:
        the_list = []
        for tick_list_items in list(self.dict_of_substage_names_and_ticksheet_items.values()):
            the_list +=tick_list_items

        return ListOfTickSheetItems(the_list)

    @property
    def list_of_substage_names_aligned_to_tick_sheet_items(self) -> List[str]:
        the_list = []
        for substage, tick_list_items in self.dict_of_substage_names_and_ticksheet_items.items():
            the_list +=[substage.name]*len(tick_list_items)

        return the_list

    @property
    def dict_of_substage_names_and_ticksheet_items(self) -> Dict[TickSubStage, ListOfTickSheetItems]:
        vals = [ticks_for_qualification_and_cadet.dict_of_substages_and_ticksheet_items for ticks_for_qualification_and_cadet in self.values()]
        ## should be the same...
        return vals[0]

class QualificationsAndTicksForCadet(Dict[Qualification, TicksForQualification]):
    pass


class DictOfCadetsWithQualificationsAndTicks(
    Dict[Cadet, QualificationsAndTicksForCadet]
):

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))


    def subset_for_qualification(
        self, qualification: Qualification
    ) -> DictOfCadetsAndTicksWithinQualification:
        return DictOfCadetsAndTicksWithinQualification(
            dict(
                [
                    (cadet, qualifications_and_ticks_for_cadet[qualification])
                    for cadet, qualifications_and_ticks_for_cadet in self.items()
                ]

        ), qualification=qualification)


