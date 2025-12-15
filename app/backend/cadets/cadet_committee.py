import datetime
from typing import List, Tuple

from app.data_access.configuration.fixed import (
    MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
    MAX_AGE_TO_JOIN_COMMITTEE,
    MIN_AGE_TO_JOIN_COMMITTEE,
    MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
    YEARS_ON_CADET_COMMITTEE,
    MONTH_WHEN_EGM_HAPPENS,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.membership_status import current_member

from app.backend.cadets.list_of_cadets import DEPRECATE_get_list_of_cadets, get_sorted_list_of_cadets_from_raw_data
from app.objects.composed.committee import ListOfCadetsOnCommittee

from app.objects.cadets import Cadet, ListOfCadets

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_list_of_cadet_committee_members,
)
from app.objects.utilities.exceptions import MissingData, missing_data


def get_list_of_cadets_who_are_members_but_not_on_committee_or_elected_ordered_by_name(
    object_store: ObjectStore,
) -> ListOfCadets:
    all_cadets = get_sorted_list_of_cadets_from_raw_data(object_store)
    list_of_committee_members = get_list_of_cadets_on_committee(object_store)

    list_of_cadets = ListOfCadets(
        [
            cadet
            for cadet in all_cadets
            if not list_of_committee_members.is_cadet_elected_to_committee(cadet)
            and cadet.membership_status == current_member
        ]
    )

    return list_of_cadets.sort_by_name()


def get_cadet_on_committee_status(object_store: ObjectStore, cadet: Cadet) -> str:
    list_of_committee_members = get_list_of_cadets_on_committee(object_store)
    try:
        member = list_of_committee_members.get_cadet_on_committee(cadet)

        return member.status_string()
    except MissingData:
        return "Not on cadet committee"


def get_list_of_cadet_as_str_members_but_not_on_committee_born_in_right_age_bracket(
    object_store: ObjectStore,
) -> List[str]:
    list_of_cadets_not_on_committee_born_in_right_age_bracket = (
        get_list_of_cadets_members_but_not_on_committee_in_right_age_bracket(
            object_store=object_store
        )
    )
    list_of_cadets_not_on_committee_born_in_right_age_bracket = (
        list_of_cadets_not_on_committee_born_in_right_age_bracket.sort_by_name()
    )

    list_of_cadet_as_str_not_on_committee_born_in_right_age_bracket = [
        str(cadet)
        for cadet in list_of_cadets_not_on_committee_born_in_right_age_bracket
    ]

    return list_of_cadet_as_str_not_on_committee_born_in_right_age_bracket


def get_list_of_cadets_members_but_not_on_committee_in_right_age_bracket(
    object_store: ObjectStore,
) -> ListOfCadets:
    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(object_store)

    list_of_cadets = ListOfCadets(
        [
            cadet
            for cadet in list_of_cadets
            if is_cadet_member_not_on_committee_and_in_right_age_bracket_to_join(
                cadet=cadet, object_store=object_store
            )
        ]
    )

    list_of_cadets = list_of_cadets.sort_by_dob_desc()

    return list_of_cadets


def is_cadet_member_not_on_committee_and_in_right_age_bracket_to_join(
    object_store: ObjectStore, cadet: Cadet
) -> bool:
    list_of_committee_members = get_list_of_cadets_on_committee(object_store)
    next_year_for_committee = get_next_year_for_cadet_committee_after_EGM()
    earliest_date, latest_date = earliest_and_latest_date_to_join_committee(
        next_year_for_committee
    )

    return (
        cadet.date_of_birth <= latest_date
        and cadet.date_of_birth >= earliest_date
        and not list_of_committee_members.is_cadet_currently_on_committee(cadet)
        and cadet.membership_status == current_member
    )


### MODIFY


def add_new_cadet_to_committee(
    interface: abstractInterface,
    cadet: Cadet,
    date_term_starts: datetime.date,
    date_term_ends: datetime.date,
    deselected: bool = False
):
    try:
        interface.update(interface.object_store.data_api.data_list_of_cadets_on_committee.add_new_cadet_to_committee,
                         cadet_id=cadet.id,
                         date_term_starts=date_term_starts,
                         date_term_ends=date_term_ends,
                         deselected=deselected
                         )
    except Exception as e:
        interface.log_error("Error %s when adding %s to committee" % (str(e), str(cadet)))


def toggle_selection_for_cadet_committee_member(
    interface: abstractInterface, cadet: Cadet
):
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_cadets_on_committee.toggle_selection_for_cadet_committee_member,
            cadet_id=cadet.id
        )
    except Exception as e:
        interface.log_error("Error %s when modifying cadet committee member %s" % (str(e), str(cadet)))



def DEPRECATE_delete_cadet_from_committee_data(
    interface: abstractInterface, cadet: Cadet, areyousure=False
):
    if not areyousure:
        return

    list_of_committee_members = get_list_of_cadets_on_committee(interface.object_store)
    existing_membership = list_of_committee_members.get_cadet_on_committee(
        cadet, default=missing_data
    )

    list_of_committee_members.delete_cadet_from_data(cadet)
    DEPRECATE_update_list_of_cadets_on_committee(
        object_store=object_store,
        updated_list_of_cadets_on_committee=list_of_committee_members,
    )

    return existing_membership


## STORAGE
def get_list_of_cadets_currently_serving(object_store: ObjectStore) -> ListOfCadets:
    list_of_cadets_on_committee = get_list_of_cadets_on_committee(object_store)

    return list_of_cadets_on_committee.list_of_cadets_currently_serving()


def get_list_of_cadets_on_committee(
    object_store: ObjectStore,
) -> ListOfCadetsOnCommittee:
    return object_store.get(object_store.data_api.data_list_of_cadets_on_committee.get_list_of_cadets_on_committee)


def DEPRECATE_update_list_of_cadets_on_committee(
    object_store: ObjectStore,
    updated_list_of_cadets_on_committee: ListOfCadetsOnCommittee,
):
    object_store.DEPRECATE_update(
        new_object=updated_list_of_cadets_on_committee,
        object_definition=object_definition_for_list_of_cadet_committee_members,
    )


## DATES


def start_and_end_date_on_cadet_commmittee() -> Tuple[datetime.date, datetime.date]:
    start_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee_after_EGM(),
    )
    end_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee_after_EGM() + YEARS_ON_CADET_COMMITTEE,
    )

    return start_date_on_committee, end_date_on_committee


def earliest_and_latest_date_to_join_committee(next_year_for_committee: int):
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

    return earliest_date, latest_date


def get_next_year_for_cadet_committee_after_EGM():
    today = datetime.date.today()
    if today.month < MONTH_WHEN_EGM_HAPPENS:
        return today.year
    else:
        return today.year + 1


def month_name_when_cadet_committee_age_bracket_begins():
    ARBITRARY_YEAR = 1990
    return datetime.date(
        ARBITRARY_YEAR, MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, 1
    ).strftime("%B")
