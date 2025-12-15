from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
)
from app.backend.volunteers.relevant_information_for_volunteer import (
    check_any_status_is_unable,
)
from app.objects.cadet_attendance import DictOfDaySelectors
from app.objects.cadets import ListOfCadets
from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.volunteers_at_event_with_registration_data import (
    RegistrationDataForVolunteerAtEvent,
)

from app.objects.day_selectors import DaySelector, Day
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.utils import simplify_and_display
from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_all_event_data_for_volunteers,
    object_definition_for_list_of_volunteers_with_ids_at_event,
)


def get_list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
    object_store: ObjectStore, event: Event, day: Day, club_dinghy: ClubDinghy
) -> ListOfVolunteers:
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    return all_event_info.list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
        day=day, club_dinghy=club_dinghy
    )


def get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies(
    object_store: ObjectStore, event: Event, day: Day
) -> ListOfVolunteers:
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers = all_event_info.get_list_of_volunteers_at_event_on_day_not_currently_allocated_to_club_dinghies(
        day=day
    )
    return volunteers.sort_by_firstname()


def allocate_club_dinghy_to_volunteer_on_day(
    object_store: ObjectStore,
    event: Event,
    day: Day,
    volunteer: Volunteer,
    club_dinghy: ClubDinghy,
):
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    all_event_info.allocate_club_dinghy_to_volunteer_on_day(
        day=day, volunteer=volunteer, club_dinghy=club_dinghy
    )
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_event_info
    )


def remove_club_dinghy_from_volunteer_on_day(
    object_store: ObjectStore, event: Event, day: Day, volunteer: Volunteer
):
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    all_event_info.remove_club_dinghy_from_volunteer_on_day(
        day=day, volunteer=volunteer
    )

    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_event_info
    )


def copy_club_dinghy_for_instructor_across_all_days(
    object_store: ObjectStore,
    event: Event,
    day: Day,
    club_dinghy: ClubDinghy,
    volunteer: Volunteer,
):
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    all_event_info.copy_club_dinghy_for_instructor_across_all_days(
        day=day, volunteer=volunteer, club_dinghy=club_dinghy
    )

    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_event_info
    )


def get_attendance_matrix_for_list_of_volunteers_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_volunteers: ListOfVolunteers = arg_not_passed,
) -> DictOfDaySelectors:
    all_event_info = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    dict_of_availability = {}
    if list_of_volunteers is arg_not_passed:
        list_of_volunteers = all_event_info.list_of_volunteers()
    for volunteer in list_of_volunteers:
        volunteer_at_event_data = all_event_info.dict_of_registration_data_for_volunteers_at_event.get_data_for_volunteer(
            volunteer, default=None
        )
        if volunteer_at_event_data is None:
            dict_of_availability[volunteer] = DaySelector()
        else:
            dict_of_availability[volunteer] = volunteer_at_event_data.availablity

    return DictOfDaySelectors(dict_of_availability)


def add_volunteer_at_event(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    registration_data: RegistrationDataForVolunteerAtEvent,
):
    all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    all_event_data.add_new_volunteer(
        volunteer=volunteer, registration_data=registration_data
    )
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_event_data
    )


def get_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, event: Event
) -> DictOfAllEventDataForVolunteers:
    return object_store.DEPRECATE_get(
        object_definition=object_definition_for_dict_of_all_event_data_for_volunteers,
        event_id=event.id,
    )


def update_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, dict_of_all_event_data: DictOfAllEventDataForVolunteers
):
    object_store.DEPRECATE_update(
        object_definition=object_definition_for_dict_of_all_event_data_for_volunteers,
        event_id=dict_of_all_event_data.event.id,
        new_object=dict_of_all_event_data,
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
    first_relevant_information = list_of_relevant_information[
        0
    ]  ## can use first as all the same - checked

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


def delete_volunteer_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):
    all_volunteer_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    messages = all_volunteer_data.delete_volunteer_from_event(volunteer)
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_volunteer_data
    )

    return messages


def update_volunteer_availability_at_event(
    object_store: ObjectStore,
    volunteer: Volunteer,
    event: Event,
    availability: DaySelector,
):
    for day in event.days_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(
                object_store=object_store, event=event, volunteer=volunteer, day=day
            )
        else:
            make_volunteer_unavailable_on_day(
                object_store=object_store, event=event, volunteer=volunteer, day=day
            )


def make_volunteer_available_on_day(
    object_store: ObjectStore, volunteer: Volunteer, event: Event, day: Day
):
    dict_of_volunteer_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    dict_of_volunteer_data.make_volunteer_available_on_day(day=day, volunteer=volunteer)
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=dict_of_volunteer_data
    )


def make_volunteer_unavailable_on_day(
    object_store: ObjectStore, volunteer: Volunteer, event: Event, day: Day
):
    all_volunteer_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    all_volunteer_data.make_volunteer_unavailable_on_day(volunteer=volunteer, day=day)
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_volunteer_data
    )


def is_volunteer_currently_available_for_only_one_day(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> bool:
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    reg_for_volunteer = registration_data.get_data_for_volunteer(volunteer)
    availabilty = reg_for_volunteer.availablity.days_available()

    return len(availabilty) <= 1
