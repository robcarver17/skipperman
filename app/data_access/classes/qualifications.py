from app.objects.qualifications import (
    ListOfQualifications,
    ListOfCadetsWithIdsAndQualifications,
)
from app.objects.ticks import (
    ListOfTickSubStages,
    ListOfTickSheetItems,
    ListOfCadetsWithTickListItems,
)


class DataListOfQualifications(object):
    def read(self) -> ListOfQualifications:
        raise NotImplemented

    def write(self, list_of_qualifications: ListOfQualifications):
        raise NotImplemented


class DataListOfCadetsWithQualifications(object):
    def read(self) -> ListOfCadetsWithIdsAndQualifications:
        raise NotImplemented

    def write(self, list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications):
        raise NotImplemented


class DataListOfTickSubStages(object):
    def read(self) -> ListOfTickSubStages:
        raise NotImplemented

    def write(self, list_of_tick_sub_stages: ListOfTickSubStages):
        raise NotImplemented


class DataListOfTickSheetItems(object):
    def read(self) -> ListOfTickSheetItems:
        raise NotImplemented

    def write(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        raise NotImplemented


class DataListOfCadetsWithTickListItems(object):
    def read(self) -> ListOfCadetsWithTickListItems:
        raise NotImplemented

    def write(self, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems):
        raise NotImplemented

    def read_for_cadet_id(self, cadet_id: str):
        raise NotImplemented

    def write_for_cadet_id(
        self,
        list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems,
        cadet_id: str,
    ):
        raise NotImplemented
