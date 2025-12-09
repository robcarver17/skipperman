from typing import List, Union

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)

from app.backend.registration_data.cadet_registration_data import (
    get_list_of_active_cadets_at_event,
)
from app.backend.registration_data.identified_cadets_at_event import (
    get_list_of_identified_cadets_at_event,
)
from app.backend.registration_data.identified_volunteers_at_event import (
    list_of_identified_volunteers_with_volunteer_id,
    get_list_of_relevant_information_for_volunteer_in_registration_data,
)
from app.backend.volunteers.connected_cadets import (
    get_list_of_cadets_associated_with_volunteer,
    add_list_of_cadets_to_volunteer_connection,
    is_cadet_already_associated_with_volunteer,
    get_list_of_volunteers_associated_with_cadet,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.events import Event
from app.objects.groups import Group, sorted_locations
from app.objects.utilities.utils import in_x_not_in_y, in_both_x_and_y
from app.objects.volunteers import Volunteer, ListOfVolunteers


def are_all_cadets_in_list_already_connection_to_volunteer(
    object_store: ObjectStore, volunteer: Volunteer, list_of_cadets: ListOfCadets
) -> bool:
    list_of_already_connected = [
        is_cadet_already_associated_with_volunteer(
            object_store=object_store, volunteer=volunteer, cadet=cadet
        )
        for cadet in list_of_cadets
    ]

    return all(list_of_already_connected)


def update_cadet_connections_when_volunteer_already_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    list_of_associated_cadets_in_mapped_data = get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer(
        object_store=object_store, event=event, volunteer=volunteer
    )

    update_cadet_connections_for_volunteer_already_at_event_given_list_of_cadets(
        object_store=object_store,
        volunteer=volunteer,
        list_of_cadets_to_connect=list_of_associated_cadets_in_mapped_data,
    )


def update_cadet_connections_for_volunteer_already_at_event_given_list_of_cadets(
    object_store: ObjectStore,
    volunteer: Volunteer,
    list_of_cadets_to_connect: ListOfCadets,
):
    currently_connected_cadets = get_list_of_cadets_associated_with_volunteer(
        object_store=object_store, volunteer=volunteer
    )
    new_cadets = in_x_not_in_y(
        x=list_of_cadets_to_connect,
        y=currently_connected_cadets,
    )

    add_list_of_cadets_to_volunteer_connection(
        object_store=object_store,
        volunteer=volunteer,
        list_of_cadets=ListOfCadets(new_cadets),
    )


def get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> ListOfCadets:
    unique_list_of_all_cadet_ids_for_volunteer = (
        get_unique_list_of_cadet_ids_in_registration_data_given_identified_volunteer(
            object_store=object_store, event=event, volunteer=volunteer
        )
    )

    active_cadets = get_list_of_active_cadets_at_event(
        object_store=object_store, event=event
    )
    list_of_active_cadets_for_volunteer = [
        cadet
        for cadet in active_cadets
        if cadet.id in unique_list_of_all_cadet_ids_for_volunteer
    ]

    return ListOfCadets(list_of_active_cadets_for_volunteer)


def get_unique_list_of_cadet_ids_in_registration_data_given_identified_volunteer(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> List[str]:
    relevant_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(
        object_store=object_store, event=event, volunteer=volunteer
    )

    identified_cadets_at_event = get_list_of_identified_cadets_at_event(
        object_store=object_store, event=event
    )

    list_of_all_cadet_ids_for_volunteer = [
        identified_cadets_at_event.cadet_id_given_row_id_ignoring_all_skipped_cadets(
            identified_volunteer.row_id
        )
        for identified_volunteer in relevant_identified_volunteers
    ]

    unique_list_of_all_cadet_ids_for_volunteer = list(
        set(list_of_all_cadet_ids_for_volunteer)
    )

    return unique_list_of_all_cadet_ids_for_volunteer


def are_all_cadets_associated_with_volunteer_in_registration_data_cancelled_or_deleted(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> bool:
    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=object_store, volunteer=volunteer, event=event
        )
    )

    return list_of_relevant_information.all_cancelled_or_deleted()


def get_list_of_volunteers_associated_with_cadet_at_event(
    object_store: ObjectStore, cadet: Cadet, event: Event
):
    list_of_volunteers = get_list_of_volunteers_associated_with_cadet(
        object_store=object_store, cadet=cadet
    )
    volunteer_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers_at_event = (
        volunteer_data.dict_of_registration_data_for_volunteers_at_event.list_of_volunteers_at_event()
    )
    volunteers = [
        volunteer
        for volunteer in list_of_volunteers
        if volunteer in volunteers_at_event
    ]

    return ListOfVolunteers(volunteers)


def get_cadet_location_string_for_volunteer(
    dict_of_all_cadet_event_data: DictOfAllEventInfoForCadets,
    volunteer_data_at_event: AllEventDataForVolunteer,
):
    list_of_cadets_at_event_and_associated = (
        get_list_of_cadets_associated_with_volunteer_at_event_given_event_data(
            dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
            volunteer_data_at_event=volunteer_data_at_event,
        )
    )
    if len(list_of_cadets_at_event_and_associated) == 0:
        return "xx No associated sailor(s) at event"  ## trick to get at end of sort

    list_of_groups = list_of_cadet_groups_associated_with_volunteer(
        dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
        list_of_cadets_at_event_and_associated=list_of_cadets_at_event_and_associated,
    )
    if list_of_groups is no_cadets_allocated_to_groups_yet:
        return "x %d associated sailor(s) not in groups" % len(
            list_of_cadets_at_event_and_associated  ## same trick
        )
    else:
        return str_type_of_group_given_list_of_groups(list_of_groups)


def get_list_of_cadets_associated_with_volunteer_at_event_given_event_data(
    dict_of_all_cadet_event_data: DictOfAllEventInfoForCadets,
    volunteer_data_at_event: AllEventDataForVolunteer,
) -> ListOfCadets:
    cadets_at_event = dict_of_all_cadet_event_data.list_of_cadets
    asssociated_with_volunteer = volunteer_data_at_event.associated_cadets

    return ListOfCadets(in_both_x_and_y(cadets_at_event, asssociated_with_volunteer))


def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.location for group in list_of_groups]
    unique_list_of_group_locations = list(set(types_of_groups))
    sorted_list_of_group_locations = sorted_locations(unique_list_of_group_locations)
    sorted_list_of_group_locations = [
        location.name for location in sorted_list_of_group_locations
    ]

    return ", ".join(sorted_list_of_group_locations)


def list_of_cadet_groups_associated_with_volunteer(
    dict_of_all_cadet_event_data: DictOfAllEventInfoForCadets,
    list_of_cadets_at_event_and_associated: ListOfCadets,
) -> Union[List[Group], object]:
    list_of_groups = []
    for cadet in list_of_cadets_at_event_and_associated:
        list_of_groups += dict_of_all_cadet_event_data.dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        ).list_of_groups

    list_of_groups = list(set(list_of_groups))
    if len(list_of_groups) == 0:
        return no_cadets_allocated_to_groups_yet

    return list_of_groups


no_cadets_allocated_to_groups_yet = object()


def get_list_of_cadets_associated_with_volunteer_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    list_of_cadets = get_list_of_cadets_associated_with_volunteer(
        volunteer=volunteer, object_store=object_store
    )
    event_data_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    active_cadets_at_event = event_data_for_cadets.list_of_cadets
    list_of_cadets_at_event = [
        cadet for cadet in list_of_cadets if cadet in active_cadets_at_event
    ]

    return ListOfCadets(list_of_cadets_at_event)
