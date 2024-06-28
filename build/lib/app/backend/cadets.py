import datetime
from copy import copy
from typing import Tuple

from app.backend.data.cadet_committee import CadetCommitteeData
from app.data_access.configuration.fixed import (
    MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
    MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
    YEARS_ON_CADET_COMMITTEE,
)
from app.data_access.storage_layer.api import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets_at_id_level import CadetData
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.committee import ListOfCadetsOnCommittee
from app.objects.constants import arg_not_passed, missing_data


def add_new_verified_cadet(data_layer: DataLayer, cadet: Cadet) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet_data.add_cadet(cadet)

    return cadet


def confirm_cadet_exists(interface: abstractInterface, cadet_selected: str):
    cadet_data = CadetData(interface.data)
    cadet_data.confirm_cadet_exists(cadet_selected)


def get_list_of_cadets_as_str_similar_to_name_first(
    object_with_name, from_list_of_cadets: ListOfCadets
) -> list:
    list_of_cadets_similar_to_first = get_list_of_cadets_similar_to_name_first(
        object_with_name, from_list_of_cadets=from_list_of_cadets
    )
    return [str(cadet) for cadet in list_of_cadets_similar_to_first]


def get_list_of_cadets_similar_to_name_first(
    object_with_name, from_list_of_cadets: ListOfCadets
) -> ListOfCadets:
    list_of_cadets = copy(from_list_of_cadets)

    similar_cadets = list_of_cadets.similar_surnames(object_with_name)
    similar_cadets = similar_cadets.sort_by_firstname()

    first_lot = []
    for cadet in similar_cadets:
        ## avoid double counting
        first_lot.append(list_of_cadets.pop_with_id(cadet.id))

    return ListOfCadets(first_lot + list_of_cadets)


def DEPRECATE_get_cadet_from_id(interface: abstractInterface, cadet_id: str) -> Cadet:
    list_of_cadets = DEPRECATE_load_list_of_all_cadets(interface)

    return list_of_cadets.object_with_id(cadet_id)


def DEPRECATE_get_cadet_given_cadet_as_str(
    interface: abstractInterface, cadet_selected: str
) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_selected)

    return cadet


def get_cadet_given_cadet_as_str(data_layer: DataLayer, cadet_as_str: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_as_str)

    return cadet


def get_sorted_list_of_cadets(
    interface: abstractInterface, sort_by: str = arg_not_passed
) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet


def cadet_name_from_id(interface: abstractInterface, cadet_id: str) -> str:
    cadet = DEPRECATE_cadet_from_id_USE_get_cadet_from_id(
        interface=interface, cadet_id=cadet_id
    )

    return cadet.name


def DEPRECATE_cadet_from_id_USE_get_cadet_from_id(
    interface: abstractInterface, cadet_id: str
) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_with_id(cadet_id)

    return cadet


def get_cadet_from_id(data_layer: DataLayer, cadet_id: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_with_id(cadet_id)

    return cadet


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


def DEPRECATE_load_list_of_all_cadets(interface: abstractInterface) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_list_of_cadets()


def load_list_of_all_cadets(data_layer: DataLayer) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    return cadet_data.get_list_of_cadets()


def modify_cadet(data_layer: DataLayer, cadet_id: str, new_cadet: Cadet):
    cadet_data = CadetData(data_layer)
    cadet_data.modify_cadet(cadet_id=cadet_id, new_cadet=new_cadet)


def get_list_of_cadets_not_on_committee_ordered_by_age(
    data_layer: DataLayer,
) -> ListOfCadets:
    cadet_data = CadetCommitteeData(data_layer)
    list_of_cadets = cadet_data.get_list_of_cadets_not_on_committee_ordered_by_age()

    return list_of_cadets


def get_list_of_cadets_on_committee(data_layer: DataLayer) -> ListOfCadetsOnCommittee:
    cadet_data = CadetCommitteeData(data_layer)
    return cadet_data.get_list_of_cadets_on_committee()


MIN_AGE_TO_JOIN_COMMITTEE = 16
MAX_AGE_TO_JOIN_COMMITTEE = 17


def get_list_of_cadets_not_on_committee_in_right_age_bracket(
    data_layer: DataLayer, next_year_for_committee: int
) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    list_of_cadets = cadet_data.get_list_of_cadets()
    list_of_committee_members = cadet_data.get_list_of_cadets_with_id_on_committee()

    earliest_date = datetime.date(
        next_year_for_committee - MAX_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )
    latest_date = datetime.date(
        next_year_for_committee - MIN_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )

    list_of_cadets = ListOfCadets(
        [
            cadet
            for cadet in list_of_cadets
            if cadet.date_of_birth < latest_date
            and cadet.date_of_birth >= earliest_date
            and cadet.id not in list_of_committee_members.list_of_cadet_ids()
        ]
    )

    list_of_cadets = list_of_cadets.sort_by_dob_desc()

    return list_of_cadets


def get_next_year_for_cadet_committee():
    today = datetime.date.today()
    if today.month < MONTH_WHEN_CADET_AGE_BRACKET_BEGINS:
        return today.year
    else:
        return today.year + 1


def month_name_when_cadet_committee_age_bracket_begins():
    return datetime.date(1990, MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, 1).strftime("%B")


def add_new_cadet_to_committee(
    data_layer: DataLayer,
    cadet: Cadet,
    date_term_start: datetime.date,
    date_term_end: datetime.date,
):
    cadet_data = CadetCommitteeData(data_layer)
    cadet_data.elect_to_committee_with_dates(
        cadet=cadet, date_term_end=date_term_end, date_term_start=date_term_start
    )


def toggle_selection_for_cadet_committee_member(data_layer: DataLayer, cadet: Cadet):
    cadet_data = CadetCommitteeData(data_layer)
    cadet_data.toggle_selection_for_cadet_committee_member(cadet)


def start_and_end_date_on_cadet_commmittee() -> Tuple[datetime.date, datetime.date]:
    start_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee(),
    )
    end_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee() + YEARS_ON_CADET_COMMITTEE,
    )

    return start_date_on_committee, end_date_on_committee
