
from dataclasses import dataclass

from app.objects.day_selectors import Day

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class ClubDinghy(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name


class ListOfClubDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return ClubDinghy

    def name_given_id(self, id: str) -> str:
        names = [item.name for item in self if item.id == id]

        if len(names)==0:
            return missing_data
        elif len(names)>1:
            raise Exception("Found more than one boat with same ID should be impossible")

        return names[0]

    def delete_given_name(self, boat_name: str):
        idx = self.idx_given_name(boat_name)
        if idx is missing_data:
            raise Exception("Can't find boat with name to delete %s" % boat_name)
        self.pop(idx)

    def idx_given_name(self, boat_name: str):
        id = self.id_given_name(boat_name)
        return self.index_of_id(id)

    def id_given_name(self, boat_name: str):
        id = [item.id for item in self if item.name == boat_name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one boat with same name should be impossible")

        return str(id[0])

    def add(self, boat_name: str):
        boat = ClubDinghy(name=boat_name)
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat.id = self.next_id()

        self.append(boat)

    def list_of_names(self):
        return [boat.name for boat in self]

@dataclass
class CadetAtEventWithClubDinghy(GenericSkipperManObject):
    cadet_id: str
    club_dinghy_id: str
    day: Day

class ListOfCadetAtEventWithClubDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithClubDinghy

    def unique_sorted_list_of_dinghy_ids(self, sorted_list_of_all_dinghies: ListOfClubDinghies):
        list_of_dinghies_here = [object.club_dinghy_id for object in self]
        list_of_dinghies_here = list(set(list_of_dinghies_here))
        sorted_list = [dinghy.id for dinghy in sorted_list_of_all_dinghies if dinghy.id in list_of_dinghies_here]

        return sorted_list

    def DEPRECATE_delete_allocation_for_cadet(self, cadet_id: str):
        ## allowed to fail
        try:
            idx = self.idx_of_item_with_cadet_id(cadet_id)
            self.pop(idx)
        except:
            return

    def update_allocation_for_cadet_on_day(self, cadet_id: str, day: Day, club_dinghy_id: str):
        self.delete_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day)
        self.append(CadetAtEventWithClubDinghy(cadet_id=cadet_id, club_dinghy_id=club_dinghy_id, day=day))

    def delete_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        ## allowed to fail
        idx = self.index_of_item_for_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if idx is missing_data:
            return

        self.pop(idx)


    def idx_of_item_with_cadet_id(self, cadet_id: str):
        idx = [item for item in self if item.cadet_id == cadet_id]
        if len(idx)==0:
            return missing_data
        elif len(idx)>1:
            raise Exception("Can only have one boat per cadet")

        return self.index(idx[0])

    def DEPRECATE_dinghy_for_cadet_id(self, cadet_id:str, default = missing_data) -> str:
        list_of_items = [item.club_dinghy_id for item in self if item.cadet_id == cadet_id]
        if len(list_of_items)==0:
            return default
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

    def dinghy_for_cadet_id_on_day\
                    (self, cadet_id:str, day: Day, default = missing_data) -> str:
        item = self.item_for_cadet_id_on_day(cadet_id=cadet_id, day=day, default=missing_data)
        if item is missing_data:
            return default

        return item.club_dinghy_id



    def index_of_item_for_cadet_id_on_day\
                    (self, cadet_id:str, day: Day) -> int:

        item = self.item_for_cadet_id_on_day(cadet_id=cadet_id, day=day, default=missing_data)
        if item is missing_data:
            return missing_data

        return self.index(item)

    def item_for_cadet_id_on_day\
                    (self, cadet_id:str, day: Day, default = missing_data) -> CadetAtEventWithClubDinghy:
        list_of_items = [item for item in self if item.cadet_id == cadet_id and item.day == day]
        if len(list_of_items)==0:
            return default
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

    def list_of_unique_cadet_ids(self): ##should be unique
        return list(set([item.cadet_id for item in self]))

NO_BOAT = ''
