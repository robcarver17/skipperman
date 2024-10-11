import datetime
from dataclasses import dataclass
from typing import List, Dict

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject
from app.objects.qualifications import ListOfQualifications, ListOfCadetsWithIdsAndQualifications, Qualification

@dataclass
class QualificationAndDate:
    qualification: Qualification
    date_achieved: datetime.date

    @property
    def name(self):
        return self.qualification.name

class QualificationsForCadet(List[QualificationAndDate]):
    def sort_by_qualification_order(self):
        self.sort(key=lambda x: x.qualification.id)

class DictOfQualificationsForCadets(Dict[Cadet, QualificationsForCadet]):
    def __init__(self, dict_of_qualifications: Dict[Cadet, QualificationsForCadet], list_of_cadets_with_ids_and_qualifications: ListOfCadetsWithIdsAndQualifications):
        self._list_of_cadets_with_ids_and_qualifications = list_of_cadets_with_ids_and_qualifications
        super().__init__(dict_of_qualifications)
    def qualifications_for_cadet(self, cadet: Cadet) -> QualificationsForCadet:
        return self.get(cadet, QualificationsForCadet([]))

    @property
    def list_of_cadets_with_ids_and_qualifications(self) -> ListOfCadetsWithIdsAndQualifications:
        return self._list_of_cadets_with_ids_and_qualifications

def create_dict_of_qualifications_for_cadets(list_of_qualifications: ListOfQualifications,
                                             list_of_cadets: ListOfCadets,
                                             list_of_cadets_with_ids_and_qualifications: ListOfCadetsWithIdsAndQualifications) -> DictOfQualificationsForCadets:

    dict_of_qualifications_for_cadets = DictOfQualificationsForCadets({}, list_of_cadets_with_ids_and_qualifications=list_of_cadets_with_ids_and_qualifications)
    for cadet_with_id_and_qualification in list_of_cadets_with_ids_and_qualifications:
        update_dict_of_qualifications_for_cadets(
            cadet_with_id_and_qualification=cadet_with_id_and_qualification,
            list_of_cadets=list_of_cadets,
            list_of_qualifications=list_of_qualifications,
            dict_of_qualifications_for_cadets=dict_of_qualifications_for_cadets
        )

    return dict_of_qualifications_for_cadets

def update_dict_of_qualifications_for_cadets(cadet_with_id_and_qualification,
                                             list_of_cadets: ListOfCadets,
                                             list_of_qualifications: ListOfQualifications,
                                             dict_of_qualifications_for_cadets: DictOfQualificationsForCadets):

    cadet = list_of_cadets.cadet_with_id(cadet_with_id_and_qualification.cadet_id)
    list_of_qualifications_and_dates_for_cadet = dict_of_qualifications_for_cadets.get(cadet, QualificationsForCadet([]))

    qualification = list_of_qualifications.object_with_id(cadet_with_id_and_qualification.qualification_id)
    date_achieved = cadet_with_id_and_qualification.date
    qualification_and_date = QualificationAndDate(qualification=qualification, date_achieved=date_achieved)

    list_of_qualifications_and_dates_for_cadet.append(qualification_and_date)
    dict_of_qualifications_for_cadets[cadet] = list_of_qualifications_and_dates_for_cadet


### USED FOR WRITE ONLY
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
        return ListOfNamedCadetsWithQualifications(
            sorted(self, key=lambda object: object.date, reverse=True)
        )

    @classmethod
    def from_id_lists(
        cls,
        list_of_qualifications: ListOfQualifications,
        list_of_cadets: ListOfCadets,
        list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications,
    ):
        return ListOfNamedCadetsWithQualifications(
            [
                NamedCadetWithQualification(
                    cadet_name=list_of_cadets.cadet_with_id(
                        cadet_id=cadet_with_qualification.cadet_id
                    ).name,
                    qualification_name=list_of_qualifications.name_given_id(
                        cadet_with_qualification.qualification_id
                    ),
                    date=cadet_with_qualification.date,
                )
                for cadet_with_qualification in list_of_cadets_with_qualifications
            ]
        )
