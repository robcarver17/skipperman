from typing import List, Dict

from app.backend.data.cadets_at_event import load_identified_cadets_at_event, load_cadets_at_event, \
    list_of_row_ids_at_event_given_cadet_id
from app.backend.data.volunteer_rota import delete_role_at_event_for_volunteer_on_day
from app.backend.data.volunteer_allocation import save_list_of_volunteers_at_event
from app.backend.data.volunteers import  load_all_volunteers, \
    get_list_of_cadet_volunteer_associations
from app.backend.data.volunteer_allocation import load_list_of_volunteers_at_event, \
    load_list_of_identified_volunteers_at_event, save_list_of_identified_volunteers_at_event,\
    update_volunteer_at_event, get_volunteer_at_event

from app.backend.cadets import cadet_name_from_id
from app.backend.volunteers.volunteers import list_of_similar_volunteers
from app.backend.wa_import.update_cadets_at_event import mark_cadet_at_event_as_unchanged, \
    get_cadet_at_event_for_cadet_id
from app.backend.volunteers.volunter_relevant_information import get_relevant_information_for_volunteer_given_details

from app.objects.constants import missing_data
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import ListOfRelevantInformationForVolunteer
#from app.objects.food import FoodRequirements
from app.objects.utils import union_of_x_and_y, in_x_not_in_y
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfIdentifiedVolunteersAtEvent


def add_identified_volunteer(volunteer_id:str,
                                event: Event,
                                row_id: str,
                             volunteer_index: int):
    list_of_volunteers = load_list_of_identified_volunteers_at_event(event)
    list_of_volunteers.add(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id)
    save_list_of_identified_volunteers_at_event(list_of_volunteers=list_of_volunteers, event=event)

def list_of_identified_volunteers_with_volunteer_id(volunteer_id:str,
                                event: Event) -> ListOfIdentifiedVolunteersAtEvent:

    list_of_volunteers = load_list_of_identified_volunteers_at_event(event)
    return list_of_volunteers.list_of_identified_volunteers_with_volunteer_id(volunteer_id)


def add_volunteer_at_event(event: Event,volunteer_id: str,list_of_associated_cadet_id: List[str],
                                                             availability: DaySelector,
                                                       preferred_duties: str,
                                same_or_different: str,
                                any_other_information: str,
                           notes: str
    ):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    volunteer_at_event = VolunteerAtEvent(
        volunteer_id=volunteer_id,
        availablity=availability,
        list_of_associated_cadet_id=list_of_associated_cadet_id,
        preferred_duties=preferred_duties,
        same_or_different=same_or_different,
        any_other_information=any_other_information,
        notes=notes
    )
    list_of_volunteers_at_event.add_new_volunteer(volunteer_at_event)

    save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)



def volunteer_ids_associated_with_cadet_at_specific_event(event: Event, cadet_id: str) -> list:
    volunteer_data = load_list_of_volunteers_at_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return volunteer_ids


def get_list_of_relevant_voluteers(volunteer: Volunteer,
                                   cadet_id: str ## could be missing data
                                     ) -> list:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(volunteer=volunteer)
    if cadet_id is missing_data:
        list_of_volunteers_associated_with_cadet= []
    else:
        list_of_volunteers_associated_with_cadet = get_list_of_volunteers_associated_with_cadet(cadet_id=cadet_id)

    list_of_volunteers = union_of_x_and_y(list_of_volunteers_associated_with_cadet,
                                          list_of_volunteers_with_similar_name)

    return list_of_volunteers

def get_list_of_volunteers_associated_with_cadet(cadet_id: str) -> list:
    list_of_cadet_volunteer_associations = get_list_of_cadet_volunteer_associations()
    list_of_associated_ids = list_of_cadet_volunteer_associations.list_of_volunteer_ids_associated_with_cadet_id(cadet_id=cadet_id)
    list_of_all_volunteers = load_all_volunteers()

    list_of_volunteers_associated_with_cadet = [list_of_all_volunteers.object_with_id(volunteer_id) for volunteer_id in list_of_associated_ids]

    return list_of_volunteers_associated_with_cadet


def mark_volunteer_as_skipped(
                                event: Event,
                                row_id: str,
                             volunteer_index: int):

    list_of_volunteers = load_list_of_identified_volunteers_at_event(event)
    list_of_volunteers.identified_as_processed_not_allocated(row_id=row_id, volunteer_index=volunteer_index)
    save_list_of_identified_volunteers_at_event(list_of_volunteers=list_of_volunteers, event=event)


def get_volunteer_name_and_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    list_of_all_volunteers = load_all_volunteers()

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


def update_volunteer_availability_at_event(volunteer_id:str, event: Event, availability: DaySelector):
    for day in event.weekdays_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(volunteer_id=volunteer_id, event=event, day=day)
        else:
            make_volunteer_unavailable_on_day(volunteer_id=volunteer_id, event=event, day=day)

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


