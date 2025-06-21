import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects

from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.qualifications import (
    ListOfQualifications,
    ListOfCadetsWithIdsAndQualifications,
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
    def apply_qualification(self, qualification: Qualification, awarded_by: str):
        if self.is_cadet_qualified(qualification):
            return

        self.append(
            QualificationAndDate(
                qualification=qualification,
                date_achieved=datetime.date.today(),
                awarded_by=awarded_by,
            )
        )

    def remove_qualitication(self, qualification: Qualification):
        if not self.is_cadet_qualified(qualification):
            return
        idx_of_qualification_with_date = self.list_of_qualifications().index(
            qualification
        )

        self.pop(idx_of_qualification_with_date)

    def sort_by_qualification_order(self):
        self.sort(key=lambda x: x.qualification.id)

    def is_cadet_qualified(self, qualification: Qualification):
        return qualification in self.list_of_qualifications()

    def list_of_qualifications(self) -> List[Qualification]:
        return [x.qualification for x in self]


class DictOfQualificationsForCadets(Dict[Cadet, QualificationsForCadet]):
    def __init__(
        self,
        dict_of_qualifications: Dict[Cadet, QualificationsForCadet],
        list_of_cadets_with_ids_and_qualifications: ListOfCadetsWithIdsAndQualifications,
    ):
        self._list_of_cadets_with_ids_and_qualifications = (
            list_of_cadets_with_ids_and_qualifications
        )
        super().__init__(dict_of_qualifications)

    def apply_qualification_to_cadet(
        self, cadet: Cadet, qualification: Qualification, awarded_by: str
    ):
        qualifications_for_cadet = self.qualifications_for_cadet(cadet)
        qualifications_for_cadet.apply_qualification(
            qualification, awarded_by=awarded_by
        )
        self.list_of_cadets_with_ids_and_qualifications.apply_qualification_to_cadet(
            cadet_id=cadet.id, qualification_id=qualification.id, awarded_by=awarded_by
        )

    def delete_all_qualifications_for_cadet(self, cadet: Cadet):
        try:
            self.pop(cadet)
        except:
            return

        self.list_of_cadets_with_ids_and_qualifications.delete_all_qualifications_for_cadet(
            cadet_id=cadet.id
        )

    def remove_qualification_from_cadet(
        self, cadet: Cadet, qualification: Qualification
    ):
        qualifications_for_cadet = self.qualifications_for_cadet(cadet)
        qualifications_for_cadet.remove_qualitication(qualification)
        self.list_of_cadets_with_ids_and_qualifications.remove_qualification_from_cadet(
            cadet_id=cadet.id, qualification_id=qualification.id
        )

    def qualifications_for_cadet(self, cadet: Cadet) -> QualificationsForCadet:
        return self.get(cadet, QualificationsForCadet([]))

    @property
    def list_of_cadets_with_ids_and_qualifications(
        self,
    ) -> ListOfCadetsWithIdsAndQualifications:
        return self._list_of_cadets_with_ids_and_qualifications

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

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


def create_dict_of_qualifications_for_cadets(
    list_of_qualifications: ListOfQualifications,
    list_of_cadets: ListOfCadets,
    list_of_cadets_with_ids_and_qualifications: ListOfCadetsWithIdsAndQualifications,
) -> DictOfQualificationsForCadets:
    dict_of_qualifications_for_cadets = DictOfQualificationsForCadets(
        {},
        list_of_cadets_with_ids_and_qualifications=list_of_cadets_with_ids_and_qualifications,
    )
    for cadet_with_id_and_qualification in list_of_cadets_with_ids_and_qualifications:
        update_dict_of_qualifications_for_cadets(
            cadet_with_id_and_qualification=cadet_with_id_and_qualification,
            list_of_cadets=list_of_cadets,
            list_of_qualifications=list_of_qualifications,
            dict_of_qualifications_for_cadets=dict_of_qualifications_for_cadets,
        )

    return dict_of_qualifications_for_cadets


def update_dict_of_qualifications_for_cadets(
    cadet_with_id_and_qualification,
    list_of_cadets: ListOfCadets,
    list_of_qualifications: ListOfQualifications,
    dict_of_qualifications_for_cadets: DictOfQualificationsForCadets,
):
    cadet = list_of_cadets.cadet_with_id(cadet_with_id_and_qualification.cadet_id)
    list_of_qualifications_and_dates_for_cadet = (
        dict_of_qualifications_for_cadets.qualifications_for_cadet(cadet)
    )

    qualification = list_of_qualifications.qualification_given_id(
        cadet_with_id_and_qualification.qualification_id
    )
    date_achieved = cadet_with_id_and_qualification.date
    qualification_and_date = QualificationAndDate(
        qualification=qualification,
        date_achieved=date_achieved,
        awarded_by=cadet_with_id_and_qualification.awarded_by,
    )

    list_of_qualifications_and_dates_for_cadet.append(qualification_and_date)
    dict_of_qualifications_for_cadets[
        cadet
    ] = list_of_qualifications_and_dates_for_cadet


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
