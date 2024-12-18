from typing import List, Dict

from app.data_access.store.data_access import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData
from app.OLD_backend.data.volunteers import VolunteerData
from app.OLD_backend.rota.volunteer_rota import (
    DEPRECATE_load_list_of_volunteers_at_event,
)

from app.OLD_backend.cadets import cadet_name_from_id, get_cadet_from_id
from app.OLD_backend.volunteers.volunteers import (
    DEPRECATE_get_volunteer_from_id,
)
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event
from app.objects.cadets import ListOfCadets, Cadet

from app.objects.events import Event

# from app.objects_OLD.food import FoodRequirements
from app.objects.volunteers import Volunteer
from app.objects_OLD.volunteers_at_event import (
    DEPRECATE_VolunteerAtEvent,
)
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId


def DEPRECATE_get_volunteer_ids_associated_with_cadet_at_specific_event(
    interface: abstractInterface, event: Event, cadet_id: str
) -> list:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return (
        volunteer_allocation_data.volunteer_ids_associated_with_cadet_at_specific_event(
            event=event, cadet_id=cadet_id
        )
    )


def get_volunteer_ids_associated_with_cadet_at_specific_event(
    data_layer: DataLayer, event: Event, cadet_id: str
) -> list:
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    return (
        volunteer_allocation_data.volunteer_ids_associated_with_cadet_at_specific_event(
            event=event, cadet_id=cadet_id
        )
    )


def get_volunteer_name_and_associated_cadets_for_event(
    interface: abstractInterface, event: Event, volunteer_id: str, cadet_id: str
) -> str:
    volunteer_data = VolunteerData(interface.data)
    list_of_all_volunteers = volunteer_data.get_list_of_volunteers()
    volunteer_name = str(list_of_all_volunteers.object_with_id(volunteer_id))

    other_cadets = get_string_of_other_associated_cadets_for_event(
        interface=interface, event=event, volunteer_id=volunteer_id, cadet_id=cadet_id
    )

    return volunteer_name + other_cadets


def get_string_of_other_associated_cadets_for_event(
    interface: abstractInterface, event: Event, volunteer_id: str, cadet_id: str
) -> str:
    associated_cadets_without_this_cadet = (
        get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
            interface=interface,
            event=event,
            volunteer_id=volunteer_id,
            cadet_id=cadet_id,
        )
    )

    if len(associated_cadets_without_this_cadet) == 0:
        return ""

    associated_cadets_without_this_cadet_names = [
        cadet_name_from_id(data_layer=interface.data, cadet_id=other_cadet_id)
        for other_cadet_id in associated_cadets_without_this_cadet
    ]
    associated_cadets_without_this_cadet_names_str = ", ".join(
        associated_cadets_without_this_cadet_names
    )

    return (
        "(Other registered group_allocations associated with this volunteer: "
        + associated_cadets_without_this_cadet_names_str
        + " )"
    )


def any_other_cadets_for_volunteer_at_event_apart_from_this_one(
    interface: abstractInterface, event: Event, volunteer_id: str, cadet_id: str
) -> bool:
    associated_cadets_without_this_cadet = (
        get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
            interface=interface,
            event=event,
            volunteer_id=volunteer_id,
            cadet_id=cadet_id,
        )
    )

    return len(associated_cadets_without_this_cadet) > 0


