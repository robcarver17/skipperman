import datetime
from copy import copy
from dataclasses import dataclass
from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets import CadetData, SORT_BY_DOB_DSC, SORT_BY_DOB_ASC
from app.data_access.configuration.configuration import MIN_CADET_AGE, MAX_CADET_AGE
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.committee import CadetCommitteeMember
from app.objects.constants import arg_not_passed, missing_data


def add_new_verified_cadet(interface: abstractInterface, cadet: Cadet) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet_data.add_cadet(cadet)

    return cadet


def confirm_cadet_exists(interface: abstractInterface, cadet_selected: str):
    cadet_data = CadetData(interface.data)
    cadet_data.confirm_cadet_exists(cadet_selected)


def get_list_of_cadets_as_str_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets) -> list:
    list_of_cadets_similar_to_first = get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets=from_list_of_cadets)
    return [str(cadet) for cadet in list_of_cadets_similar_to_first]

def get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets) -> ListOfCadets:
    list_of_cadets = copy(from_list_of_cadets)

    similar_cadets = list_of_cadets.similar_surnames(object_with_name)
    similar_cadets = similar_cadets.sort_by_firstname()

    first_lot = []
    for cadet in similar_cadets:
        ## avoid double counting
        first_lot.append(list_of_cadets.pop_with_id(cadet.id))

    return ListOfCadets(first_lot+list_of_cadets)

def get_cadet_from_id(interface: abstractInterface, cadet_id: str) -> Cadet:
    list_of_cadets = load_list_of_all_cadets(interface)

    return list_of_cadets.object_with_id(cadet_id)



def get_cadet_from_list_of_cadets(interface: abstractInterface, cadet_selected: str) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_selected)

    return cadet


def get_sorted_list_of_cadets(interface: abstractInterface, sort_by: str = arg_not_passed) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet




def cadet_name_from_id(interface: abstractInterface, cadet_id: str) -> str:
    cadet = cadet_from_id(interface=interface, cadet_id=cadet_id)

    return cadet.name


def cadet_from_id(interface: abstractInterface, cadet_id: str) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_with_id_(cadet_id)

    return cadet



LOWEST_FEASIBLE_CADET_AGE = MIN_CADET_AGE - 2
HIGHEST_FEASIBLE_CADET_AGE = MAX_CADET_AGE + 20  ## might be backfilling



def verify_cadet_and_warn(interface: abstractInterface, cadet: Cadet) -> str:
    print("Checking %s" % cadet)
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet, interface=interface)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(interface: abstractInterface, cadet: Cadet) -> str:
    similar_cadets = get_list_of_similar_cadets(interface=interface, cadet=cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        ## Some similar group_allocations, let's see if it's a match
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


def get_list_of_similar_cadets(interface: abstractInterface, cadet: Cadet) -> list:
    cadet_data = CadetData(interface.data)
    return cadet_data.similar_cadets(cadet)


def get_matching_cadet_with_id_or_missing_data(
    interface: abstractInterface,
    cadet: Cadet,
) -> Cadet:
    cadet_data = CadetData(interface.data)
    matched_cadet_with_id = cadet_data.get_matching_cadet_with_id_or_missing_data(cadet)

    return matched_cadet_with_id


def load_list_of_all_cadets(interface: abstractInterface) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_list_of_cadets()


def modify_cadet(interface: abstractInterface, cadet_id: str, new_cadet: Cadet):
    cadet_data = CadetData(interface.data)
    cadet_data.modify_cadet(cadet_id=cadet_id, new_cadet=new_cadet)


def get_list_of_cadets_not_on_committee_ordered_by_age(interface: abstractInterface) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    all_cadets = get_sorted_list_of_cadets(interface=interface, sort_by=SORT_BY_DOB_ASC)
    committee = cadet_data.get_list_of_cadets_on_committee()

    list_of_cadets = ListOfCadets([cadet for cadet in all_cadets if cadet.id not in committee.list_of_cadet_ids()])

    return list_of_cadets

@dataclass
class CadetOnCommitteeWithName:
    cadet_on_committee: CadetCommitteeMember
    cadet: Cadet

    def __lt__(self, other):
        if self.cadet_on_committee.status_string()<other.cadet_on_committee.status_string():
            return True
        elif self.cadet_on_committee.status_string()>other.cadet_on_committee.status_string():
            return False

        return self.cadet.name<other.cadet.name

    @property
    def cadet_id(self):
        return self.cadet.id

    @property
    def deselected(self):
        return self.cadet_on_committee.deselected


class ListOfCadetsOnCommitteeWithName(List[CadetOnCommitteeWithName]):
    pass

def get_list_of_cadets_with_names_on_committee(interface: abstractInterface) -> ListOfCadetsOnCommitteeWithName:
    cadet_data = CadetData(interface.data)
    list_of_cadets = cadet_data.get_list_of_cadets()
    list_of_committee_members = cadet_data.get_list_of_cadets_on_committee()
    list_of_cadets_on_committee = [list_of_cadets.cadet_with_id(cadet_on_committee.cadet_id) for cadet_on_committee in list_of_committee_members]

    list_of_cadets_on_committee = ListOfCadetsOnCommitteeWithName(
        [
            CadetOnCommitteeWithName(cadet=cadet, cadet_on_committee=cadet_on_committee)
            for cadet, cadet_on_committee in zip(list_of_cadets_on_committee, list_of_committee_members)])

    list_of_cadets_on_committee.sort()

    return list_of_cadets_on_committee

def get_list_of_cadets_not_on_committee_born_after_sept_first_in_year(interface: abstractInterface,
                                                                      next_year_for_committee: int) -> ListOfCadets:

    cadet_data = CadetData(interface.data)
    list_of_cadets = cadet_data.get_list_of_cadets()
    list_of_committee_members = cadet_data.get_list_of_cadets_on_committee()

    list_of_cadets = [cadet for cadet in list_of_cadets if cadet.date_of_birth<datetime.date(next_year_for_committee-16,9,1)
                        and cadet.date_of_birth>=datetime.date(next_year_for_committee-17, 9,1)
                      and cadet.id not in list_of_committee_members.list_of_cadet_ids()]

    return ListOfCadets(list_of_cadets).sort_by_dob_asc()

def get_next_year_for_cadet_committee():
    today = datetime.date.today()
    if today.month<9:
        return today.year
    else:
        return today.year+1


def add_new_cadet_to_committee(interface: abstractInterface, cadet: Cadet, date_term_start: datetime.date, date_term_end: datetime.date):
    cadet_data = CadetData(interface.data)
    cadet_data.elect_to_committee_with_dates(cadet=cadet,
                                             date_term_end=date_term_end,
                                             date_term_start=date_term_start
                                             )


def toggle_selection_for_cadet_committee_member(interface: abstractInterface, cadet_id: str):
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_with_id_(cadet_id)
    committee_members = cadet_data.get_list_of_cadets_on_committee()
    specific_member = committee_members.cadet_committee_member_with_id(cadet_id)
    if specific_member is missing_data:
        interface.log_error("Cadet %s is not on committee so can't be selected / deselected" % cadet)

    currently_deselected = specific_member.deselected
    if currently_deselected:
        cadet_data.reselect_to_committee(cadet)
    else:
        cadet_data.deselect_from_committee(cadet)
