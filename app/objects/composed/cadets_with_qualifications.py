import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects

from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.qualifications import (
    Qualification,
)


@dataclass
class QualificationAndDate:
    qualification: Qualification
    date_achieved: datetime.date
    awarded_by: str

    @property
    def name(self):
        return self.qualification.name


class QualificationsForCadet(List[QualificationAndDate]):

    def is_cadet_qualified(self, qualification: Qualification):
        return qualification in self.list_of_qualifications()

    def list_of_qualifications(self) -> List[Qualification]:
        return [x.qualification for x in self]


class DictOfQualificationsForCadets(Dict[Cadet, QualificationsForCadet]):
    def list_of_cadets_and_qualifications_and_dates(
        self,
    ) -> List[Tuple[Cadet, Qualification, datetime.date, str]]:
        all_in_one_list = []
        for cadet in self.list_of_cadets:
            all_quals_cadet = self[cadet]
            for qualification_and_date in all_quals_cadet:
                all_in_one_list.append(
                    (
                        cadet,
                        qualification_and_date.qualification,
                        qualification_and_date.date_achieved,
                        qualification_and_date.awarded_by,
                    )
                )

        return all_in_one_list

    def qualifications_for_cadet(self, cadet: Cadet) -> QualificationsForCadet:
        return self.get(cadet, QualificationsForCadet([]))


    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))





### USED FOR WRITE TO CSV ONLY
@dataclass
class NamedCadetWithQualification(GenericSkipperManObject):
    cadet_name: str
    qualification_name: str
    date: datetime.date
    awarded_by: str


class ListOfNamedCadetsWithQualifications(GenericListOfObjects):
    def _object_class_contained(self):
        return NamedCadetWithQualification

    def sort_by_date(self):
        return ListOfNamedCadetsWithQualifications(
            sorted(self, key=lambda object: object.date, reverse=True)
        )

    @classmethod
    def from_dict_of_qualifications(
        cls, dict_of_qualifications: DictOfQualificationsForCadets
    ):
        list_of_cadets_and_qualifications_and_dates = (
            dict_of_qualifications.list_of_cadets_and_qualifications_and_dates()
        )

        return ListOfNamedCadetsWithQualifications(
            [
                NamedCadetWithQualification(
                    cadet_name=cadet_qualification_date[0].name,
                    qualification_name=cadet_qualification_date[1].name,
                    date=cadet_qualification_date[2],
                    awarded_by=cadet_qualification_date[3],
                )
                for cadet_qualification_date in list_of_cadets_and_qualifications_and_dates
            ]
        )
