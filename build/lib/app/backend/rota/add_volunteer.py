from app.objects.cadets import ListOfCadets
from app.objects.composed.volunteers_at_event_with_registration_data import RegistrationDataForVolunteerAtEvent
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId

from app.objects.utils import in_x_not_in_y

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event
from app.objects.volunteers import ListOfVolunteers, Volunteer
from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.backend.volunteers.volunteers_at_event import add_volunteer_at_event
from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
)


def get_list_of_volunteers_except_those_already_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteers:
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    volunteers_at_event = registration_data.list_of_volunteers_at_event()
    master_list_of_volunteers = get_list_of_volunteers(object_store)

    all_volunteer_ids = master_list_of_volunteers.list_of_ids
    ids_of_volunteers_not_at_event = in_x_not_in_y(
        x=all_volunteer_ids, y=volunteers_at_event.list_of_ids
    )

    volunteers_not_at_event = (
        master_list_of_volunteers.subset_from_list_of_ids_retaining_order(
            ids_of_volunteers_not_at_event
        )
    )

    return volunteers_not_at_event.sort_by_firstname()


def add_volunteer_to_event_with_full_availability(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
):
    availability = (
        event.day_selector_for_days_in_event()
    )  ## assume available all days in event

    registration_data = RegistrationDataForVolunteerAtEvent(availablity=availability,
                                                            list_of_associated_cadets=ListOfCadets([]))

    add_volunteer_at_event(
        object_store=object_store,
        event=event,
        volunteer=volunteer,
        registration_data=registration_data
    )
