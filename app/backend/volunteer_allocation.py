from app.backend.update_master_event_data import get_row_in_master_event_for_cadet_id
from app.data_access.data import data
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_current_cadet_id, \
    get_volunteer_index
from app.logic.abstract_interface import abstractInterface
from app.logic.volunteers.add_volunteer import list_of_similar_volunteers
from app.objects.events import Event
from app.objects.utils import union_of_x_and_y
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfCadetsWithoutVolunteersAtEvent
from app.logic.events.volunteer_allocation.relevant_information import RelevantInformationForVolunteer, \
    get_volunteer_at_event_from_relevant_information, get_relevant_information_for_volunteer
from app.backend.cadets import cadet_name_from_id

CADET_ID = "cadet_id"

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

    list_of_volunteers_associated_with_cadet = [list_of_all_volunteers.object_with_id(id) for id in list_of_associated_ids]

    return list_of_volunteers_associated_with_cadet


def remove_volunteer_and_cadet_association(cadet_id: str, volunteer_id: str):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read()
    volunteers_at_event_data.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)

def delete_volunteer_with_id(volunteer_id: str):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read()
    volunteers_at_event_data.remove_volunteer_with_id(volunteer_id=volunteer_id)


def add_volunteer_and_cadet_association(cadet_id:str, volunteer_id: str, event_id: str, relevant_information: RelevantInformationForVolunteer):
    #### WHAT HAPPENS IF VOLUNTEER ALREADY AT EVENT FOR ANOTHER CADET?
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event_id)
    volunteer_at_event = get_volunteer_at_event_from_relevant_information(
        relevant_information=relevant_information,
        cadet_id=cadet_id,
        volunteer_id=volunteer_id
    )
    volunteers_at_event_data.add_potentially_new_volunteer_with_cadet_association(volunteer_at_event)

def mark_cadet_as_been_processed_if_no_volunteers_available(cadet_id: str, event:Event):
    list_of_associated_volunteers = volunteer_ids_associated_with_cadet_at_specific_event(event=event,
                                                                                          cadet_id=cadet_id)
    if len(list_of_associated_volunteers)==0:
        mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id=cadet_id, event=event)

def mark_cadet_as_been_processed_with_no_volunteers_available(cadet_id: str, event:Event):
    list_of_cadets_without_volunteers =  data.data_list_of_cadets_without_volunteers_at_event.read()
    list_of_cadets_without_volunteers.add_cadet_id_without_volunteer(cadet_id=cadet_id, event_id=event.id)
    data.data_list_of_cadets_without_volunteers_at_event.write(list_of_cadets_without_volunteers)

## Won't change between calls
list_of_all_volunteers = get_all_volunteers()

def get_volunteer_from_id(volunteer_id) -> Volunteer:
    return list_of_all_volunteers.object_with_id(volunteer_id)

def get_volunteer_name_and_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    name = str(list_of_all_volunteers.object_with_id(volunteer_id))
    other_cadets = get_string_of_other_associated_cadets_for_event(event=event,
                                                                   volunteer_id=volunteer_id,
                                                                   cadet_id=cadet_id)

    return name+other_cadets

def get_string_of_other_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [other_cadet_id for other_cadet_id in associated_cadets if other_cadet_id is not cadet_id]
    if len(associated_cadets_without_this_cadet)==0:
        return ""

    associated_cadets_without_this_cadet_names = [cadet_name_from_id(other_cadet_id) for other_cadet_id in associated_cadets_without_this_cadet]
    associated_cadets_without_this_cadet_names_str = ", ".join(associated_cadets_without_this_cadet_names)

    return "(Other registered cadets associated with this volunteer: "+associated_cadets_without_this_cadet_names_str

def get_volunteer_at_event(volunteer_id: str, event: Event):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteer_at_event = volunteers_at_event_data.volunteer_at_event_with_id(volunteer_id)

    return volunteer_at_event


def get_relevant_information_for_current_volunteer(interface: abstractInterface) -> RelevantInformationForVolunteer:
    cadet_id = get_current_cadet_id(interface)
    volunteer_index = get_volunteer_index(interface)
    event = get_event_from_state(interface)
    row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    relevant_information = get_relevant_information_for_volunteer(row_in_master_event=row_in_master_event, volunteer_index=volunteer_index)

    return relevant_information

def update_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    volunteers_at_event_data = data.data_list_of_volunteers_at_event.read(event_id=event.id)
    volunteers_at_event_data.update_volunteer_at_event(volunteer_at_event)
    data.data_list_of_volunteers_at_event.write(volunteers_at_event_data, event_id=event.id)
