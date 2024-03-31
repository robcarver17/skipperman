
from dataclasses import dataclass
from typing import List

from app.objects.utils import in_x_not_in_y

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class Qualification(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name


class ListOfQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Qualification

    def name_given_id(self, id: str) -> str:
        names = [item.name for item in self if item.id == id]

        if len(names)==0:
            return missing_data
        elif len(names)>1:
            raise Exception("Found more than one qualification with same ID should be impossible")

        return names[0]

    def delete_given_name(self, name: str):
        idx = self.idx_given_name(name)
        if idx is missing_data:
            raise Exception("Can't find name to delete %s" % name)
        self.pop(idx)

    def idx_given_name(self, name: str):
        id = self.id_given_name(name)
        return self.index_of_id(id)

    def id_given_name(self, name: str):
        id = [item.id for item in self if item.name == name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one qualification with same name should be impossible")

        return str(id[0])

    def add(self, name: str):
        qualification = Qualification(name=name)
        try:
            assert name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate qualification %s already exists" % name)
        qualification.id = self.next_id()

        self.append(qualification)

    def list_of_names(self):
        return [qual.name for qual in self]

@dataclass
class CadetWithQualification(GenericSkipperManObject):
    cadet_id: str
    qualification_id: str

class ListOfCadetsWithQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetWithQualification

    def list_of_qualification_ids_for_cadet(self, cadet_id: str):
        matching = [item.qualification_id for item in self if item.cadet_id ==cadet_id]
        return matching

    def update_for_cadet(self,cadet_id:str, list_of_qualification_ids:List[str]):
        current_list = self.list_of_qualification_ids_for_cadet(cadet_id)
        now_deleted = in_x_not_in_y(current_list, list_of_qualification_ids)
        new_qualifications = in_x_not_in_y(list_of_qualification_ids, current_list)
        self.drop(cadet_id, now_deleted=now_deleted)
        self.add(cadet_id, new_qualifications=new_qualifications)

    def drop(self, cadet_id: str, now_deleted: List[str]):
        for item in self:
            if item.cadet_id==cadet_id and item.qualification_id in now_deleted:
                self.remove(item)

    def add(self, cadet_id, new_qualifications: List[str]):
        for qualification_id in new_qualifications:
            self.append(CadetWithQualification(cadet_id=cadet_id, qualification_id=qualification_id))