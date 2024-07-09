from typing import List, Dict, Union

from app.data_access.storage_layer.api import DataLayer

from app.data_access.configuration.configuration import UNABLE_TO_VOLUNTEER_KEYWORD
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.patrol_boats import PatrolBoatsData
from app.backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.backend.data.volunteer_allocation import VolunteerAllocationData
from app.backend.data.volunteers import VolunteerData, SORT_BY_FIRSTNAME
from app.backend.volunteers.volunteer_rota import (
    get_volunteer_at_event,
    delete_role_at_event_for_volunteer_on_day,
    DEPRECATE_load_list_of_volunteers_at_event,
)

from app.backend.cadets import cadet_name_from_id
from app.backend.volunteers.volunteers import (
    list_of_similar_volunteers,
    are_all_cadet_ids_in_list_already_connection_to_volunteer,
    get_volunteer_from_id,
)
from app.backend.wa_import.update_cadets_at_event import get_cadet_at_event_for_cadet_id
from app.backend.volunteers.volunter_relevant_information import (
    get_relevant_information_for_volunteer_in_event_at_row_and_index,
    suggested_volunteer_availability,
)

from app.objects.constants import missing_data
from app.objects.day_selectors import Day, DaySelector, union_across_day_selectors
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)

# from app.objects.food import FoodRequirements
from app.objects.utils import union_of_x_and_y, in_x_not_in_y, we_are_not_the_same
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_at_event import (
    VolunteerAtEventWithId,
    ListOfIdentifiedVolunteersAtEvent,
)


