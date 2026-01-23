from typing import List, Union

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_VOLUNTEER_NAME,
    SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_VOLUNTEER_NAME,
)
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import object_definition_for_volunteers
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed, missing_data
from app.objects.volunteers import Volunteer, ListOfVolunteers, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, \
    SORT_BY_NAME_SIMILARITY


def get_volunteer_with_matching_name(
    object_store: ObjectStore, volunteer: Volunteer, default=missing_data
) -> Union[object, Volunteer]:
    return object_store.get(object_store.data_api.data_list_of_volunteers.get_matching_volunteer, volunteer=volunteer, default=default)


def get_volunteer_from_name(
    object_store: ObjectStore, volunteer_name: str
) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)

    return list_of_volunteers.volunteer_with_matching_name(volunteer_name)


def get_volunteer_from_id(object_store: ObjectStore, volunteer_id: str) -> Volunteer:
    return object_store.get(object_store.data_api.data_list_of_volunteers.get_volunteer_from_id, volunteer_id=volunteer_id)


def DEPRECATE_get_volunteer_from_list_of_given_str_of_volunteer(
    object_store: ObjectStore, volunteer_as_str: str, default=missing_data
) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)
    list_of_volunteers_as_str = DEPRECATE_get_list_of_volunteers_as_str(list_of_volunteers)
    try:
        volunteer_idx = list_of_volunteers_as_str.index(volunteer_as_str)
    except IndexError:
        return default

    return list_of_volunteers[volunteer_idx]


def DEPRECATE_get_list_of_volunteers_as_str(list_of_volunteers: ListOfVolunteers) -> List[str]:
    return [str(volunteer) for volunteer in list_of_volunteers]


def get_sorted_list_of_volunteers(
    object_store: ObjectStore,
    sort_by: str = arg_not_passed,
    similar_volunteer: Volunteer = arg_not_passed,
    exclude_volunteer: Volunteer = arg_not_passed,
) -> ListOfVolunteers:
    master_list = object_store.get(object_store.data_api.data_list_of_volunteers.read, sort_by=sort_by,
                                exclude_volunteer=exclude_volunteer)

    if sort_by == SORT_BY_SURNAME:
        return master_list ## already sorted
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list ## already sorted
    elif sort_by == SORT_BY_NAME_SIMILARITY:
        if similar_volunteer is arg_not_passed:
            raise Exception("Need to pass similar volunteer")
        return master_list.sort_by_similarity(volunteer=similar_volunteer)
    else:
        return master_list

def sort_list_of_volunteers(
    list_of_volunteers: ListOfVolunteers,
    sort_by: str = arg_not_passed,
    similar_volunteer: Volunteer = arg_not_passed,
) -> ListOfVolunteers:
    if sort_by == SORT_BY_SURNAME:
        return list_of_volunteers.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return list_of_volunteers.sort_by_firstname()
    elif sort_by == SORT_BY_NAME_SIMILARITY:
        if similar_volunteer is arg_not_passed:
            raise Exception("Need to pass similar volunteer")
        return list_of_volunteers.sort_by_similarity(volunteer=similar_volunteer)
    else:
        return list_of_volunteers




def list_of_similar_volunteers(
    object_store: ObjectStore, volunteer: Volunteer
) -> ListOfVolunteers:
    list_of_volunteers = get_list_of_volunteers(object_store)
    return list_of_volunteers.similar_volunteers(
        volunteer, name_threshold=SIMILARITY_LEVEL_TO_WARN_VOLUNTEER_NAME
    )


def list_of_very_similar_volunteers(
    object_store: ObjectStore, volunteer: Volunteer
) -> ListOfVolunteers:
    list_of_volunteers = get_list_of_volunteers(object_store)
    return list_of_volunteers.similar_volunteers(
        volunteer, name_threshold=SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_VOLUNTEER_NAME
    )


def single_very_similar_volunteer_or_missing_data(
    object_store: ObjectStore, volunteer: Volunteer
) -> Volunteer:
    very_similar_volunteers = list_of_very_similar_volunteers(object_store, volunteer)
    if len(very_similar_volunteers) == 1:
        return very_similar_volunteers[0]

    return missing_data

def delete_volunteer(interface: abstractInterface, volunteer: Volunteer, areyousure=False):
    if not areyousure:
        return
    try:
        interface.update(interface.object_store.data_api.data_list_of_volunteers.delete_volunteer, volunteer=volunteer)
    except Exception as e:
        interface.log_error("Error when deleting %s: %s" % (volunteer, str(e)))


def get_list_of_volunteers(object_store: ObjectStore) -> ListOfVolunteers:
    return object_store.get(object_store.data_api.data_list_of_volunteers.read)

