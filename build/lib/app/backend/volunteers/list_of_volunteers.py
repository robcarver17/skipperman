from typing import List

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import object_definition_for_volunteers
from app.objects.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer, ListOfVolunteers


def get_volunteer_from_id(object_store: ObjectStore, volunteer_id: str) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)
    return list_of_volunteers.object_with_id(volunteer_id)


def get_volunteer_from_list_of_given_str_of_volunteer(
    object_store: ObjectStore, volunteer_as_str: str
) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers(object_store)
    list_of_volunteers_as_str = get_list_of_volunteers_as_str(list_of_volunteers)
    volunteer_idx = list_of_volunteers_as_str.index(volunteer_as_str)

    return list_of_volunteers[volunteer_idx]


def get_list_of_volunteers_as_str(list_of_volunteers: ListOfVolunteers) -> List[str]:
    return [str(volunteer) for volunteer in list_of_volunteers]


def get_sorted_list_of_volunteers(
    object_store: ObjectStore, sort_by: str = arg_not_passed
) -> ListOfVolunteers:
    master_list = get_list_of_volunteers(object_store)
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    else:
        return master_list


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
