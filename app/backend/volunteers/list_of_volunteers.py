from typing import List, Union

from app.OLD_backend.data.volunteers import VolunteerData
from app.data_access.store.data_access import DataLayer

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import object_definition_for_volunteers
from app.objects.exceptions import arg_not_passed, missing_data
from app.objects.volunteers import Volunteer, ListOfVolunteers




def get_volunteer_with_matching_name(
        object_store: ObjectStore, volunteer: Volunteer
) -> Union[object, Volunteer]:
    list_of_volunteers = get_list_of_volunteers(object_store)

    return list_of_volunteers.volunteer_with_matching_name(volunteer)

def get_volunteer_from_id(object_store: ObjectStore, volunteer_id: str) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)
    return list_of_volunteers.object_with_id(volunteer_id)


def get_volunteer_from_list_of_given_str_of_volunteer(
    object_store: ObjectStore, volunteer_as_str: str, default = missing_data
) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)
    list_of_volunteers_as_str = get_list_of_volunteers_as_str(list_of_volunteers)
    try:
        volunteer_idx = list_of_volunteers_as_str.index(volunteer_as_str)
    except IndexError:
        return default

    return list_of_volunteers[volunteer_idx]


def get_list_of_volunteers_as_str(list_of_volunteers: ListOfVolunteers) -> List[str]:
    return [str(volunteer) for volunteer in list_of_volunteers]


def get_sorted_list_of_volunteers(
    object_store: ObjectStore, sort_by: str = arg_not_passed
) -> ListOfVolunteers:
    master_list = get_list_of_volunteers(object_store)
    return sort_list_of_volunteers(list_of_volunteers=master_list, sort_by=sort_by)

def sort_list_of_volunteers(list_of_volunteers: ListOfVolunteers,  sort_by: str = arg_not_passed) -> ListOfVolunteers:
    if sort_by is arg_not_passed:
        return list_of_volunteers
    if sort_by == SORT_BY_SURNAME:
        return list_of_volunteers.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return list_of_volunteers.sort_by_firstname()
    else:
        return list_of_volunteers


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"


def get_list_of_volunteers(object_store: ObjectStore) -> ListOfVolunteers:
    return object_store.get(object_definition_for_volunteers)


def update_list_of_volunteers(
    object_store: ObjectStore, list_of_volunteers: ListOfVolunteers
):
    object_store.update(
        new_object=list_of_volunteers,
        object_definition=object_definition_for_volunteers,
    )

