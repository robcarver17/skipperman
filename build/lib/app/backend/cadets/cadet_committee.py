import datetime
from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.committee import earliest_and_latest_date_to_join_committee, \
    get_next_year_for_cadet_committee_after_EGM
from app.objects.membership_status import current_member

from app.backend.cadets.list_of_cadets import  get_sorted_list_of_cadets
from app.objects.composed.committee import ListOfCadetsOnCommittee

from app.objects.cadets import Cadet, ListOfCadets

from app.data_access.store.object_store import ObjectStore
from app.objects.utilities.exceptions import MissingData


def get_list_of_cadets_who_are_members_but_not_on_committee_or_elected_ordered_by_name(
    object_store: ObjectStore,
) -> ListOfCadets:
    all_cadets = get_sorted_list_of_cadets(object_store)
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
    list_of_cadets = get_sorted_list_of_cadets(object_store)

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



def delete_cadet_from_committee_data(
    interface: abstractInterface, cadet: Cadet, areyousure=False
) -> bool:
    if not areyousure:
        raise Exception("Have to be sure to delete")

    try:
        interface.update(
            interface.object_store.data_api.data_list_of_cadets_on_committee.delete_cadet_from_committee_data,
            cadet_id=cadet.id
        )
        cadet_was_on_commmittee = True
    except MissingData:
        cadet_was_on_commmittee = False

    except Exception as e:
        interface.log_error("Error %s when deleting cadet committee member %s" % (str(e), str(cadet)))
        return  False

    return cadet_was_on_commmittee


## STORAGE
def get_list_of_cadets_currently_serving(object_store: ObjectStore) -> ListOfCadets:
    list_of_cadets_on_committee = get_list_of_cadets_on_committee(object_store)

    return list_of_cadets_on_committee.list_of_cadets_currently_serving()


def get_list_of_cadets_on_committee(
    object_store: ObjectStore,
) -> ListOfCadetsOnCommittee:
    return object_store.get(object_store.data_api.data_list_of_cadets_on_committee.get_list_of_cadets_on_committee)





