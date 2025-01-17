import datetime
from dataclasses import dataclass
from typing import List

from app.objects.exceptions import (
    missing_data,
    arg_not_passed,
    MissingData,
    MultipleMatches,
)
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.generic_objects import (
    GenericSkipperManObject,
    GenericSkipperManObjectWithIds,
)


@dataclass
class Qualification(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ListOfQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Qualification

    def replace(
        self, existing_qualification: Qualification, new_qualification: Qualification
    ):
        index = self.idx_given_name(existing_qualification.name)
        new_qualification.id = existing_qualification.id

        self[index] = new_qualification

    def qualification_given_name(self, name: str):
        idx = self.idx_given_name(name)
        return self[idx]

    def idx_given_name(self, name: str):
        id = self.id_given_name(name)
        return self.index_of_id(id)

    def id_given_name(self, name: str):
        id = [item.id for item in self if item.name == name]

        if len(id) == 0:
            raise MissingData
        elif len(id) > 1:
            raise MultipleMatches(
                "Found more than one qualification with same name should be impossible"
            )

        return str(id[0])

    def add(self, name: str):
        qualification = Qualification(name=name)
        try:
            assert name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate qualification %s already exists" % name
            )
        qualification.id = self.next_id()

        self.append(qualification)

    def list_of_names(self):
        return [qual.name for qual in self]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))


@dataclass
class CadetWithIdAndQualification(GenericSkipperManObject):
    cadet_id: str
    qualification_id: str
    date: datetime.date


class ListOfCadetsWithIdsAndQualifications(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetWithIdAndQualification

    def sort_by_date(self):
        return ListOfCadetsWithIdsAndQualifications(
            sorted(self, key=lambda object: object.date, reverse=True)
        )

    def apply_qualification_to_cadet(self, cadet_id: str, qualification_id: str):
        if self.does_cadet_id_have_qualification(
            cadet_id=cadet_id, qualification_id=qualification_id
        ):
            return
        self.append(
            CadetWithIdAndQualification(
                cadet_id=cadet_id,
                qualification_id=qualification_id,
                date=datetime.datetime.today(),
            )
        )

    def remove_qualification_from_cadet(self, cadet_id: str, qualification_id: str):
        for item in self:
            if item.cadet_id == cadet_id and item.qualification_id == qualification_id:
                self.remove(item)

    def does_cadet_id_have_qualification(self, cadet_id: str, qualification_id: str):
        list_of_qualification_ids = self.list_of_qualification_ids_for_cadet(cadet_id)

        return qualification_id in list_of_qualification_ids

    def list_of_qualification_ids_for_cadet(self, cadet_id: str):
        matching = [item.qualification_id for item in self if item.cadet_id == cadet_id]
        return matching
