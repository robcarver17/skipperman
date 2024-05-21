from typing import List, Dict, Union

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.patrol_boats import PatrolBoatsData
from app.backend.data.cadets_at_event import \
    list_of_row_ids_at_event_given_cadet_id, CadetsAtEventData
from app.backend.data.volunteer_allocation import VolunteerAllocationData
from app.backend.data.volunteers import DEPRECATE_load_all_volunteers,    VolunteerData,  SORT_BY_FIRSTNAME
from app.backend.volunteers.volunteer_rota import DEPRECATED_load_list_of_identified_volunteers_at_event, \
    load_list_of_identified_volunteers_at_event, DEPRECATED_load_list_of_volunteers_at_event, \
    DEPRECATE_get_volunteer_at_event, get_volunteer_at_event, delete_role_at_event_for_volunteer_on_day

from app.backend.cadets import DEPRECATED_cadet_name_from_id, cadet_name_from_id
from app.backend.volunteers.volunteers import  list_of_similar_volunteers
from app.backend.wa_import.update_cadets_at_event import   get_cadet_at_event_for_cadet_id
from app.backend.volunteers.volunter_relevant_information import \
    get_relevant_information_for_volunteer_in_event_at_row_and_index

from app.objects.constants import missing_data
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.relevant_information_for_volunteers import ListOfRelevantInformationForVolunteer
#from app.objects.food import FoodRequirements
from app.objects.utils import union_of_x_and_y, in_x_not_in_y
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfIdentifiedVolunteersAtEvent


def add_identified_volunteer(interface: abstractInterface,
                                volunteer_id:str,
                                event: Event,
                                row_id: str,
                             volunteer_index: int):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_identified_volunteer(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id, event=event)

def DEPRECATE_list_of_identified_volunteers_with_volunteer_id(volunteer_id:str,
                                                              event: Event) -> ListOfIdentifiedVolunteersAtEvent:

    list_of_volunteers = DEPRECATED_load_list_of_identified_volunteers_at_event(event)
    return list_of_volunteers.list_of_identified_volunteers_with_volunteer_id(volunteer_id)

def list_of_identified_volunteers_with_volunteer_id(interface: abstractInterface,
                                                    volunteer_id:str,
                                                              event: Event) -> ListOfIdentifiedVolunteersAtEvent:

    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    list_of_volunteers = volunteer_allocation_data.load_list_of_identified_volunteers_at_event(event)
    return list_of_volunteers.list_of_identified_volunteers_with_volunteer_id(volunteer_id)


def add_volunteer_at_event(interface: abstractInterface,
                           event: Event,
                           volunteer_at_event: VolunteerAtEvent
    ):


    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_at_event(event=event, volunteer_at_event=volunteer_at_event)



def DEPRECATE_volunteer_ids_associated_with_cadet_at_specific_event(event: Event, cadet_id: str) -> list:
    volunteer_data = DEPRECATED_load_list_of_volunteers_at_event(event)
    volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

    return volunteer_ids

def volunteer_ids_associated_with_cadet_at_specific_event(interface:abstractInterface, event: Event, cadet_id: str) -> list:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)



def get_list_of_relevant_volunteers(interface:abstractInterface,
                                    volunteer: Volunteer,
                                    cadet_id: str  ## could be missing data
                                    ) -> list:
    list_of_volunteers_with_similar_name = list_of_similar_volunteers(interface=interface, volunteer=volunteer)
    if cadet_id is missing_data:
        list_of_volunteers_associated_with_cadet= []
    else:
        list_of_volunteers_associated_with_cadet = get_list_of_volunteers_associated_with_cadet(interface=interface, cadet_id=cadet_id)

    list_of_volunteers = union_of_x_and_y(list_of_volunteers_associated_with_cadet,
                                          list_of_volunteers_with_similar_name)

    return list_of_volunteers

def get_list_of_volunteers_associated_with_cadet(interface: abstractInterface, cadet_id: str) -> list:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_list_of_volunteers_associated_with_cadet(cadet_id)


def mark_volunteer_as_skipped(interface: abstractInterface,
                                event: Event,
                                row_id: str,
                             volunteer_index: int):

    volunteer_data = VolunteerAllocationData(interface.data)
    volunteer_data.mark_volunteer_as_skipped(row_id=row_id, volunteer_index=volunteer_index, event=event)
    interface.save_stored_items()

