from typing import List

from app.data_access.data import DEPRECATED_data
from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent, ListOfIdentifiedVolunteersAtEvent,\
    VolunteerAtEvent

def load_list_of_identified_volunteers_at_event(event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_identified_volunteers_at_event.read(event_id=event.id)

def save_list_of_identified_volunteers_at_event(event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent):
    DEPRECATED_data.data_list_of_identified_volunteers_at_event.write(list_of_identified_volunteers=list_of_volunteers, event_id=event.id)

def load_list_of_volunteers_at_event(event: Event)-> ListOfVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_volunteers_at_event.read(event_id=event.id)


def save_list_of_volunteers_at_event(event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEvent):
    DEPRECATED_data.data_list_of_volunteers_at_event.write(event_id=event.id, list_of_volunteers_at_event=list_of_volunteers_at_event)








def remove_volunteer_and_cadet_association_at_event(cadet_id: str, volunteer_id: str, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def delete_volunteer_with_id_at_event(volunteer_id: str, event: Event):
    list_of_volunteers_at_event= load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_volunteer_with_id(volunteer_id=volunteer_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def update_volunteer_notes_at_event(event: Event, volunteer_id: str, new_notes: str):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.update_volunteer_notes_at_event(volunteer_id=volunteer_id, new_notes=new_notes)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)



def add_volunteer_and_cadet_association_for_existing_volunteer(cadet_id:str, volunteer_id: str, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(volunteer_id=volunteer_id, cadet_id=cadet_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def add_volunteer_to_event_with_just_id(volunteer_id: str, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    availability = event.day_selector_with_covered_days() ## assume available all days in event

    list_of_volunteers_at_event.add_volunteer_with_just_id(volunteer_id,
                                                        availability=availability)

    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)




def update_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.update_volunteer_at_event(volunteer_at_event)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def days_at_event_when_volunteer_available(event: Event,
                                                                             volunteer_id: str) -> List[Day]:
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    all_days = [day
                    for day in event.weekdays_in_event()
                        if volunteer_at_event.availablity.available_on_day(day)]

    return all_days


def get_volunteer_at_event(volunteer_id: str, event: Event) -> VolunteerAtEvent:
    volunteers_at_event_data = load_list_of_volunteers_at_event(event)
    volunteer_at_event = volunteers_at_event_data.volunteer_at_event_with_id(volunteer_id)
    if volunteer_at_event is missing_data:
        raise Exception("Weirdly volunteer with id %s is no longer in event %s" % (volunteer_id, event))

    return volunteer_at_event

def is_volunteer_already_at_event(volunteer_id: str, event: Event) -> bool:
    volunteers_at_event_data = load_list_of_volunteers_at_event(event)

    return volunteer_id in volunteers_at_event_data.list_of_volunteer_ids
