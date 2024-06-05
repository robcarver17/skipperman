import pandas as pd
from app.backend.data.volunteers import VolunteerData

from app.objects.volunteers_at_event import NO_VOLUNTEER_ALLOCATED

from app.backend.cadets import cadet_name_from_id
from app.backend.reporting.all_event_data.components import ROW_ID, day_item_dict_as_string_or_single_if_identical
from app.objects.day_selectors import EMPTY_DAY_SELECTOR

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.backend.data.volunteer_allocation import VolunteerAllocationData
from app.backend.data.volunteer_rota import VolunteerRotaData
from app.backend.volunteers.volunteers import get_volunteer_name_from_id, get_dict_of_existing_skills
from app.backend.data.patrol_boats import PatrolBoatsData

def get_df_for_volunteers_event_data_dump(
        interface: abstractInterface,
        event: Event
):

    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    list_of_identified_volunteers = volunteers_at_event_data.load_list_of_identified_volunteers_at_event(event)
    list_of_row_ids = [identified_volunteer.row_id for identified_volunteer in list_of_identified_volunteers]
    list_of_volunteer_ids = list_of_identified_volunteers.list_of_volunteer_ids_including_unallocated()
    list_of_volunteer_names = [get_volunteer_name_or_not_allocated(interface=interface, volunteer_id=volunteer_id) for volunteer_id in list_of_volunteer_ids]
    list_of_connected_cadets = [get_connected_cadet_names(interface=interface, event=event, volunteer_id=volunteer_id) for volunteer_id in list_of_volunteer_ids]

    list_of_availability = [data_from_volunteers_at_event_data_or_empty(interface=interface, event=event, volunteer_id=volunteer_id, keyname='availablity', default=EMPTY_DAY_SELECTOR).days_available_as_str()
                            for volunteer_id in list_of_volunteer_ids]

    list_of_preferred_duties = [data_from_volunteers_at_event_data_or_empty(interface=interface, event=event, volunteer_id=volunteer_id, keyname='preferred_duties', default='')
                            for volunteer_id in list_of_volunteer_ids]

    list_of_same_different = [data_from_volunteers_at_event_data_or_empty(interface=interface, event=event, volunteer_id=volunteer_id, keyname='same_or_different', default='')
                            for volunteer_id in list_of_volunteer_ids]
    list_of_notes = [data_from_volunteers_at_event_data_or_empty(interface=interface, event=event, volunteer_id=volunteer_id, keyname='notes', default='')
                            for volunteer_id in list_of_volunteer_ids]


    list_of_skills = [get_skills_string(interface=interface, volunteer_id=volunteer_id, default='')
                            for volunteer_id in list_of_volunteer_ids]
    list_of_role_group = [get_role_group(interface=interface, event=event, volunteer_id=volunteer_id) for volunteer_id in list_of_volunteer_ids]
    list_of_boats = [get_patrol_boat(interface=interface, event=event, volunteer_id=volunteer_id) for volunteer_id in list_of_volunteer_ids]

    df = pd.DataFrame({ROW_ID: list_of_row_ids,
                         'Volunteer': list_of_volunteer_names,
                       'Cadets': list_of_connected_cadets,
                       'Availability': list_of_availability,
                       'Preferred': list_of_preferred_duties,
                       'Same or different': list_of_same_different,
                       'Notes': list_of_notes,
                       'Skills': list_of_skills,
                       'Role and Group': list_of_role_group,
                       'Patrol boat': list_of_boats
                       })

    df = df.sort_values(ROW_ID)

    return df

def get_volunteer_name_or_not_allocated(interface: abstractInterface, volunteer_id: str):
    if volunteer_id==NO_VOLUNTEER_ALLOCATED:
        return 'No volunteer on this row'
    else:
        return get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)

def get_connected_cadet_names(interface: abstractInterface, event: Event, volunteer_id: str, default=''):
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    list_of_volunteers_at_event = volunteers_at_event_data.load_list_of_volunteers_at_event(event)
    if not volunteer_id in list_of_volunteers_at_event.list_of_volunteer_ids:
        return default

    volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    names = [cadet_name_from_id(interface=interface, cadet_id=cadet_id) for cadet_id in list_of_cadet_ids]

    return ", ".join(names)

def get_skills_string(interface: abstractInterface,volunteer_id: str, default=''):
    volunteer_data = VolunteerData(interface.data)
    skills =volunteer_data.get_dict_of_existing_skills_for_volunteer_id(volunteer_id=volunteer_id)
    skills_held = [skill for skill, skill_held in skills.items() if skill_held]

    return ", ".join(skills_held)

def get_role_group(interface: abstractInterface,volunteer_id: str, event: Event, default=''):
    volunteer_rota_data =VolunteerRotaData(interface.data)
    role_dict = dict([(day, volunteer_rota_data.get_volunteer_role_at_event_on_day(event=event, day=day, volunteer_id=volunteer_id)+" "+\
                volunteer_rota_data.get_volunteer_group_name_at_event_on_day(event=event, day=day, volunteer_id=volunteer_id,
                                                                             default_if_missing=default, default_if_unallocated=default))
                 for day in event.weekdays_in_event()])

    return day_item_dict_as_string_or_single_if_identical(role_dict)

def get_patrol_boat(interface: abstractInterface,volunteer_id: str, event: Event, default=''):
    patrol_boat_data = PatrolBoatsData(interface.data)
    boat_name_dict = dict([
        (day, patrol_boat_data.get_boat_name_allocated_to_volunteer_on_day_at_event(event=event, day=day, volunteer_id=volunteer_id, default=default))
                            for day in event.weekdays_in_event()])
    return day_item_dict_as_string_or_single_if_identical(boat_name_dict)

def data_from_volunteers_at_event_data_or_empty(interface: abstractInterface, event: Event, volunteer_id: str, keyname: str, default=''):
    volunteers_at_event_data = VolunteerAllocationData(interface.data)

    list_of_volunteers_at_event = volunteers_at_event_data.load_list_of_volunteers_at_event(event)
    if not volunteer_id in list_of_volunteers_at_event.list_of_volunteer_ids:
        return default

    return getattr(list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id), keyname)