def DEPRECATE_get_volunteer_name_and_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    list_of_all_volunteers = DEPRECATE_load_all_volunteers()

    name = str(list_of_all_volunteers.object_with_id(volunteer_id))
    other_cadets = DEPRECATE_get_string_of_other_associated_cadets_for_event(event=event,
                                                                             volunteer_id=volunteer_id,
                                                                             cadet_id=cadet_id)

    return name+other_cadets

def get_volunteer_name_and_associated_cadets_for_event(interface: abstractInterface, event: Event, volunteer_id:str, cadet_id:str) -> str:
    volunteer_data = VolunteerData(interface.data)
    list_of_all_volunteers = volunteer_data.get_list_of_volunteers()
    volunteer_name = str(list_of_all_volunteers.object_with_id(volunteer_id))

    other_cadets = get_string_of_other_associated_cadets_for_event(interface=interface,
                    event=event,
                                                                             volunteer_id=volunteer_id,
                                                                             cadet_id=cadet_id)

    return volunteer_name+other_cadets


def get_string_of_other_associated_cadets_for_event(interface: abstractInterface, event: Event, volunteer_id:str, cadet_id:str) -> str:
    associated_cadets_without_this_cadet = get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        cadet_id=cadet_id
    )

    if len(associated_cadets_without_this_cadet)==0:
        return ("")

    associated_cadets_without_this_cadet_names = [cadet_name_from_id(interface=interface, cadet_id=other_cadet_id)
                                                  for other_cadet_id in associated_cadets_without_this_cadet]
    associated_cadets_without_this_cadet_names_str = ", ".join(associated_cadets_without_this_cadet_names)

    return "(Other registered group_allocations associated with this volunteer: "+associated_cadets_without_this_cadet_names_str+" )"

def DEPRECATE_get_string_of_other_associated_cadets_for_event(event: Event, volunteer_id:str, cadet_id:str) -> str:
    associated_cadets_without_this_cadet = DEPRECATE_get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
        event=event,
        volunteer_id=volunteer_id,
        cadet_id=cadet_id
    )

    if len(associated_cadets_without_this_cadet)==0:
        return ("")

    associated_cadets_without_this_cadet_names = [DEPRECATED_cadet_name_from_id(other_cadet_id) for other_cadet_id in associated_cadets_without_this_cadet]
    associated_cadets_without_this_cadet_names_str = ", ".join(associated_cadets_without_this_cadet_names)

    return "(Other registered group_allocations associated with this volunteer: "+associated_cadets_without_this_cadet_names_str+" )"

def any_other_cadets_for_volunteer_at_event_apart_from_this_one(interface: abstractInterface, event: Event, volunteer_id:str, cadet_id:str) -> bool:
    associated_cadets_without_this_cadet = get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        cadet_id=cadet_id
    )

    return len(associated_cadets_without_this_cadet)>0

def get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(interface: abstractInterface, event: Event, volunteer_id:str, cadet_id:str) -> List[str]:
    volunteer_at_event = get_volunteer_at_event(interface=interface, volunteer_id=volunteer_id, event=event)
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [other_cadet_id for other_cadet_id in associated_cadets if other_cadet_id!=cadet_id]

    return associated_cadets_without_this_cadet

def DEPRECATE_get_list_of_other_cadets_for_volunteer_at_event_apart_from_this_one(event: Event, volunteer_id:str, cadet_id:str) -> List[str]:
    volunteer_at_event = DEPRECATE_get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    associated_cadets = volunteer_at_event.list_of_associated_cadet_id
    associated_cadets_without_this_cadet = [other_cadet_id for other_cadet_id in associated_cadets if other_cadet_id!=cadet_id]

    return associated_cadets_without_this_cadet



def update_volunteer_availability_at_event(interface: abstractInterface, volunteer_id:str, event: Event, availability: DaySelector):
    for day in event.weekdays_in_event():
        if availability.available_on_day(day):
            make_volunteer_available_on_day(interface=interface, volunteer_id=volunteer_id, event=event, day=day)
        else:
            make_volunteer_unavailable_on_day(interface=interface,volunteer_id=volunteer_id, event=event, day=day)



def make_volunteer_available_on_day(interface: abstractInterface, volunteer_id: str, event: Event, day: Day):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.make_volunteer_available_on_day(event=event, day=day, volunteer_id=volunteer_id)

