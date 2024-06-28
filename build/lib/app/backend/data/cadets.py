import datetime

from app.objects.constants import missing_data

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.committee import ListOfCadetsOnCommittee, CadetOnCommittee

from app.backend.data.cadets_at_id_level import CadetData
from app.data_access.storage_layer.store import DataAccessMethod


from app.data_access.storage_layer.api import DataLayer




class CadetCommitteeData():
    def __init__(self, data_layer: DataLayer):
        self.data_layer = data_layer
        self.store = data_layer.store

    def elect_to_committee_with_dates(self, cadet: Cadet, date_term_start: datetime.date, date_term_end: datetime.date):
        cadet_data = self.cadet_at_id_level_data
        cadet_data.elect_to_committee_with_dates(cadet_id=cadet.id,
                                                 date_term_end=date_term_end,
                                                 date_term_start=date_term_start
                                                 )


    def toggle_selection_for_cadet_committee_member(self, cadet: Cadet):
        cadet_data = self.cadet_at_id_level_data
        committee_members = cadet_data.get_list_of_cadets_with_id_on_committee()
        specific_member = committee_members.cadet_committee_member_with_id(cadet.id)
        if specific_member is missing_data:
            raise("Cadet %s is not on committee so can't be selected / deselected" % cadet)

        currently_deselected = specific_member.deselected
        if currently_deselected:
            cadet_data.reselect_to_committee(cadet.id)
        else:
            cadet_data.deselect_from_committee(cadet.id)

    def get_list_of_cadets_not_on_committee_ordered_by_age(self) -> ListOfCadets:
        all_cadets = self.cadet_at_id_level_data.get_list_of_cadets()
        list_of_committee_members = self.cadet_at_id_level_data.get_list_of_cadets_with_id_on_committee()
        list_of_committee_member_ids= list_of_committee_members.list_of_cadet_ids()

        list_of_cadets = ListOfCadets([cadet for cadet in all_cadets if cadet.id not in list_of_committee_member_ids])

        return list_of_cadets.sort_by_dob_desc()

    def get_list_of_cadets_on_committee(self) -> ListOfCadetsOnCommittee:
        list_of_cadets = self.cadet_at_id_level_data.get_list_of_cadets()
        list_of_committee_members = self.cadet_at_id_level_data.get_list_of_cadets_with_id_on_committee()
        list_of_cadets_on_committee = [list_of_cadets.cadet_with_id(cadet_on_committee.cadet_id) for cadet_on_committee
                                       in list_of_committee_members]

        list_of_cadets_on_committee = ListOfCadetsOnCommittee(
            [
                CadetOnCommittee(cadet=cadet, cadet_on_committee=cadet_on_committee)
                for cadet, cadet_on_committee in zip(list_of_cadets_on_committee, list_of_committee_members)])

        list_of_cadets_on_committee.sort()

        return list_of_cadets_on_committee

    @property
    def cadet_at_id_level_data(self) -> CadetData:
        return CadetData(self.data_layer)