
from dataclasses import dataclass
from typing import List

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

    def id_given_name(self, name: str) -> str:
        ids = [item.id for item in self if item.name == name]

        if len(ids)==0:
            return missing_data
        elif len(ids)>1:
            raise Exception("Found more than one boat with same name should be impossible")

        return ids[0]

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
NOT_ALLOCATED = "Unallocated"

NO_PARTNERSHIP_LIST = [NOT_ALLOCATED, NO_PARTNER_REQUIRED]

def no_partnership(partnership_str: str):
    return partnership_str in NO_PARTNERSHIP_LIST

def valid_partnership(partnership_str: str):
    return not no_partnership(partnership_str)

@dataclass
class CadetAtEventWithDinghy(GenericSkipperManObject):
    cadet_id: str
    boat_class_id: str
    sail_number: str
    partner_cadet_id: str = NO_PARTNER_REQUIRED

UNCHANGED = "unchanged"
WAS_INVALID_NOW_INVALID_CHANGED= "invalid_changed"
WAS_INVALID_NOW_VALID = "was_invalid_now_valid"
WAS_VALID_NOW_INVALID = "was_valid_now_invalid"
WAS_VALID_NOW_VALID_CHANGED  ="valid_changed"


class ListOfCadetAtEventWithDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithDinghy

    def update_boat_info_for_cadet_and_partner_at_event(
        self,
        cadet_at_event_with_dinghy: CadetAtEventWithDinghy
    ):
        cadet_id = cadet_at_event_with_dinghy.cadet_id
        self.update_boat_for_cadet(
            cadet_id=cadet_id,
            sail_number=cadet_at_event_with_dinghy.sail_number,
            boat_class_id=cadet_at_event_with_dinghy.boat_class_id
        )
        self.modify_two_handed_partnership(cadet_id=cadet_id,
                                           new_two_handed_partner_id=cadet_at_event_with_dinghy.partner_cadet_id)

    def modify_two_handed_partnership(self,  cadet_id: str,  new_two_handed_partner_id: str):
        how_changed = self.how_has_partnership_id_changed(cadet_id=cadet_id, new_two_handed_partner_id=new_two_handed_partner_id)
        if how_changed==UNCHANGED:
            pass
        elif how_changed==WAS_INVALID_NOW_INVALID_CHANGED:
            ## change only this cadet, change of state from singlehanded to not allocated or reverse
            self.add_two_handed_partner_to_existing_cadet(cadet_id=cadet_id, partner_id=new_two_handed_partner_id)
        elif how_changed==WAS_VALID_NOW_VALID_CHANGED:
            self.remove_two_handed_partner_from_existing_partner_of_cadet(cadet_id)
            self.create_two_handed_partnership(cadet_id, new_two_handed_partner_id)
        elif how_changed == WAS_VALID_NOW_INVALID:
            self.remove_two_handed_partner_from_existing_partner_of_cadet(cadet_id)
            self.remove_two_handed_partner_from_existing_cadet(cadet_id)
        elif how_changed == WAS_INVALID_NOW_VALID:
            self.create_two_handed_partnership(cadet_id, new_two_handed_partner_id)
        else:
            raise Exception("Shouldn't get here!")

    def create_two_handed_partnership(self, cadet_id: str,  new_two_handed_partner_id: str):
        self.add_two_handed_partner_to_existing_cadet(cadet_id=cadet_id, partner_id=new_two_handed_partner_id)

        ## second cadet might not exist, this ensures they do
        first_cadet = self.object_with_cadet_id(cadet_id)
        self.update_boat_for_cadet(first_cadet.partner_cadet_id, sail_number=first_cadet.sail_number, boat_class_id=first_cadet.boat_class_id)
        self.add_two_handed_partner_to_existing_cadet(cadet_id=new_two_handed_partner_id, partner_id=cadet_id)

    def add_two_handed_partner_to_existing_cadet(self, cadet_id, partner_id):
        cadet_in_data = self.object_with_cadet_id(cadet_id)
        cadet_in_data.partner_cadet_id = partner_id

    def remove_two_handed_partner_from_existing_partner_of_cadet(self, cadet_id):
        cadet_in_data = self.object_with_cadet_id(cadet_id)
        partner_id = cadet_in_data.partner_cadet_id
        self.clear_boat_details_from_existing_cadet_id(partner_id)

    def clear_boat_details_from_existing_cadet_id(self, cadet_id: str):
        idx=self.idx_of_item_with_cadet_id(cadet_id)
        self.pop(idx)

    def remove_two_handed_partner_from_existing_cadet(self, cadet_id):
        cadet_in_data = self.object_with_cadet_id(cadet_id)
        cadet_in_data.partner_cadet_id = NOT_ALLOCATED ## Assumption is we will be allocating to someone else. Boat details will remain

    def how_has_partnership_id_changed(self, cadet_id: str,  new_two_handed_partner_id: str) -> str:
        ## Changes only apply to the first cadet
        original_cadet = self.object_with_cadet_id(cadet_id)
        original_partner_id = original_cadet.partner_cadet_id

        if original_partner_id == new_two_handed_partner_id:
            return UNCHANGED

        was_valid = valid_partnership(original_partner_id)
        now_valid = valid_partnership(new_two_handed_partner_id)

        if was_valid and now_valid:
            return WAS_VALID_NOW_VALID_CHANGED
        elif was_valid and not now_valid:
            return WAS_VALID_NOW_INVALID
        elif not was_valid and now_valid:
            return WAS_INVALID_NOW_VALID
        elif not was_valid and not now_valid:
            return WAS_INVALID_NOW_INVALID_CHANGED
        else:
            raise Exception("Shouldn't get here")


    def update_boat_for_cadet(self, cadet_id: str, boat_class_id: str, sail_number: str):
        object_with_id = self.object_with_cadet_id(cadet_id)
        if object_with_id is missing_data:
            self.add_boat_for_no_existing_cadet(cadet_id=cadet_id, boat_class_id=boat_class_id, sail_number=sail_number)
        else:
            object_with_id.boat_class_id = boat_class_id
            object_with_id.sail_number = sail_number

    def add_boat_for_no_existing_cadet(self, cadet_id: str, boat_class_id: str, sail_number: str):
        self.append(CadetAtEventWithDinghy(cadet_id=cadet_id, boat_class_id=boat_class_id, sail_number=sail_number))

    def object_with_cadet_id(self, cadet_id: str) -> CadetAtEventWithDinghy:
        idx = self.idx_of_item_with_cadet_id(cadet_id)
        if idx is missing_data:
            return missing_data
        return self[idx]

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
        list_of_items = [item.boat_class_id for item in self if item.cadet_id == cadet_id]
        if len(list_of_items)==0:
            return missing_data
        if len(list_of_items)>1:
            raise Exception("Can only have one dinghy per cadet")

        return list_of_items[0]

    def list_of_cadet_ids(self):
        ## unique
        return [item.cadet_id for item in self]

    def list_of_boat_class_ids(self):
        ## not unique
        return [item.boat_class_id for item in self]

    def list_of_partner_ids_excluding_not_valid(self)-> List[str]:
        return [object.partner_cadet_id for object in self if valid_partnership(object.partner_cadet_id)]

    def unique_sorted_list_of_boat_class_ids(self, all_boat_classes: ListOfDinghies) -> List[str]:
        return [object.id for object in all_boat_classes if object.id in self.list_of_boat_class_ids()]


