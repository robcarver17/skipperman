from typing import List

from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
    update_dict_of_registration_data_for_volunteers_at_event,
)
from app.objects.cadets import ListOfCadets
from app.objects.composed.volunteers_at_event_with_registration_data import RegistrationDataForVolunteerAtEvent

from app.objects.day_selectors import DaySelector, Day
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.objects.volunteer_at_event_with_id import (
    VolunteerAtEventWithId,
    ListOfVolunteersAtEventWithId,
)
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


def add_volunteer_at_event(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    registration_data: RegistrationDataForVolunteerAtEvent

):
    all_event_data = get_dict_of_all_event_data_for_volunteers(object_store=object_store, event=event)
    all_event_data.add_new_volunteer(volunteer=volunteer,
                                     registration_data=registration_data)
    update_dict_of_all_event_data_for_volunteers(object_store=object_store, dict_of_all_event_data=all_event_data)




def get_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, event: Event
) -> DictOfAllEventDataForVolunteers:
    return object_store.get(
        object_definition=object_definition_for_dict_of_all_event_data_for_volunteers,
        event_id=event.id,
    )


def update_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, dict_of_all_event_data: DictOfAllEventDataForVolunteers
):
    object_store.update(
        object_definition=object_definition_for_dict_of_all_event_data_for_volunteers,
        event_id=dict_of_all_event_data.event.id,
        new_object=dict_of_all_event_data,
    )


def get_volunteer_registration_data_from_list_of_relevant_information_with_no_conflicts(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    list_of_associated_cadets: ListOfCadets,
) -> RegistrationDataForVolunteerAtEvent:
    first_relevant_information = list_of_relevant_information[
        0
    ]  ## can use first as all the same - checked
    return RegistrationDataForVolunteerAtEvent(
        availablity=first_relevant_information.availability.volunteer_availablity,
        list_of_associated_cadets=list_of_associated_cadets,
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
    all_volunteer_data.delete_volunteer_from_event(volunteer)
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_volunteer_data
    )


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
    dict_of_volunteer_data = get_dict_of_all_event_data_for_volunteers(object_store=object_store, event=event)
    dict_of_volunteer_data.make_volunteer_available_on_day(day=day, volunteer=volunteer)
    update_dict_of_all_event_data_for_volunteers(object_store=object_store, dict_of_all_event_data=dict_of_volunteer_data)

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
