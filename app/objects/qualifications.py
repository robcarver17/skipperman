import datetime
from dataclasses import dataclass
from typing import List

from app.objects.cadets import ListOfCadets

from app.objects.utils import in_x_not_in_y

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds, \
    GenericListOfObjects


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
    date: datetime.date

class ListOfCadetsWithQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetWithQualification

    def sort_by_date(self):
        return ListOfCadetsWithQualifications(sorted(self, key = lambda object: object.date, reverse=True))

    def apply_qualification_to_cadet(self, cadet_id: str, qualification_id: str):
        if self.does_cadet_id_have_qualification(cadet_id=cadet_id, qualification_id=qualification_id):
            return
        self.append(CadetWithQualification(cadet_id=cadet_id, qualification_id=qualification_id, date=datetime.datetime.today()))


    def remove_qualification_from_cadet(self, cadet_id: str, qualification_id: str):
        for item in self:
            if item.cadet_id == cadet_id and item.qualification_id == qualification_id:
                self.remove(item)

    def list_of_cadet_ids_with_qualification(self, qualification_id: str) -> List[str]:
        return [item.cadet_id for item in self if item.qualification_id==qualification_id]

    def does_cadet_id_have_qualification(self, cadet_id: str, qualification_id: str):
        list_of_qualification_ids = self.list_of_qualification_ids_for_cadet(cadet_id)

        return qualification_id in list_of_qualification_ids

    def list_of_qualification_ids_for_cadet(self, cadet_id: str):
        matching = [item.qualification_id for item in self if item.cadet_id ==cadet_id]
        return matching



@dataclass
class NamedCadetWithQualification(GenericSkipperManObject):
    cadet_name: str
    qualification_name: str
    date: datetime.date

class ListOfNamedCadetsWithQualifications(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return NamedCadetWithQualification

    def sort_by_date(self):
        return ListOfNamedCadetsWithQualifications(sorted(self, key = lambda object: object.date, reverse=True))

    @classmethod
    def from_id_lists(cls, list_of_qualifications: ListOfQualifications, list_of_cadets: ListOfCadets, list_of_cadets_with_qualifications: ListOfCadetsWithQualifications,
                      ):

        return ListOfNamedCadetsWithQualifications([
            NamedCadetWithQualification(
                cadet_name=list_of_cadets.cadet_with_id(cadet_id=cadet_with_qualification.cadet_id).name,
                qualification_name=list_of_qualifications.name_given_id(cadet_with_qualification.qualification_id),
                date=cadet_with_qualification.date
            )

            for cadet_with_qualification in list_of_cadets_with_qualifications
        ])