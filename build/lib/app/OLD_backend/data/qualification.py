from app.objects.qualifications import (
    ListOfQualifications,
    ListOfCadetsWithIdsAndQualifications,
    Qualification,
)

from typing import List

from app.data_access.store.data_access import DataLayer
from app.objects.cadets import Cadet


class QualificationData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def highest_name_of_qualification_for_cadet(self, cadet: Cadet) -> str:
        list_of_ids = self.list_of_qualification_ids_for_cadet(cadet)
        list_of_qualification = self.load_list_of_qualifications()
        highest = ""
        for qual in list_of_qualification:
            if qual.id in list_of_ids:
                highest = qual.name

        return highest

    def list_of_named_qualifications_for_cadet(self, cadet: Cadet) -> List[str]:
        list_of_qualifications_for_cadet = self.list_of_qualifications_for_cadet(cadet)
        all_qualifications = self.load_list_of_qualifications()
        list_of_names = [
            qualification.name
            for qualification in all_qualifications
            if qualification in list_of_qualifications_for_cadet
        ]

        return list_of_names

    def list_of_qualifications_for_cadet(self, cadet: Cadet) -> List[Qualification]:
        list_of_ids = self.list_of_qualification_ids_for_cadet(cadet)
        list_of_qualifications = [
            self.get_qualification_given_id(id) for id in list_of_ids
        ]

        return list_of_qualifications

    def apply_qualification_to_cadet(self, cadet_id: str, qualification: Qualification):
        list_of_cadets_with_qualifications = (
            self.get_list_of_cadets_with_qualifications()
        )
        list_of_cadets_with_qualifications.apply_qualification_to_cadet(
            cadet_id=cadet_id, qualification_id=qualification.id
        )
        self.save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)

    def remove_qualification_from_cadet(
        self, cadet_id: str, qualification: Qualification
    ):
        list_of_cadets_with_qualifications = (
            self.get_list_of_cadets_with_qualifications()
        )
        list_of_cadets_with_qualifications.remove_qualification_from_cadet(
            cadet_id=cadet_id, qualification_id=qualification.id
        )
        self.save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)

    def list_of_cadet_ids_with_qualification(
        self, qualification: Qualification
    ) -> List[str]:
        list_of_qualification_ids_for_cadet = (
            self.get_list_of_cadets_with_qualifications()
        )
        return list_of_qualification_ids_for_cadet.list_of_cadet_ids_with_qualification(
            qualification_id=qualification.id
        )

    def does_cadet_id_have_qualification(self, cadet_id, qualification_id: str) -> bool:
        list_of_qualification_ids_for_cadet = (
            self.get_list_of_cadets_with_qualifications()
        )

        return list_of_qualification_ids_for_cadet.does_cadet_id_have_qualification(
            cadet_id=cadet_id, qualification_id=qualification_id
        )

    def get_qualification_given_name(self, name: str) -> Qualification:
        list_of_qualifications = self.load_list_of_qualifications()
        idx = list_of_qualifications.idx_given_name(name)
        return list_of_qualifications[idx]

    def list_of_qualification_ids_for_cadet(self, cadet: Cadet) -> List[str]:
        list_of_cadets_with_qualifications = (
            self.get_list_of_cadets_with_qualifications()
        )
        list_of_ids = (
            list_of_cadets_with_qualifications.list_of_qualification_ids_for_cadet(
                cadet_id=cadet.id
            )
        )
        return list_of_ids

    def get_qualification_given_id(self, id: str) -> Qualification:
        list_of_qualifications = self.load_list_of_qualifications()

        return list_of_qualifications.object_with_id(id)

    def get_list_of_all_qualification_names(self) -> List[str]:
        list_of_qualifications = self.load_list_of_qualifications()

        return list_of_qualifications.list_of_names()

    def load_list_of_qualifications(self) -> ListOfQualifications:
        return self.data_api.get_list_of_qualifications()

    def save_list_of_qualifications(self, list_of_qualifications: ListOfQualifications):
        self.data_api.save_list_of_qualifications(list_of_qualifications)

    def get_list_of_cadets_with_qualifications(
        self,
    ) -> ListOfCadetsWithIdsAndQualifications:
        return self.data_api.get_list_of_cadets_with_qualifications()

    def save_list_of_cadets_with_qualifications(
        self, list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications
    ):
        self.data_api.save_list_of_cadets_with_qualifications(
            list_of_cadets_with_qualifications
        )
