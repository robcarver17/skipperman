from typing import List

from app.backend.data.volunteer_rota import delete_role_at_event_for_volunteer_on_day
from app.backend.data.volunteers import  get_all_volunteers, \
    get_list_of_cadet_volunteer_associations
from app.backend.data.volunteer_allocation import get_list_of_volunteers_at_event, \
    get_list_of_cadets_without_volunteers_at_all_events, mark_cadet_as_been_processed_with_no_volunteers_available, \
    update_volunteer_at_event, get_volunteer_at_event
from app.backend.cadets import cadet_name_from_id

from app.backend.volunteers.volunteers import list_of_similar_volunteers
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.food import FoodRequirements
from app.objects.utils import union_of_x_and_y
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent


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
    list_of_cadet_ids_with_no_volunteers = get_list_of_cadets_without_volunteers_at_event(event)

    return cadet_id in list_of_cadet_ids_with_no_volunteers

def get_list_of_cadets_without_volunteers_at_event(event: Event) -> list:
    list_of_cadets_without_volunteers = get_list_of_cadets_without_volunteers_at_all_events()
    return list_of_cadets_without_volunteers.list_of_cadet_ids_for_event(event_id=event.id)



def volunteer_ids_associated_with_cadet_at_specific_event(event: Event, cadet_id: str) -> list:
    volunteer_data = get_list_of_volunteers_at_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return volunteer_ids


def get_list_of_relevant_voluteers(volunteer: Volunteer, cadet_id: str) -> list:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(volunteer=volunteer)
    list_of_volunteers_associated_with_cadet = get_list_of_volunteers_associated_with_cadet(cadet_id=cadet_id)

    list_of_volunteers = union_of_x_and_y(list_of_volunteers_associated_with_cadet,
                                          list_of_volunteers_with_similar_name)

    return list_of_volunteers

def get_list_of_volunteers_associated_with_cadet(cadet_id: str) -> list:
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_associations()
    list_of_associated_ids = list_of_cadet_volunteer_associations.list_of_volunteer_ids_associated_with_cadet_id(cadet_id=cadet_id)
    list_of_all_volunteers = get_all_volunteers()

    list_of_volunteers_associated_with_cadet = [list_of_all_volunteers.object_with_id(volunteer_id) for volunteer_id in list_of_associated_ids]

    return list_of_volunteers_associated_with_cadet


def mark_cadet_as_been_processed_if_no_volunteers_available(cadet_id: str, event:Event):
    list_of_associated_volunteers = volunteer_ids_associated_with_cadet_at_specific_event(event=event,
                                                                                          cadet_id=cadet_id)
    if len(list_of_associated_volunteers)==0:
        mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id=cadet_id, event=event)


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

def get_string_of_other_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    associated_cadets_without_this_cadet = list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
        event=event,
        volunteer_id=volunteer_id,
        cadet_id=cadet_id
    )

    if len(associated_cadets_without_this_cadet)==0:
        return ("")

    associated_cadets_without_this_cadet_names = [cadet_name_from_id(other_cadet_id) for other_cadet_id in associated_cadets_without_this_cadet]
    associated_cadets_without_this_cadet_names_str = ", ".join(associated_cadets_without_this_cadet_names)

    return "(Other registered group_allocations associated with this volunteer: "+associated_cadets_without_this_cadet_names_str

def any_other_cadets_for_volunteer_at_event_apart_from_this_one(event: Event, volunteer_id:str, cadet_id:str) -> bool:
    associated_cadets_without_this_cadet = list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
        event=event,
        volunteer_id=volunteer_id,
        cadet_id=cadet_id
    )

    return len(associated_cadets_without_this_cadet)>0

def list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(event: Event, volunteer_id:str, cadet_id:str) -> List[str]:
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [other_cadet_id for other_cadet_id in associated_cadets if other_cadet_id!=cadet_id]

    return associated_cadets_without_this_cadet


def update_volunteer_food_at_event(volunteer_at_event: VolunteerAtEvent, event: Event, food_requirements: FoodRequirements):
    existing_volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_at_event.volunteer_id, event=event)
    existing_volunteer_at_event.food_requirements = food_requirements
    update_volunteer_at_event(volunteer_at_event=existing_volunteer_at_event, event=event)

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