def add_identified_volunteer(
    interface: abstractInterface,
    volunteer_id: str,
    event: Event,
    row_id: str,
    volunteer_index: int,
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_identified_volunteer(
        row_id=row_id,
        volunteer_index=volunteer_index,
        volunteer_id=volunteer_id,
        event=event,
    )


def list_of_identified_volunteers_with_volunteer_id(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> ListOfIdentifiedVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    list_of_volunteers = (
        volunteer_allocation_data.load_list_of_identified_volunteers_at_event(event)
    )
    return list_of_volunteers.list_of_identified_volunteers_with_volunteer_id(
        volunteer_id
    )


def add_volunteer_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_at_event: VolunteerAtEventWithId,
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_at_event(
        event=event, volunteer_at_event=volunteer_at_event
    )


def volunteer_ids_associated_with_cadet_at_specific_event(
    interface: abstractInterface, event: Event, cadet_id: str
) -> list:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return (
        volunteer_allocation_data.volunteer_ids_associated_with_cadet_at_specific_event(
            event=event, cadet_id=cadet_id
        )
    )


def get_list_of_relevant_volunteers(
    interface: abstractInterface,
    volunteer: Volunteer,
    cadet_id: str,  ## could be missing data
) -> list:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(
        interface=interface, volunteer=volunteer
    )
    if cadet_id is missing_data:
        list_of_volunteers_associated_with_cadet = []
    else:
        list_of_volunteers_associated_with_cadet = (
            get_list_of_volunteers_associated_with_cadet(
                interface=interface, cadet_id=cadet_id
            )
        )

    list_of_volunteers = union_of_x_and_y(
        list_of_volunteers_associated_with_cadet, list_of_volunteers_with_similar_name
    )

    return list_of_volunteers


def get_list_of_volunteers_associated_with_cadet(
    interface: abstractInterface, cadet_id: str
) -> list:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_list_of_volunteers_associated_with_cadet(cadet_id)


def mark_volunteer_as_skipped(
    interface: abstractInterface, event: Event, row_id: str, volunteer_index: int
):
    volunteer_data = VolunteerAllocationData(interface.data)
    volunteer_data.mark_volunteer_as_skipped(
        row_id=row_id, volunteer_index=volunteer_index, event=event
    )
    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()


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
    volunteer_at_event = get_volunteer_at_event(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [
        other_cadet_id
        for other_cadet_id in associated_cadets
        if other_cadet_id != cadet_id
    ]

    return associated_cadets_without_this_cadet


def update_volunteer_availability_at_event(
    interface: abstractInterface,
    volunteer_id: str,
    event: Event,
    availability: DaySelector,
):
    for day in event.weekdays_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(
                interface=interface, volunteer_id=volunteer_id, event=event, day=day
            )
        else:
            make_volunteer_unavailable_on_day(
                interface=interface, volunteer_id=volunteer_id, event=event, day=day
            )


def make_volunteer_available_on_day(
    interface: abstractInterface, volunteer_id: str, event: Event, day: Day
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.make_volunteer_available_on_day(
        event=event, day=day, volunteer_id=volunteer_id
    )


def make_volunteer_unavailable_on_day(
    interface: abstractInterface, volunteer_id: str, event: Event, day: Day
):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.make_volunteer_unavailable_on_day(
        event=event, day=day, volunteer_id=volunteer_id
    )
    ## also delete any associated roles for tidyness
    delete_role_at_event_for_volunteer_on_day(
        interface=interface, volunteer_id=volunteer_id, event=event, day=day
    )

    ### and patrol boat data
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.remove_volunteer_from_patrol_boat_on_day_at_event(
        event=event, volunteer_id=volunteer_id, day=day
    )


def get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[str]:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    active_cadet_ids_at_event = cadets_at_event_data.list_of_active_cadet_ids_at_event(
        event
    )

    unique_list_of_all_cadet_ids_for_volunteer = (
        get_unique_list_of_cadet_ids_in_mapped_event_data_given_identified_volunteer_id(
            interface=interface, volunteer_id=volunteer_id, event=event
        )
    )

    list_of_active_cadet_ids_for_volunteer = [
        cadet_id
        for cadet_id in unique_list_of_all_cadet_ids_for_volunteer
        if cadet_id in active_cadet_ids_at_event
    ]

    return list_of_active_cadet_ids_for_volunteer


def get_unique_list_of_cadet_ids_in_mapped_event_data_given_identified_volunteer_id(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[str]:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    identified_cadets_at_event = (
        cadets_at_event_data.get_list_of_identified_cadets_at_event(event)
    )

    relevant_identified_volunteers = (
        get_list_of_volunteers_identified_at_event_with_volunteer_id(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )

    list_of_all_cadet_ids_for_volunteer = [
        identified_cadets_at_event.cadet_id_given_row_id(identified_volunteer.row_id)
        for identified_volunteer in relevant_identified_volunteers
    ]

    unique_list_of_all_cadet_ids_for_volunteer = list(
        set(list_of_all_cadet_ids_for_volunteer)
    )

    return unique_list_of_all_cadet_ids_for_volunteer


def get_list_of_volunteers_identified_at_event_with_volunteer_id(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> ListOfIdentifiedVolunteersAtEvent:
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    all_identified_volunteers_at_event = (
        volunteers_at_event_data.load_list_of_identified_volunteers_at_event(event)
    )
    relevant_identified_volunteers = all_identified_volunteers_at_event.list_of_identified_volunteers_with_volunteer_id(
        volunteer_id
    )

    return relevant_identified_volunteers


def get_list_of_associated_cadet_id_for_volunteer_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> List[str]:
    volunteer_at_event = get_volunteer_at_event_with_id(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    currently_associated_cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    return currently_associated_cadet_ids


def volunteer_for_this_row_and_index_already_identified(
    interface: abstractInterface, event: Event, row_id: str, volunteer_index: int
) -> bool:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)

    return (
        volunteer_allocation_data.volunteer_for_this_row_and_index_already_identified(
            event=event, row_id=row_id, volunteer_index=volunteer_index
        )
    )


def update_cadet_connections_when_volunteer_already_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    list_of_associated_cadet_id_in_mapped_data = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    currently_associated_cadet_ids_in_volunteer_allocation_data = (
        get_list_of_associated_cadet_id_for_volunteer_at_event(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )
    new_cadet_ids = in_x_not_in_y(
        x=list_of_associated_cadet_id_in_mapped_data,
        y=currently_associated_cadet_ids_in_volunteer_allocation_data,
    )

    update_cadet_connections_for_volunteer_with_list_of_cadet_ids(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        list_of_new_cadet_ids=new_cadet_ids,
    )


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


def get_volunteer_at_event_with_id(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> VolunteerAtEventWithId:
    list_of_volunteers_at_event = DEPRECATE_load_list_of_volunteers_at_event(
        interface=interface, event=event
    )
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(
        volunteer_id
    )

    return volunteer_at_event


def are_all_connected_cadets_cancelled_or_deleted(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> bool:
    list_of_relevant_information = get_list_of_relevant_information(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    return list_of_relevant_information.all_cancelled_or_deleted()


def is_current_cadet_active_at_event(
    interface: abstractInterface, cadet_id: str, event: Event
) -> bool:
    cadet_at_event = get_cadet_at_event_for_cadet_id(
        interface=interface, event=event, cadet_id=cadet_id
    )

    return cadet_at_event.is_active()


def get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
    interface: abstractInterface, cadet_id: str, event: Event
) -> Dict[str, str]:
    ## list of volunteers at event
    list_of_volunteers_ids = volunteer_ids_associated_with_cadet_at_specific_event(
        event=event, cadet_id=cadet_id, interface=interface
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


def are_any_volunteers_associated_with_cadet_at_event(
    interface: abstractInterface, cadet_id: str, event: Event
):
    dict_of_relevant_volunteers = (
        get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
            interface=interface, cadet_id=cadet_id, event=event
        )
    )

    return len(dict_of_relevant_volunteers) > 0


def get_list_of_relevant_information(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> ListOfRelevantInformationForVolunteer:
    list_of_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(
        interface=interface, volunteer_id=volunteer_id, event=event
    )  ## can appear more than once

    list_of_relevant_information = [
        get_relevant_information_for_volunteer_in_event_at_row_and_index(
            interface=interface,
            row_id=identified_volunteer.row_id,
            volunteer_index=identified_volunteer.volunteer_index,
            event=event,
        )
        for identified_volunteer in list_of_identified_volunteers
    ]

    return ListOfRelevantInformationForVolunteer(list_of_relevant_information)


def get_list_of_volunteers_except_those_already_at_event(
    interface: abstractInterface, event: Event
) -> ListOfVolunteers:
    volunteer_data = VolunteerAllocationData(interface.data)
    return volunteer_data.get_sorted_list_of_volunteers_except_those_already_at_event(
        event, SORT_BY_FIRSTNAME
    )


def get_volunteer_with_matching_name(
    data_layer: DataLayer, volunteer: Volunteer
) -> Union[object, Volunteer]:
    volunteer_data = VolunteerData(data_layer)
    matched_volunteer_with_id = volunteer_data.get_volunteer_with_matching_name(
        volunteer
    )

    return matched_volunteer_with_id


NO_ISSUES_WITH_VOLUNTEER = ""


def relevant_information_requires_clarification_or_cadets_not_permanently_connected(
    interface: abstractInterface,
    event: Event,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_id: str,
) -> str:
    issues = NO_ISSUES_WITH_VOLUNTEER
    volunteer_name = get_volunteer_from_id(
        interface=interface, volunteer_id=volunteer_id
    )

    list_of_status = [
        relevant_information.identify.self_declared_status
        for relevant_information in list_of_relevant_information
    ]
    list_of_preferred = [
        relevant_information.availability.preferred_duties
        for relevant_information in list_of_relevant_information
    ]
    list_of_availability = [
        suggested_volunteer_availability(relevant_information.availability)
        for relevant_information in list_of_relevant_information
    ]
    list_of_cadet_availability = [
        relevant_information.availability.cadet_availability
        for relevant_information in list_of_relevant_information
    ]

    list_of_same_or_different = [
        relevant_information.availability.same_or_different
        for relevant_information in list_of_relevant_information
    ]

    any_status_is_unable = any(
        [
            status
            for status in list_of_status
            if UNABLE_TO_VOLUNTEER_KEYWORD in status.lower()
        ]
    )
    availability_conflict = we_are_not_the_same(list_of_availability)
    if availability_conflict:
        ## cannot check so say false
        cadet_vs_volunteer_availability_conflict = False
    else:
        volunteer_availability = list_of_availability[0]  ## all the same
        cadet_vs_volunteer_availability_conflict = (
            is_volunteer_available_on_days_when_cadet_not_attending(
                volunteer_availability=volunteer_availability,
                list_of_cadet_availability=list_of_cadet_availability,
            )
        )

    preferred_conflict = we_are_not_the_same(list_of_preferred)
    same_or_different_conflict = we_are_not_the_same(list_of_same_or_different)
    cadets_not_connected = any_cadets_not_permanently_connected(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    if any_status_is_unable:
        issues += (
            "Volunteer %s is unable to volunteer according to at least one registration. "
            % volunteer_name
        )
    if availability_conflict:
        issues += (
            "Inconsistency between availability for cadet and volunteer %s across registrations. "
            % volunteer_name
        )
    if cadet_vs_volunteer_availability_conflict:
        issues += (
            "Volunteer %s is available on days when cadet is not. " % volunteer_name
        )
    if preferred_conflict:
        issues += (
            "Inconsistency on preferred duties across registrations for volunter %s . "
            % volunteer_name
        )
    if same_or_different_conflict:
        issues += (
            "Inconsistency on same/different duties across registrations for volunteer %s . "
            % volunteer_name
        )
    if cadets_not_connected:
        issues += (
            "Volunteer %s is not currently permanently connected to all registered cadets. "
            % volunteer_name
        )

    return issues


def is_volunteer_available_on_days_when_cadet_not_attending(
    volunteer_availability: DaySelector, list_of_cadet_availability: List[DaySelector]
) -> bool:
    all_cadets_availability = union_across_day_selectors(list_of_cadet_availability)
    for day in volunteer_availability.days_available():
        if not all_cadets_availability.available_on_day(day):
            return True

    return False


def any_cadets_not_permanently_connected(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)

    already_all_connected = are_all_cadet_ids_in_list_already_connection_to_volunteer(
        interface=interface, volunteer=volunteer, list_of_cadet_ids=list_of_cadet_ids
    )

    return not already_all_connected


def get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_id: str,
    list_of_associated_cadet_id: List[str],
) -> VolunteerAtEventWithId:
    first_relevant_information = list_of_relevant_information[
        0
    ]  ## can use first as all the same - checked
    return VolunteerAtEventWithId(
        volunteer_id=volunteer_id,
        availablity=suggested_volunteer_availability(
            first_relevant_information.availability
        ),
        list_of_associated_cadet_id=list_of_associated_cadet_id,
        preferred_duties=first_relevant_information.availability.preferred_duties,
        same_or_different=first_relevant_information.availability.same_or_different,
        any_other_information=get_any_other_information_joint_string(
            list_of_relevant_information
        ),
    )


def get_any_other_information_joint_string(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    list_of_other_information = [
        relevant_information.availability.any_other_information
        for relevant_information in list_of_relevant_information
    ]
    unique_list = list(set(list_of_other_information))

    return ". ".join(unique_list)
