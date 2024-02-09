from app.backend.volunteers.volunteer_allocation import delete_role_at_event_for_volunteer_on_all_days
from app.backend.volunteers.volunter_relevant_information import get_volunteer_at_event_from_relevant_information
from app.data_access.data import data
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import RelevantInformationForVolunteer
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent, ListOfCadetsWithoutVolunteersAtEvent, \
    VolunteerAtEvent


def get_list_of_volunteers_at_event(event: Event):
    return data.data_list_of_volunteers_at_event.read(event_id=event.id)


def save_list_of_volunteers_at_event(event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEvent):
    data.data_list_of_volunteers_at_event.write(event_id=event.id, list_of_volunteers_at_event=list_of_volunteers_at_event)


def get_list_of_cadets_without_volunteers_at_all_events() -> ListOfCadetsWithoutVolunteersAtEvent:
    list_of_cadets_without_volunteers =  data.data_list_of_cadets_without_volunteers_at_event.read()

    return list_of_cadets_without_volunteers


def save_list_of_cadets_without_volunteers_at_all_events(list_of_cadets_without_volunteers: ListOfCadetsWithoutVolunteersAtEvent):
    data.data_list_of_cadets_without_volunteers_at_event.write(list_of_cadets_without_volunteers)


def remove_volunteer_and_cadet_association_at_event(cadet_id: str, volunteer_id: str, event: Event):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def delete_volunteer_with_id_at_event(volunteer_id: str, event: Event):
    list_of_volunteers_at_event= get_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_volunteer_with_id(volunteer_id=volunteer_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)

    ## for consistenecy also remove assigned roles FIXME REMOVE
    delete_role_at_event_for_volunteer_on_all_days(volunteer_id=volunteer_id, event=event)


def add_volunteer_and_cadet_association_for_potential_new_volunteer(cadet_id:str, volunteer_id: str, event: Event, relevant_information: RelevantInformationForVolunteer):

    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)
    volunteer_at_event = get_volunteer_at_event_from_relevant_information(
        relevant_information=relevant_information,
        cadet_id=cadet_id,
        volunteer_id=volunteer_id
    )
    list_of_volunteers_at_event.add_potentially_new_volunteer_with_cadet_association(volunteer_at_event)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def add_volunteer_and_cadet_association_for_existing_volunteer(cadet_id:str, volunteer_id: str, event: Event):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(volunteer_id=volunteer_id, cadet_id=cadet_id)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def add_volunteer_to_event_with_just_id(volunteer_id: str, event: Event):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)
    availability = event.day_selector_with_covered_days() ## assume available all days in event

    list_of_volunteers_at_event.add_volunteer_with_just_id(volunteer_id,
                                                        availability=availability)

    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id: str, event:Event):
    list_of_cadets_without_volunteers =  get_list_of_cadets_without_volunteers_at_all_events()
    list_of_cadets_without_volunteers.add_cadet_id_without_volunteer(cadet_id=cadet_id, event_id=event.id)
    save_list_of_cadets_without_volunteers_at_all_events(list_of_cadets_without_volunteers=list_of_cadets_without_volunteers)


def update_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    list_of_volunteers_at_event = get_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.update_volunteer_at_event(volunteer_at_event)
    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)
