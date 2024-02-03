from typing import List

from app.backend.volunteers.volunter_relevant_information import get_volunteer_at_event_from_relevant_information
from app.backend.cadets import cadet_name_from_id

from app.data_access.data import data
from app.backend.volunteers.volunteers import list_of_similar_volunteers
from app.logic.events.events_in_state import get_event_given_id
from app.objects.constants import missing_data
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.food import FoodRequirements
from app.objects.utils import union_of_x_and_y
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfCadetsWithoutVolunteersAtEvent
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent


def get_all_volunteers()-> ListOfVolunteers:
    return data.data_list_of_volunteers.read()

def any_volunteers_at_event_for_cadet(event: Event, cadet_id: str) -> bool:
    volunteer_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)
    return len(volunteer_ids)>0


def have_volunteers_been_processed_at_event_for_cadet(event: Event, cadet_id: str) -> bool:
    volunteer_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)
    has_volunteer = len(volunteer_ids)>0
    processed_but_no_volunteers = is_cadet_marked_as_no_volunteers_but_already_processed(cadet_id=cadet_id,event=event)

    is_processed = has_volunteer or processed_but_no_volunteers

    return is_processed

def is_cadet_marked_as_no_volunteers_but_already_processed(cadet_id: str, event: Event) -> bool:
    list_of_cadet_ids_with_no_volunteers = get_list_of_cadets_without_volunteers_at_event(event=event)

    return cadet_id in list_of_cadet_ids_with_no_volunteers

def get_list_of_cadets_without_volunteers_at_event(event: Event) -> list:
    list_of_cadets_without_volunteers = get_list_of_cadets_without_volunteers()
    return list_of_cadets_without_volunteers.list_of_cadet_ids_for_event(event_id=event.id)

def get_list_of_cadets_without_volunteers() -> ListOfCadetsWithoutVolunteersAtEvent:
    return data.data_list_of_cadets_without_volunteers_at_event.read()


def volunteer_ids_associated_with_cadet_at_specific_event(event: Event, cadet_id: str) -> list:
    volunteer_data = get_volunteer_data_for_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return volunteer_ids


def get_volunteer_data_for_event(event: Event):
    return data.data_list_of_volunteers_at_event.read(event_id=event.id)


def get_list_of_relevant_voluteers(volunteer: Volunteer, cadet_id: str) -> list:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(volunteer=volunteer)
    list_of_volunteers_associated_with_cadet = get_list_of_volunteers_associated_with_cadet(cadet_id=cadet_id)

    list_of_volunteers = union_of_x_and_y(list_of_volunteers_associated_with_cadet,
                                          list_of_volunteers_with_similar_name)

    return list_of_volunteers

def get_list_of_volunteers_associated_with_cadet(cadet_id: str) -> list:
    list_of_cadet_volunteer_associations = data.data_list_of_cadet_volunteer_associations.read()
    list_of_associated_ids = list_of_cadet_volunteer_associations.list_of_volunteer_ids_associated_with_cadet_id(cadet_id=cadet_id)
    list_of_all_volunteers = data.data_list_of_volunteers.read()

    list_of_volunteers_associated_with_cadet = [list_of_all_volunteers.object_with_id(volunteer_id) for volunteer_id in list_of_associated_ids]

    return list_of_volunteers_associated_with_cadet


def remove_volunteer_and_cadet_association(cadet_id: str, volunteer_id: str, event: Event):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteers_at_event_data.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
    data.data_list_of_volunteers_at_event.write(event_id=event.id, list_of_volunteers_at_event=volunteers_at_event_data)

def delete_volunteer_with_id_at_event(volunteer_id: str, event: Event):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteers_at_event_data.remove_volunteer_with_id(volunteer_id=volunteer_id)
    data.data_list_of_volunteers_at_event.write(event_id=event.id, list_of_volunteers_at_event=volunteers_at_event_data)

    ## for consistenecy also remove assigned roles
    delete_role_at_event_for_volunteer_on_all_days(volunteer_id=volunteer_id, event=event)


def add_volunteer_and_cadet_association_for_potential_new_volunteer(cadet_id:str, volunteer_id: str, event_id: str, relevant_information: RelevantInformationForVolunteer):

    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event_id)
    volunteer_at_event = get_volunteer_at_event_from_relevant_information(
        relevant_information=relevant_information,
        cadet_id=cadet_id,
        volunteer_id=volunteer_id
    )
    volunteers_at_event_data.add_potentially_new_volunteer_with_cadet_association(volunteer_at_event)
    data.data_list_of_volunteers_at_event.write(volunteers_at_event_data, event_id=event_id)


def add_volunteer_and_cadet_association_for_existing_volunteer(cadet_id:str, volunteer_id: str, event_id: str):

    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event_id)
    volunteers_at_event_data.add_cadet_id_to_existing_volunteer(volunteer_id=volunteer_id, cadet_id=cadet_id)
    data.data_list_of_volunteers_at_event.write(volunteers_at_event_data, event_id=event_id)