def get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(event: Event, volunteer_id: str) -> List[str]:
    identified_cadets = load_identified_cadets_at_event(event)
    cadets_at_event = load_cadets_at_event(event)
    active_cadet_ids_at_event = cadets_at_event.list_of_active_cadet_ids()

    all_identified_volunteers_at_event = load_list_of_identified_volunteers_at_event(event)
    relevant_identified_volunteers = all_identified_volunteers_at_event.list_of_identified_volunteers_with_volunteer_id(volunteer_id)

    list_of_all_cadet_ids_for_volunteer = [
        identified_cadets.cadet_id_given_row_id(identified_volunteer.row_id)
        for identified_volunteer in relevant_identified_volunteers]

    unique_list_of_all_cadet_ids_for_volunteer = list(set(list_of_all_cadet_ids_for_volunteer))

    list_of_active_cadet_ids_for_volunteer = [
        cadet_id for cadet_id in unique_list_of_all_cadet_ids_for_volunteer
        if cadet_id in active_cadet_ids_at_event
    ]


    return list_of_active_cadet_ids_for_volunteer



def mark_all_cadets_associated_with_volunteer_at_event_as_no_longer_changed(event: Event, volunteer_id: str):
    list_of_associated_cadet_ids = get_list_of_associated_cadet_id_for_volunteer_at_event(event=event, volunteer_id=volunteer_id)

    for cadet_id in list_of_associated_cadet_ids:
        mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event)

def get_list_of_associated_cadet_id_for_volunteer_at_event(event: Event, volunteer_id: str)-> List[str]:
    volunteer_at_event = get_volunteer_at_event_with_id(event=event, volunteer_id=volunteer_id)
    currently_associated_cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    return currently_associated_cadet_ids


def volunteer_for_this_row_and_index_already_identified(event: Event, row_id: str, volunteer_index: int) -> bool:
    list_of_volunteers = load_list_of_identified_volunteers_at_event(event)
    
    volunteer_id= list_of_volunteers.volunteer_id_given_row_id_and_index(row_id=row_id, volunteer_index=volunteer_index)
    return volunteer_id is not missing_data


def update_cadet_connections_when_cadet_already_at_event(event: Event, volunteer_id: str):
    list_of_associated_cadet_id = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        event=event, volunteer_id=volunteer_id)

    currently_associated_cadet_ids = get_list_of_associated_cadet_id_for_volunteer_at_event(event=event, volunteer_id=volunteer_id)
    new_cadet_ids = in_x_not_in_y(x=list_of_associated_cadet_id, y=currently_associated_cadet_ids)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)

    for cadet_id in new_cadet_ids:
        print("Adding association with cadet %s to existing volunteer %s" % (cadet_id, volunteer_id))
        list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
        mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event)


def get_volunteer_at_event_with_id(event: Event, volunteer_id: str) -> VolunteerAtEvent:
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)

    return volunteer_at_event


def are_all_connected_cadets_cancelled_or_deleted(volunteer_id: str, event: Event)-> bool:

    list_of_relevant_information = get_list_of_relevant_information(volunteer_id=volunteer_id, event=event)

    return list_of_relevant_information.all_cancelled_or_deleted()


def is_current_cadet_active_at_event(cadet_id: str, event: Event)-> bool:
    cadet_at_event = get_cadet_at_event_for_cadet_id(event=event, cadet_id=cadet_id)

    return cadet_at_event.is_active()


def get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
                                                                               cadet_id: str, event: Event) \
        -> Dict[str, str]:

    ## list of volunteers at event
    list_of_volunteers_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)
    list_of_relevant_volunteer_names_and_other_cadets = [get_volunteer_name_and_associated_cadets_for_event(
        event=event, volunteer_id=volunteer_id, cadet_id=cadet_id) for volunteer_id in list_of_volunteers_ids
    ]

    return dict([volunteer_and_any_other_cadets, id] for volunteer_and_any_other_cadets, id in
                zip(list_of_relevant_volunteer_names_and_other_cadets, list_of_volunteers_ids))


def any_volunteers_associated_with_cadet_at_event(cadet_id: str, event:Event):
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
         cadet_id=cadet_id, event=event)
    return len(dict_of_relevant_volunteers)>0


def list_of_volunteers_for_cadet_identified(cadet_id: str, event: Event) -> List[str]:
    list_of_identified_volunteers_at_event = load_list_of_identified_volunteers_at_event(event=event)

    list_of_row_ids= list_of_row_ids_at_event_given_cadet_id(cadet_id=cadet_id, event=event)
    list_of_volunteer_ids=list_of_identified_volunteers_at_event.list_of_volunteer_ids_given_list_of_row_ids_excluding_unallocated(list_of_row_ids)

    return list_of_volunteer_ids


def get_list_of_relevant_information(volunteer_id: str, event: Event) -> ListOfRelevantInformationForVolunteer:

    list_of_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(volunteer_id=volunteer_id, event=event) ## can appear more than once

    list_of_relevant_information = [get_relevant_information_for_volunteer_given_details(
        row_id=identified_volunteer.row_id,
        volunteer_index=identified_volunteer.volunteer_index,
        event=event
            ) for identified_volunteer in list_of_identified_volunteers]

    return ListOfRelevantInformationForVolunteer(list_of_relevant_information)
