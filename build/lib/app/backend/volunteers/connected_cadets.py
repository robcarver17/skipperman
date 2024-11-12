import datetime
from copy import copy

from app.objects.membership_status import current_member

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.volunteers import Volunteer
from app.objects.composed.cadet_volunteer_associations import (
    ListOfCadetVolunteerAssociations,
)

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_volunteer_and_cadet_associations,
)


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
    volunteer_as_pseudo_cadet = Cadet(
        first_name=volunteer.first_name,
        surname=volunteer.surname,
        date_of_birth=datetime.date(1970, 1, 1),
        membership_status=current_member,
    )  ## so matching works

    similar_cadets = from_list_of_cadets.similar_surnames(volunteer_as_pseudo_cadet)
    similar_cadets = similar_cadets.sort_by_firstname()

    return similar_cadets


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