def add_volunteer_to_event_with_just_id(volunteer_id: str, event_id: str):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event_id)
    event = get_event_given_id(event_id)
    availability = event.day_selector_with_covered_days() ## assume available all days in event

    volunteers_at_event_data.add_volunteer_with_just_id(volunteer_id,
                                                        availability=availability)

    data.data_list_of_volunteers_at_event.write(volunteers_at_event_data, event_id=event_id)

def mark_cadet_as_been_processed_if_no_volunteers_available(cadet_id: str, event:Event):
    list_of_associated_volunteers = volunteer_ids_associated_with_cadet_at_specific_event(event=event,
                                                                                          cadet_id=cadet_id)
    if len(list_of_associated_volunteers)==0:
        mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id=cadet_id, event=event)

def mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id: str, event:Event):
    list_of_cadets_without_volunteers =  data.data_list_of_cadets_without_volunteers_at_event.read()
    list_of_cadets_without_volunteers.add_cadet_id_without_volunteer(cadet_id=cadet_id, event_id=event.id)
    data.data_list_of_cadets_without_volunteers_at_event.write(list_of_cadets_without_volunteers)

def get_volunteer_from_id(volunteer_id) -> Volunteer:
    list_of_all_volunteers = get_all_volunteers()
    return list_of_all_volunteers.object_with_id(volunteer_id)

def get_volunteer_name_and_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    list_of_all_volunteers = get_all_volunteers()

    name = str(list_of_all_volunteers.object_with_id(volunteer_id))
    other_cadets = get_string_of_other_associated_cadets_for_event(event=event,
                                                                   volunteer_id=volunteer_id,
                                                                   cadet_id=cadet_id)

    return name+other_cadets

def get_string_of_other_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [other_cadet_id for other_cadet_id in associated_cadets if other_cadet_id!=cadet_id]
    if len(associated_cadets_without_this_cadet)==0:
        return ""

    associated_cadets_without_this_cadet_names = [cadet_name_from_id(other_cadet_id) for other_cadet_id in associated_cadets_without_this_cadet]
    associated_cadets_without_this_cadet_names_str = ", ".join(associated_cadets_without_this_cadet_names)

    return "(Other registered group_allocations associated with this volunteer: "+associated_cadets_without_this_cadet_names_str

def get_volunteer_at_event(volunteer_id: str, event: Event) -> VolunteerAtEvent:
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteer_at_event = volunteers_at_event_data.volunteer_at_event_with_id(volunteer_id)
    if volunteer_at_event is missing_data:
        raise Exception("Weirdly volunteer with id %s is no longer in event %s" % (volunteer_id, event))

    return volunteer_at_event


def update_volunteer_food_at_event(volunteer_at_event: VolunteerAtEvent, event: Event, food_requirements: FoodRequirements):
    existing_volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_at_event.volunteer_id, event=event)
    existing_volunteer_at_event.food_requirements = food_requirements
    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

def update_volunteer_availability_at_event(volunteer_at_event: VolunteerAtEvent, event: Event, availability: DaySelector):
    for day in event.weekdays_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(volunteer_id=volunteer_at_event.volunteer_id, event=event, day=day)
        else:
            make_volunteer_unavailable_on_day(volunteer_id=volunteer_at_event.volunteer_id, event=event, day=day)

def make_volunteer_available_on_day(volunteer_id: str, event: Event, day: Day):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer_at_event.availablity.make_available_on_day(day)
    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)


def make_volunteer_unavailable_on_day(volunteer_id: str, event: Event, day: Day):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer_at_event.availablity.make_unavailable_on_day(day)
    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

    ## also delete any associated roles for tidyness
    delete_role_at_event_for_volunteer_on_day(volunteer_id=volunteer_id, event=event, day=day)

def update_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteers_at_event_data.update_volunteer_at_event(volunteer_at_event)
    data.data_list_of_volunteers_at_event.write(volunteers_at_event_data, event_id=event.id)


def days_at_event_when_volunteer_available(event: Event,
                                                                             volunteer_id: str) -> List[Day]:
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    all_days = [day
                    for day in event.weekdays_in_event()
                        if volunteer_at_event.availablity.available_on_day(day)]

    return all_days


def delete_role_at_event_for_volunteer_on_day(volunteer_id: str, day: Day,
                                     event: Event):
    volunteer_in_role_at_event_on_day = VolunteerInRoleAtEvent(volunteer_id=volunteer_id,
                                                               day=day)

    volunteers_in_roles_data = data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)
    volunteers_in_roles_data.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day)
    data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                         list_of_volunteers_in_roles_at_event=volunteers_in_roles_data)

def delete_role_at_event_for_volunteer_on_all_days(volunteer_id: str,
                                     event: Event):

    for day in event.weekdays_in_event():
        delete_role_at_event_for_volunteer_on_day(volunteer_id=volunteer_id,
                                                  day=day,
                                                  event=event)