from copy import copy
from typing import List

from app.backend.volunteers.list_of_volunteers import list_of_similar_volunteers
from app.objects.utilities.exceptions import missing_data, arg_not_passed

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.utilities.cadet_matching_and_sorting import get_list_of_cadets_with_similar_surname
from app.objects.utilities.utils import union_of_x_and_y
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.composed.cadet_volunteer_associations import (
    ListOfCadetVolunteerAssociations,
    DictOfCadetsAssociatedWithVolunteer,
    DictOfVolunteersAssociatedWithCadet,
)

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_volunteer_and_cadet_associations,
    object_definition_for_dict_of_volunteers_associated_with_cadets,
    object_definition_for_dict_of_cadets_associated_with_volunteers,
)


def get_dict_of_cadets_associated_with_volunteers(
    object_store: ObjectStore,
) -> DictOfCadetsAssociatedWithVolunteer:
    return object_store.get(
        object_definition_for_dict_of_cadets_associated_with_volunteers
    )


def get_dict_of_volunteers_associated_with_cadets(
    object_store: ObjectStore,
) -> DictOfVolunteersAssociatedWithCadet:
    return object_store.get(
        object_definition_for_dict_of_volunteers_associated_with_cadets
    )


def get_list_of_similar_volunteers(
    object_store: ObjectStore,
    volunteer: Volunteer,
    cadet: Cadet = arg_not_passed,  ## could be missing data
) -> ListOfVolunteers:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(
        object_store=object_store, volunteer=volunteer
    )
    if (cadet is missing_data) or (cadet is arg_not_passed):
        list_of_volunteers_associated_with_cadet = []
    else:
        list_of_volunteers_associated_with_cadet = (
            get_list_of_volunteers_associated_with_cadet(
                object_store=object_store, cadet=cadet
            )
        )

    list_of_volunteers = union_of_x_and_y(
        list_of_volunteers_associated_with_cadet, list_of_volunteers_with_similar_name
    )

    return ListOfVolunteers(list_of_volunteers)


def get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first(
    volunteer: Volunteer, from_list_of_cadets: ListOfCadets
) -> ListOfCadets:
    similar_cadets = get_list_of_cadets_with_names_similar_to_volunteer(
        volunteer=volunteer, from_list_of_cadets=from_list_of_cadets
    )
    remaining_list_of_cadets = copy(from_list_of_cadets)
    list_of_similar_cadets_to_insert_at_front_of_list = []
    for cadet in similar_cadets:
        ## avoid double counting
        list_of_similar_cadets_to_insert_at_front_of_list.append(
            remaining_list_of_cadets.pop_cadet(cadet)
        )

    return ListOfCadets(
        list_of_similar_cadets_to_insert_at_front_of_list + remaining_list_of_cadets
    )


def get_list_of_cadets_with_names_similar_to_volunteer(
    volunteer: Volunteer, from_list_of_cadets: ListOfCadets
) -> ListOfCadets:

    similar_cadets = get_list_of_cadets_with_similar_surname(from_list_of_cadets, surname=volunteer.surname)
    similar_cadets = similar_cadets.sort_by_firstname()

    return similar_cadets


def is_cadet_already_associated_with_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, cadet: Cadet
) -> bool:
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    return (
        volunteer
        in list_of_cadet_volunteer_associations.list_of_volunteers_associated_with_cadet(
            cadet
        )
    )


def get_list_of_cadets_associated_with_volunteer(
    object_store: ObjectStore, volunteer: Volunteer
) -> ListOfCadets:
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    return (
        list_of_cadet_volunteer_associations.list_of_cadets_associated_with_volunteer(
            volunteer
        )
    )


def get_list_of_volunteers_associated_with_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> ListOfVolunteers:

    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    return (
        list_of_cadet_volunteer_associations.list_of_volunteers_associated_with_cadet(
            cadet
        )
    )


## UPDATES
def delete_cadet_connection(
    object_store: ObjectStore, cadet: Cadet, volunteer: Volunteer
):
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    list_of_cadet_volunteer_associations.delete_association(
        cadet=cadet, volunteer=volunteer
    )
    update_list_of_cadet_volunteer_association(
        list_of_cadet_volunteer_associations=list_of_cadet_volunteer_associations,
        object_store=object_store,
    )


def delete_all_connections_for_cadet(
    object_store: ObjectStore, cadet: Cadet, areyousure: bool =False
):
    if not areyousure:
        return

    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    list_of_associated_volunteers = list_of_cadet_volunteer_associations.delete_all_associations_for_cadet(cadet)
    update_list_of_cadet_volunteer_association(
        list_of_cadet_volunteer_associations=list_of_cadet_volunteer_associations,
        object_store=object_store,
    )

    return list_of_associated_volunteers



def delete_all_connections_for_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, areyousure: bool =False
):
    if not areyousure:
        return

    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    list_of_associated_cadets = list_of_cadet_volunteer_associations.delete_all_associations_for_volunteer(volunteer)
    update_list_of_cadet_volunteer_association(
        list_of_cadet_volunteer_associations=list_of_cadet_volunteer_associations,
        object_store=object_store,
    )

    return list_of_associated_cadets


def add_list_of_cadets_to_volunteer_connection(
    object_store: ObjectStore, volunteer: Volunteer, list_of_cadets: List[Cadet]
):
    for cadet in list_of_cadets:
        add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
            object_store=object_store, volunteer=volunteer, cadet=cadet
        )


def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
    object_store: ObjectStore, cadet: Cadet, volunteer: Volunteer
):
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_association(
        object_store
    )
    list_of_cadet_volunteer_associations.add_association(
        cadet=cadet, volunteer=volunteer
    )
    update_list_of_cadet_volunteer_association(
        list_of_cadet_volunteer_associations=list_of_cadet_volunteer_associations,
        object_store=object_store,
    )


## RAW DATA
def get_list_of_cadet_volunteer_association(
    object_store: ObjectStore,
) -> ListOfCadetVolunteerAssociations:
    return object_store.get(object_definition_for_volunteer_and_cadet_associations)


def update_list_of_cadet_volunteer_association(
    object_store: ObjectStore,
    list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations,
):
    object_store.update(
        new_object=list_of_cadet_volunteer_associations,
        object_definition=object_definition_for_volunteer_and_cadet_associations,
    )

