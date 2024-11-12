from typing import List

from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.OLD_backend.rota.volunteer_rota import delete_role_at_event_for_volunteer_on_all_days, \
    delete_role_at_event_for_volunteer_on_day

from app.data_access.store.data_access import DataLayer
from app.objects.cadets import ListOfCadets

from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData
from app.backend.registration_data.volunter_relevant_information import suggested_volunteer_availability
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import DaySelector, Day
from app.objects.relevant_information_for_volunteers import ListOfRelevantInformationForVolunteer
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId, ListOfVolunteersAtEventWithId
from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.composed.volunteers_at_event_with_registration_data import (
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_registration_data_for_volunteers_at_event,
    object_definition_for_dict_of_all_event_data_for_volunteers,
    object_definition_for_list_of_volunteers_with_ids_at_event,
)
from app.objects_OLD.volunteers_at_event import ListOfVolunteersAtEvent


def add_volunteer_at_event(
    object_store: ObjectStore,
    event: Event,
    volunteer_at_event: VolunteerAtEventWithId,
):
    list_of_volunteers_at_event = get_list_of_volunteers_with_ids_at_event(object_store=object_store, event=event)
    list_of_volunteers_at_event.add_new_volunteer(volunteer_at_event)
    update_list_of_volunteers_with_ids_at_event(object_store=object_store, event=event, list_of_volunteers_at_event_with_id=list_of_volunteers_at_event)


def get_list_of_volunteers_with_ids_at_event(object_store: ObjectStore, event:Event) -> ListOfVolunteersAtEventWithId:
    return object_store.get(object_definition=object_definition_for_list_of_volunteers_with_ids_at_event, event_id= event.id)

def update_list_of_volunteers_with_ids_at_event(object_store: ObjectStore, event:Event, list_of_volunteers_at_event_with_id: ListOfVolunteersAtEventWithId):
    object_store.update(new_object=list_of_volunteers_at_event_with_id, object_definition=object_definition_for_list_of_volunteers_with_ids_at_event,
                        event_id = event.id)


def get_dict_of_all_event_data_for_volunteers(
    object_store: ObjectStore, event: Event
) -> DictOfAllEventDataForVolunteers:
    return object_store.get(
        object_definition=object_definition_for_dict_of_all_event_data_for_volunteers,
        event_id=event.id,
    )


def get_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfRegistrationDataForVolunteerAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        event_id=event.id,
    )

def update_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore,  dict_of_registration_data: DictOfRegistrationDataForVolunteerAtEvent):
    object_store.update(
        new_object=dict_of_registration_data,
        object_definition=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        event_id=dict_of_registration_data.event.id,
    )


def is_volunteer_already_at_event(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> bool:
    dict_of_volunteers_at_event = get_dict_of_registration_data_for_volunteers_at_event(object_store=object_store, event=event)
    return volunteer in dict_of_volunteers_at_event.list_of_volunteers_at_event()


def get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer: Volunteer,
    list_of_associated_cadets: ListOfCadets,
) -> VolunteerAtEventWithId:
    first_relevant_information = list_of_relevant_information[
        0
    ]  ## can use first as all the same - checked
    return VolunteerAtEventWithId(
        volunteer_id=volunteer.id,
        availablity=suggested_volunteer_availability(
            first_relevant_information.availability
        ),
        list_of_associated_cadet_id=list_of_associated_cadets.list_of_ids,
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
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(object_store=object_store, event=event)
    return registration_data.list_of_volunteers_at_event()



def delete_volunteer_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
):

    dict_of_registration_data = get_dict_of_registration_data_for_volunteers_at_event(object_store=object_store, event=event)
    dict_of_registration_data.drop_volunteer(volunteer)
    update_dict_of_registration_data_for_volunteers_at_event(dict_of_registration_data=dict_of_registration_data, object_store=object_store)


    patrol_boat_data = PatrolBoatsData(data_layer)
    patrol_boat_data.delete_volunteer_with_id_at_event(
        event=event, volunteer_id=volunteer_id
    )

    delete_role_at_event_for_volunteer_on_all_days(
        data_layer=data_layer, volunteer_id=volunteer_id, event=event
    )


def update_volunteer_availability_at_event(
    data_layer: DataLayer,
    volunteer: Volunteer,
    event: Event,
    availability: DaySelector,
):
    for day in event.weekdays_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(
                data_layer=data_layer, event=event, volunteer=volunteer, day=day
            )
        else:
            make_volunteer_unavailable_on_day(
                data_layer=data_layer, event=event, volunteer=volunteer, day=day
            )


def make_volunteer_available_on_day(
    data_layer: DataLayer, volunteer: Volunteer, event: Event, day: Day
):
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    volunteer_allocation_data.make_volunteer_available_on_day(
        event=event, day=day, volunteer=volunteer
    )


def make_volunteer_unavailable_on_day(
    data_layer: DataLayer, volunteer: Volunteer, event: Event, day: Day
):
    volunteer_allocation_data = VolunteerAllocationData(data_layer)
    volunteer_allocation_data.make_volunteer_unavailable_on_day(
        event=event, day=day, volunteer=volunteer
    )
    ## also delete any associated roles for tidyness
    delete_role_at_event_for_volunteer_on_day(
        data_layer=data_layer, event=event, volunteer=volunteer, day=day
    )

    ### and patrol boat data
    patrol_boat_data = PatrolBoatsData(data_layer)
    patrol_boat_data.remove_volunteer_from_patrol_boat_on_day_at_event(
        event=event, volunteer=volunteer, day=day
    )