def get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
    interface: abstractInterface, event: Event, volunteer_id: str, cadet_id: str
) -> List[str]:
    volunteer_at_event = DEPRECATE_get_volunteer_at_event_with_id(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [
        other_cadet_id
        for other_cadet_id in associated_cadets
        if other_cadet_id != cadet_id
    ]

    return associated_cadets_without_this_cadet


def get_list_of_associated_cadet_id_for_volunteer_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[str]:
    volunteer_at_event = DEPRECATE_get_volunteer_at_event_with_id(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    currently_associated_cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    return currently_associated_cadet_ids


def update_cadet_connections_for_volunteer_with_list_of_cadet_ids(
    interface: abstractInterface,
    event: Event,
    volunteer_id: str,
    list_of_new_cadet_ids: List[str],
):
    volunteer_data = VolunteerAllocationData(interface.data)

    for cadet_id in list_of_new_cadet_ids:
        print(
            "Adding association with cadet %s to existing volunteer %s"
            % (cadet_id, volunteer_id)
        )
        volunteer_data.add_cadet_id_to_existing_volunteer(
            cadet_id=cadet_id, volunteer_id=volunteer_id, event=event
        )


def is_current_cadet_active_at_event(
    interface: abstractInterface, cadet_id: str, event: Event
) -> bool:
    cadet_at_event = get_cadet_at_event(
        interface=interface, event=event, cadet_id=cadet_id
    )

    return cadet_at_event.is_active()


def get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
    interface: abstractInterface, cadet_id: str, event: Event
) -> Dict[str, str]:
    ## list of volunteers at event
    list_of_volunteers_ids = (
        DEPRECATE_get_volunteer_ids_associated_with_cadet_at_specific_event(
            event=event, cadet_id=cadet_id, interface=interface
        )
    )
    list_of_relevant_volunteer_names_and_other_cadets = [
        get_volunteer_name_and_associated_cadets_for_event(
            interface=interface,
            event=event,
            volunteer_id=volunteer_id,
            cadet_id=cadet_id,
        )
        for volunteer_id in list_of_volunteers_ids
    ]

    return dict(
        [volunteer_and_any_other_cadets, id]
        for volunteer_and_any_other_cadets, id in zip(
            list_of_relevant_volunteer_names_and_other_cadets, list_of_volunteers_ids
        )
    )


def get_list_of_connected_cadets_given_volunteer_at_event(
    data_layer: DataLayer, volunteer_at_event: VolunteerAtEventWithId
) -> ListOfCadets:
    cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    connected_cadets = ListOfCadets(
        [
            get_cadet_from_id(data_layer=data_layer, cadet_id=cadet_id)
            for cadet_id in cadet_ids
        ]
    )

    return connected_cadets


def remove_volunteer_and_cadet_association_at_event(
    data_layer: DataLayer, event: Event, volunteer: Volunteer, cadet: Cadet
):
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    volunteer_allocation_data.remove_volunteer_and_cadet_association_at_event(
        event=event, volunteer=volunteer, cadet=cadet
    )


def add_volunteer_and_cadet_association_for_existing_volunteer(
    data_layer: DataLayer, event: Event, cadet: Cadet, volunteer: Volunteer
):
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    volunteer_allocation_data.add_volunteer_and_cadet_association_for_existing_volunteer(
        event=event, volunteer=volunteer, cadet=cadet
    )


def get_volunteer_at_event(
    data_layer: DataLayer, volunteer_id: str, event: Event
) -> DEPRECATE_VolunteerAtEvent:
    volunteer_at_event_with_id = get_volunteer_at_event_with_id(
        data_layer=data_layer, event=event, volunteer_id=volunteer_id
    )
    volunteer_data = VolunteerData(data_layer)
    volunteer = volunteer_data.volunteer_with_id(volunteer_id=volunteer_id)

    return DEPRECATE_VolunteerAtEvent.from_volunteer_and_voluteer_at_event_with_id(
        volunteer=volunteer,
        volunteer_at_event_with_id=volunteer_at_event_with_id,
        event=event,
    )


def DEPRECATE_get_volunteer_at_event_with_id(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> VolunteerAtEventWithId:
    list_of_volunteers_at_event = DEPRECATE_load_list_of_volunteers_at_event(
        interface=interface, event=event
    )
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(
        volunteer_id
    )

    return volunteer_at_event


def get_volunteer_at_event_with_id(
    data_layer: DataLayer, event: Event, volunteer_id: str
) -> VolunteerAtEventWithId:
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    return volunteer_allocation_data.get_volunteer_at_this_event(
        event=event, volunteer_id=volunteer_id
    )


def DEPRECATE_get_list_of_volunteer_names_associated_with_cadet_at_event(
    interface: abstractInterface, cadet_id: str, event: Event
):
    list_of_volunteer_ids = (
        DEPRECATE_get_volunteer_ids_associated_with_cadet_at_specific_event(
            interface=interface, event=event, cadet_id=cadet_id
        )
    )
    volunteer_names = [
        DEPRECATE_get_volunteer_from_id(
            interface=interface, volunteer_id=volunteer_id
        ).name
        for volunteer_id in list_of_volunteer_ids
    ]

    return volunteer_names


