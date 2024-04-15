from app.objects.qualifications import ListOfQualifications,ListOfCadetsWithQualifications
from app.objects.ticks import ListOfTickSubStages, ListOfTickSheetItems, ListOfCadetsWithTickListItems

class DataListOfQualifications(object):
    def read(self) -> ListOfQualifications:
        raise NotImplemented

    def write(self, list_of_qualifications: ListOfQualifications):
        raise NotImplemented


class DataListOfCadetsWithQualifications(object):
    def read(self) -> ListOfCadetsWithQualifications:
        raise NotImplemented

    def write(self, list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
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

