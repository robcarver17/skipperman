from app.backend.club_boats.volunteer_with_club_dinghies import (
    get_dict_of_volunteers_and_club_dinghies_at_event,
    copy_club_dinghy_for_instructor_across_list_of_days_allow_overwrite,
)
from app.backend.food.modify_food_data import remove_food_requirements_for_volunteer_at_event
from app.backend.patrol_boats.changes import delete_volunteer_from_patrol_boat_on_all_days_of_event, \
    delete_volunteer_from_patrol_boat_on_day_at_event
from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
    get_attendance_matrix_for_list_of_volunteers_at_event,
)
from app.backend.rota.changes import delete_role_at_event_for_volunteer_on_day, \
    delete_role_at_event_for_volunteer_across_all_days
from app.backend.volunteers.relevant_information_for_volunteer import (
    check_any_status_is_unable,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import ListOfCadets
from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.volunteers_at_event_with_registration_data import (
    RegistrationDataForVolunteerAtEvent,
)

from app.objects.day_selectors import DaySelector, Day
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.objects.utilities.utils import simplify_and_display
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId
from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore


def get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies(
    object_store: ObjectStore, event: Event, day: Day
) -> ListOfVolunteers:
    club_dinghies = get_dict_of_volunteers_and_club_dinghies_at_event(
        object_store=object_store, event=event
    )
    list_of_volunteers_on_day_currently_allocated_to_club_dinghy = (
        club_dinghies.list_of_volunteers_on_day_currently_allocated_to_any_club_dinghy(
            day
        )
    )
    availablity_matrix = get_attendance_matrix_for_list_of_volunteers_at_event(
        object_store=object_store,
        event=event,
    )
    new_list = []
    for volunteer, availablity in availablity_matrix.items():
        if availablity.available_on_day(day):
            if (
                volunteer
                not in list_of_volunteers_on_day_currently_allocated_to_club_dinghy
            ):
                new_list.append(volunteer)

    list_of_volunteers = ListOfVolunteers(new_list)

    return list_of_volunteers.sort_by_firstname()


def copy_club_dinghy_for_instructor_across_all_days_attending_allow_overwrite(
    interface: abstractInterface,
    event: Event,
    club_dinghy: ClubDinghy,
    volunteer: Volunteer,
):
    attendance = get_attendance_matrix_for_list_of_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    attendance_for_volunteer = attendance[volunteer]
    list_of_days = attendance_for_volunteer.days_that_intersect_with(
        event.day_selector_for_days_in_event()
    )
    copy_club_dinghy_for_instructor_across_list_of_days_allow_overwrite(
        interface=interface,
        event=event,
        volunteer=volunteer,
        list_of_days=list_of_days,
        club_dinghy=club_dinghy,
    )


def add_volunteer_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    registration_data: RegistrationDataForVolunteerAtEvent,
):
    volunteer_at_event_with_id = VolunteerAtEventWithId(
        volunteer_id=volunteer.id,
        availablity=registration_data.availablity,
        list_of_associated_cadet_id=registration_data.list_of_associated_cadets.list_of_ids,
        any_other_information=registration_data.any_other_information,
        notes=registration_data.notes,
        preferred_duties=registration_data.preferred_duties,
        same_or_different=registration_data.same_or_different,
        self_declared_status=registration_data.self_declared_status,
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.add_volunteer_to_event,
        volunteer_at_event_with_id=volunteer_at_event_with_id,
        event_id=event.id,
    )


def get_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, event: Event
) -> DictOfAllEventDataForVolunteers:
    return object_store.get(
        object_store.data_api.dict_of_all_event_data_for_volunteers.get_dict_of_all_event_info_for_volunteers,
        event=event,
    )


def get_volunteer_registration_data_from_list_of_relevant_information(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    list_of_associated_cadets: ListOfCadets,
    any_issues: bool,
) -> RegistrationDataForVolunteerAtEvent:
    if any_issues:
        return get_volunteer_registration_data_from_list_of_relevant_information_with_conflicts(
            list_of_relevant_information=list_of_relevant_information,
            list_of_associated_cadets=list_of_associated_cadets,
        )
    else:
        return get_volunteer_registration_data_from_list_of_relevant_information_with_no_conflicts(
            list_of_relevant_information=list_of_relevant_information,
            list_of_associated_cadets=list_of_associated_cadets,
        )


def get_volunteer_registration_data_from_list_of_relevant_information_with_conflicts(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    list_of_associated_cadets: ListOfCadets,
) -> RegistrationDataForVolunteerAtEvent:
    return RegistrationDataForVolunteerAtEvent(
        availablity=merge_availability(list_of_relevant_information),
        list_of_associated_cadets=list_of_associated_cadets,
        preferred_duties=merge_preferred_duties(list_of_relevant_information),
        same_or_different=merge_same_or_different(list_of_relevant_information),
        self_declared_status=merge_self_declared_status(list_of_relevant_information),
        any_other_information=merge_other_information(list_of_relevant_information),
    )