def make_volunteer_unavailable_on_day(interface: abstractInterface, volunteer_id: str, event: Event, day: Day):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.make_volunteer_unavailable_on_day(event=event,
                                                                day=day,
                                                                volunteer_id=volunteer_id
                                                                )
    ## also delete any associated roles for tidyness
    delete_role_at_event_for_volunteer_on_day(interface=interface, volunteer_id=volunteer_id, event=event, day=day)

    ### and patrol boat data
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.remove_volunteer_from_patrol_boat_on_day_at_event(event=event, volunteer_id=volunteer_id, day=day)


def get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(interface: abstractInterface,
        event: Event, volunteer_id: str) -> List[str]:

    cadets_at_event_data = CadetsAtEventData(interface.data)
    active_cadet_ids_at_event = cadets_at_event_data.list_of_active_cadet_ids_at_event(event)

    unique_list_of_all_cadet_ids_for_volunteer = get_unique_list_of_cadet_ids_in_mapped_event_data_given_identified_volunteer_id(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    list_of_active_cadet_ids_for_volunteer = [
        cadet_id for cadet_id in unique_list_of_all_cadet_ids_for_volunteer
        if cadet_id in active_cadet_ids_at_event
    ]


    return list_of_active_cadet_ids_for_volunteer



def get_unique_list_of_cadet_ids_in_mapped_event_data_given_identified_volunteer_id(interface: abstractInterface,
        event: Event, volunteer_id: str) -> List[str]:

    cadets_at_event_data = CadetsAtEventData(interface.data)
    identified_cadets_at_event = cadets_at_event_data.get_list_of_identified_cadets_at_event(event)

    relevant_identified_volunteers = get_list_of_volunteers_identified_at_event_with_volunteer_id(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id
    )

    list_of_all_cadet_ids_for_volunteer = [
        identified_cadets_at_event.cadet_id_given_row_id(identified_volunteer.row_id)
        for identified_volunteer in relevant_identified_volunteers]

    unique_list_of_all_cadet_ids_for_volunteer = list(set(list_of_all_cadet_ids_for_volunteer))

    return unique_list_of_all_cadet_ids_for_volunteer


def get_list_of_volunteers_identified_at_event_with_volunteer_id(interface: abstractInterface,
                                                                                    event: Event, volunteer_id: str) -> ListOfIdentifiedVolunteersAtEvent:
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    all_identified_volunteers_at_event = volunteers_at_event_data.load_list_of_identified_volunteers_at_event(event)
    relevant_identified_volunteers = all_identified_volunteers_at_event.list_of_identified_volunteers_with_volunteer_id(
        volunteer_id)

    return relevant_identified_volunteers


def get_list_of_associated_cadet_id_for_volunteer_at_event(interface: abstractInterface, event: Event, volunteer_id: str)-> List[str]:

    volunteer_at_event = get_volunteer_at_event_with_id(interface=interface, event=event, volunteer_id=volunteer_id)
    currently_associated_cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    return currently_associated_cadet_ids


def volunteer_for_this_row_and_index_already_identified(interface: abstractInterface, event: Event, row_id: str, volunteer_index: int) -> bool:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)

    return volunteer_allocation_data.volunteer_for_this_row_and_index_already_identified(
        event=event,
        row_id=row_id,
        volunteer_index=volunteer_index
    )


def update_cadet_connections_when_volunteer_already_at_event(interface: abstractInterface, event: Event, volunteer_id: str):
    list_of_associated_cadet_id_in_mapped_data = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, event=event, volunteer_id=volunteer_id)

    currently_associated_cadet_ids_in_volunteer_allocation_data = get_list_of_associated_cadet_id_for_volunteer_at_event(interface=interface, event=event, volunteer_id=volunteer_id)
    new_cadet_ids = in_x_not_in_y(x=list_of_associated_cadet_id_in_mapped_data, y=currently_associated_cadet_ids_in_volunteer_allocation_data)

    update_cadet_connections_for_volunteer_with_list_of_cadet_ids(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        list_of_new_cadet_ids=new_cadet_ids
    )