def compare_list_of_cadets_with_dinghies_and_return_list_with_changed_values(new_list: ListOfCadetAtEventWithDinghies, existing_list: ListOfCadetAtEventWithDinghies):
    updated_list = ListOfCadetAtEventWithDinghies([])
    for potentially_updated_cadet_at_event in new_list:
        cadet_in_existing_list = existing_list.object_with_cadet_id(potentially_updated_cadet_at_event.cadet_id)

        already_in_a_changed_partnership = is_cadet_already_in_changed_partnership(updated_list=updated_list, potentially_updated_cadet_at_event=potentially_updated_cadet_at_event)
        if already_in_a_changed_partnership:
            continue

        if cadet_in_existing_list is missing_data:
            print("new cadet %s" % str(potentially_updated_cadet_at_event))
            updated_list.append(potentially_updated_cadet_at_event)
            continue

        elif cadet_in_existing_list==potentially_updated_cadet_at_event:
            print("no change to %s" % str(potentially_updated_cadet_at_event))
            ## no change
            continue
        else:
            print("Change from %s to %s" % (str(cadet_in_existing_list), str(potentially_updated_cadet_at_event)))
            updated_list.append(potentially_updated_cadet_at_event)

    return updated_list

def is_cadet_already_in_changed_partnership(updated_list: ListOfCadetAtEventWithDinghies,  potentially_updated_cadet_at_event: CadetAtEventWithDinghy)-> bool:
    list_of_changed_partner_id = updated_list.list_of_partner_ids_excluding_not_valid()
    cadet_id = potentially_updated_cadet_at_event.cadet_id
    changed= cadet_id in list_of_changed_partner_id

    return changed