def get_volunteer_registration_data_from_list_of_relevant_information_with_no_conflicts(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    list_of_associated_cadets: ListOfCadets,
) -> RegistrationDataForVolunteerAtEvent:
    first_relevant_information = list_of_relevant_information[
        0
    ]  ## can use first as all the same - checked

    ### we should never get here since a status of unavailable will throw out an error but hey ho
    availability = get_availablity_given_status(
        first_relevant_information.availability.volunteer_availablity,
        list_of_relevant_information=list_of_relevant_information,
    )

    return RegistrationDataForVolunteerAtEvent(
        availablity=availability,
        list_of_associated_cadets=list_of_associated_cadets,
        preferred_duties=first_relevant_information.availability.preferred_duties,
        same_or_different=first_relevant_information.availability.same_or_different,
        self_declared_status=first_relevant_information.identify.self_declared_status,
        any_other_information=merge_other_information(
            list_of_relevant_information
        ),  ## only one not checked for uniqueness
    )


def merge_availability(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> DaySelector:
    all_availability = [
        relevant_information.availability.volunteer_availablity
        for relevant_information in list_of_relevant_information
    ]
    availability = DaySelector.create_empty()
    for item_available in all_availability:
        availability = availability.union(item_available)

    availability = get_availablity_given_status(
        availability, list_of_relevant_information
    )

    return availability


def merge_preferred_duties(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    return merge_string(
        list_of_relevant_information, "availability", "preferred_duties"
    )


def merge_same_or_different(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    return merge_string(
        list_of_relevant_information, "availability", "same_or_different"
    )


def merge_self_declared_status(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    return merge_string(
        list_of_relevant_information, "identify", "self_declared_status"
    )


def merge_other_information(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    return merge_string(
        list_of_relevant_information,
        first_item="details",
        second_item="any_other_information",
        linker=", ",
    )


def get_availablity_given_status(
    availability: DaySelector,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
):
    if check_any_status_is_unable(
        list_of_relevant_information=list_of_relevant_information
    ):
        return availability.create_empty()
    else:
        return availability


def merge_string(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    first_item: str,
    second_item: str,
    linker: str = " OR ",
) -> str:
    list_of_strings = [
        getattr(getattr(relevant_information, first_item), second_item)
        for relevant_information in list_of_relevant_information
    ]

    return simplify_and_display(list_of_strings, linker=linker)


def load_list_of_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteers:
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    return registration_data.list_of_volunteers_at_event()


def update_volunteer_availability_at_event(
    interface: abstractInterface,
    volunteer: Volunteer,
    event: Event,
    availability: DaySelector,
):
    for day in event.days_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(
                interface=interface, event=event, volunteer=volunteer, day=day
            )
        else:
            make_volunteer_unavailable_on_day(
                interface=interface, event=event, volunteer=volunteer, day=day
            )


def make_volunteer_available_on_day(
    interface: abstractInterface, volunteer: Volunteer, event: Event, day: Day
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.make_volunteer_available_on_day,
        volunteer_id=volunteer.id,
        event_id=event.id,
        day=day,
    )




def make_volunteer_unavailable_on_day(
    interface: abstractInterface, volunteer: Volunteer, event: Event, day: Day
): ## ALSO NEED TO DO PATROL BOATS
    delete_volunteer_from_patrol_boat_on_day_at_event(interface=interface, event=event, day=day, volunteer=volunteer)
    remove_volunteer_from_event_data_on_day(interface=interface, event=event, day=day, volunteer=volunteer)
    delete_role_at_event_for_volunteer_on_day(interface=interface, event=event, day=day, volunteer=volunteer)

def remove_volunteer_from_event_data_on_day(
    interface: abstractInterface, volunteer: Volunteer, event: Event, day: Day
): ## ALSO NEED TO DO PATROL BOATS
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.make_volunteer_unavailable_on_day,
        volunteer_id=volunteer.id,
        event_id=event.id,
        day=day,
    )



def remove_volunteer_from_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    delete_volunteer_from_event_data(interface=interface, event=event,volunteer=volunteer)
    remove_food_requirements_for_volunteer_at_event(interface=interface, event=event,volunteer=volunteer)
    delete_volunteer_from_patrol_boat_on_all_days_of_event(interface=interface, event=event, volunteer=volunteer)
    delete_role_at_event_for_volunteer_across_all_days(interface=interface, event=event, volunteer=volunteer)
    return ""

def delete_volunteer_from_event_data(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.delete_volunteer_at_event,
        volunteer_id=volunteer.id,
        event_id=event.id,
    )