def update_cadet_connections_for_volunteer_with_list_of_cadet_ids(interface: abstractInterface,  event: Event, volunteer_id: str, list_of_new_cadet_ids: List[str]):
    volunteer_data = VolunteerAllocationData(interface.data)

    for cadet_id in list_of_new_cadet_ids:
        print("Adding association with cadet %s to existing volunteer %s" % (cadet_id, volunteer_id))
        volunteer_data.add_cadet_id_to_existing_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id, event=event)


def DEPRECATE_get_volunteer_at_event_with_id(event: Event, volunteer_id: str) -> VolunteerAtEvent:
    list_of_volunteers_at_event = DEPRECATED_load_list_of_volunteers_at_event(event)
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)

    return volunteer_at_event

def get_volunteer_at_event_with_id(interface: abstractInterface ,event: Event, volunteer_id: str) -> VolunteerAtEvent:
    list_of_volunteers_at_event = DEPRECATED_load_list_of_volunteers_at_event(event)
    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)

    return volunteer_at_event


def are_all_connected_cadets_cancelled_or_deleted(interface: abstractInterface ,volunteer_id: str, event: Event)-> bool:

    list_of_relevant_information =get_list_of_relevant_information(interface=interface, volunteer_id=volunteer_id, event=event)

    return list_of_relevant_information.all_cancelled_or_deleted()


def is_current_cadet_active_at_event(interface: abstractInterface, cadet_id: str, event: Event)-> bool:

    cadet_at_event = get_cadet_at_event_for_cadet_id(interface=interface, event=event, cadet_id=cadet_id)

    return cadet_at_event.is_active()


def get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(interface: abstractInterface,
                                                                               cadet_id: str, event: Event) \
        -> Dict[str, str]:

    ## list of volunteers at event
    list_of_volunteers_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id, interface=interface)
    list_of_relevant_volunteer_names_and_other_cadets = [get_volunteer_name_and_associated_cadets_for_event(
        interface=interface,
        event=event, volunteer_id=volunteer_id, cadet_id=cadet_id) for volunteer_id in list_of_volunteers_ids
    ]

    return dict([volunteer_and_any_other_cadets, id] for volunteer_and_any_other_cadets, id in
                zip(list_of_relevant_volunteer_names_and_other_cadets, list_of_volunteers_ids))



def are_any_volunteers_associated_with_cadet_at_event(interface: abstractInterface, cadet_id: str, event:Event):
    dict_of_relevant_volunteers = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
        interface=interface,
         cadet_id=cadet_id, event=event)

    return len(dict_of_relevant_volunteers)>0


def list_of_volunteers_for_cadet_identified(interface: abstractInterface, cadet_id: str, event: Event) -> List[str]:
    list_of_identified_volunteers_at_event = load_list_of_identified_volunteers_at_event(interface=interface, event=event)
    list_of_row_ids= list_of_row_ids_at_event_given_cadet_id(interface=interface, cadet_id=cadet_id, event=event)
    list_of_volunteer_ids=list_of_identified_volunteers_at_event.list_of_volunteer_ids_given_list_of_row_ids_excluding_unallocated(list_of_row_ids)

    return list_of_volunteer_ids



def get_list_of_relevant_information(interface: abstractInterface, volunteer_id: str, event: Event) -> ListOfRelevantInformationForVolunteer:

    list_of_identified_volunteers = list_of_identified_volunteers_with_volunteer_id(interface=interface, volunteer_id=volunteer_id, event=event) ## can appear more than once

    list_of_relevant_information = [get_relevant_information_for_volunteer_in_event_at_row_and_index(
        interface=interface,
        row_id=identified_volunteer.row_id,
        volunteer_index=identified_volunteer.volunteer_index,
        event=event
            ) for identified_volunteer in list_of_identified_volunteers]

    return ListOfRelevantInformationForVolunteer(list_of_relevant_information)


def get_list_of_volunteers_except_those_already_at_event(interface: abstractInterface, event: Event) -> ListOfVolunteers:
    volunteer_data = VolunteerAllocationData(interface.data)
    return volunteer_data.get_sorted_list_of_volunteers_except_those_already_at_event(event, SORT_BY_FIRSTNAME)

def matched_volunteer_or_missing_data(interface: abstractInterface, volunteer: Volunteer)-> Union[object, Volunteer]:
    volunteer_data = VolunteerData(interface.data)
    matched_volunteer_with_id = volunteer_data.matching_volunteer_or_missing_data(volunteer)

    return matched_volunteer_with_id