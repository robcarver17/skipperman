import datetime

from app.objects.constants import missing_data

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.committee import ListOfCadetsOnCommittee, CadetOnCommittee, ListOfCadetsWithIdOnCommittee

from app.backend.data.cadets import CadetData

from app.data_access.storage_layer.api import DataLayer


class CadetCommitteeData:
    def __init__(self, data_layer: DataLayer):
        self.data_layer = data_layer
        self.store = data_layer.store

    def cadet_on_committee_status_str(self, cadet: Cadet) -> str:
        list_of_committee_members = self.get_list_of_cadets_with_id_on_committee()
        member = list_of_committee_members.cadet_committee_member_with_id(cadet.id)
        if member is missing_data:
            return "Not on cadet committee"

        return member.status_string()


    def elect_to_committee_with_dates(
        self,
        cadet: Cadet,
        date_term_start: datetime.date,
        date_term_end: datetime.date,
    ):
        list_of_committee_members = self.get_list_of_cadets_with_id_on_committee()
        list_of_committee_members.add_new_members(
            cadet_id=cadet.id,
            date_term_starts=date_term_start,
            date_term_ends=date_term_end,
        )
        self.save_list_of_cadets_with_id_on_committee(list_of_committee_members)

    def deselect_from_committee(self, cadet_id: str):
        list_of_committee_members = self.get_list_of_cadets_with_id_on_committee()
        list_of_committee_members.deselect_member(cadet_id=cadet_id)
        self.save_list_of_cadets_with_id_on_committee(list_of_committee_members)

    def reselect_to_committee(self, cadet_id: str):
        list_of_committee_members = self.get_list_of_cadets_with_id_on_committee()
        list_of_committee_members.reselect_member(cadet_id=cadet_id)
        self.save_list_of_cadets_with_id_on_committee(list_of_committee_members)

    def toggle_selection_for_cadet_committee_member(self, cadet: Cadet):

        committee_members = self.get_list_of_cadets_with_id_on_committee()
        specific_member = committee_members.cadet_committee_member_with_id(cadet.id)
        if specific_member is missing_data:
            raise (
                "Cadet %s is not on committee so can't be selected / deselected" % cadet
            )

        currently_deselected = specific_member.deselected
        if currently_deselected:
            self.reselect_to_committee(cadet.id)
        else:
            self.deselect_from_committee(cadet.id)

    def get_list_of_cadets_not_on_committee_ordered_by_age(self) -> ListOfCadets:
        all_cadets = self.cadet_data.get_list_of_cadets()
        list_of_committee_members = (
            self.get_list_of_cadets_with_id_on_committee()
        )
        list_of_committee_member_ids = list_of_committee_members.list_of_cadet_ids()

        list_of_cadets = ListOfCadets(
            [
                cadet
                for cadet in all_cadets
                if cadet.id not in list_of_committee_member_ids
            ]
        )

        return list_of_cadets.sort_by_dob_desc()

    def get_list_of_cadets_on_committee(self) -> ListOfCadetsOnCommittee:
        list_of_cadets = self.cadet_data.get_list_of_cadets()
        list_of_committee_members = (
            self.get_list_of_cadets_with_id_on_committee()
        )
        list_of_cadets_on_committee = [
            list_of_cadets.cadet_with_id(cadet_on_committee.cadet_id)
            for cadet_on_committee in list_of_committee_members
        ]

        list_of_cadets_on_committee = ListOfCadetsOnCommittee(
            [
                CadetOnCommittee(cadet=cadet, cadet_on_committee=cadet_on_committee)
                for cadet, cadet_on_committee in zip(
                    list_of_cadets_on_committee, list_of_committee_members
                )
            ]
        )

        list_of_cadets_on_committee.sort()

        return list_of_cadets_on_committee

    def get_list_of_current_cadets_on_committee(self) -> ListOfCadetsWithIdOnCommittee:
        committee = self.get_list_of_cadets_with_id_on_committee()

        return committee.currently_active()


    def get_list_of_cadets_with_id_on_committee(self) -> ListOfCadetsWithIdOnCommittee:
        return self.data_layer.get_list_of_cadets_on_committee()

    def save_list_of_cadets_with_id_on_committee(
        self, list_of_cadets_on_committee: ListOfCadetsWithIdOnCommittee
    ):
        self.data_layer.save_list_of_cadets_on_committee(list_of_cadets_on_committee)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_layer)
