
from dataclasses import dataclass

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class Dinghy(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name


class ListOfDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Dinghy

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
        id = [item.id for item in self if item.name == boat_name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one boat with same name should be impossible")

        return self.index_of_id(str(id[0]))

    def add(self, boat_name: str):
        boat = Dinghy(name=boat_name)
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat.id = self.next_id()

        self.append(boat)

    def list_of_names(self):
        return [boat.name for boat in self]

NO_PARTNER_REQUIRED = "Singlehander"
NOT_ALLOCATED = "Doublehander - Unallocated"

@dataclass
class CadetAtEventWithDinghy(GenericSkipperManObject):
    cadet_id: str
    dinghy_id: str
    sail_number: str
    partner_cadet_id: str = NO_PARTNER_REQUIRED


class ListOfCadetAtEventWithDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithDinghy


    def delete_boat_for_cadet(self, cadet_id: str):
        ## allowed to fail
        try:
            idx = self.idx_of_item_with_cadet_id(cadet_id)
            self.pop(idx)
        except:
            return

    def update_boat_for_cadet(self, cadet_id: str, dinghy_id: str, sail_number: str, partner_cadet_id: str):
        self.delete_boat_for_cadet(cadet_id)
        self.append(CadetAtEventWithDinghy(cadet_id=cadet_id, dinghy_id=dinghy_id, sail_number=sail_number, partner_cadet_id=partner_cadet_id))

    def idx_of_item_with_cadet_id(self, cadet_id: str):
        idx = [item for item in self if item.cadet_id == cadet_id]
        if len(idx)==0:
            return missing_data
        elif len(idx)>1:
            raise Exception("Can only have one boat per cadet")

        return self.index(idx[0])

    def cadet_partner_id_for_cadet_id(self, cadet_id:str) -> str:
        list_of_items = [item.partner_cadet_id for item in self if item.cadet_id == cadet_id]
        if len(list_of_items)==0:
            return missing_data
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]


    def sail_number_for_cadet_id(self, cadet_id:str) -> str:
        list_of_items = [item.sail_number for item in self if item.cadet_id == cadet_id]
        if len(list_of_items)==0:
            return missing_data
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

    def boat_class_id_for_cadet_id(self, cadet_id:str) -> str:
        list_of_items = [item.dinghy_id for item in self if item.cadet_id == cadet_id]
        if len(list_of_items)==0:
            return missing_data
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

NO_BOAT = ''
