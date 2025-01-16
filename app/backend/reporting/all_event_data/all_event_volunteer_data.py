import pandas as pd
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import ListOfCadets
from app.objects.exceptions import MissingData

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.backend.reporting.all_event_data.components import (
    ROW_ID,
    day_item_dict_as_string_or_single_if_identical,
)
from app.objects.day_selectors import empty_day_selector

from app.objects.events import Event

from app.backend.registration_data.identified_volunteers_at_event import get_list_of_identified_volunteers_at_event
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id


def get_df_for_volunteers_event_data_dump(object_store: ObjectStore, event: Event):
    list_of_identified_volunteers = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    list_of_row_ids = [
        identified_volunteer.row_id
        for identified_volunteer in list_of_identified_volunteers
    ]
    list_of_volunteer_ids = list_of_identified_volunteers.list_of_volunteer_ids()
    list_of_volunteers = ListOfVolunteers([
        get_volunteer_from_id(object_store=object_store, volunteer_id=volunteer_id) for volunteer_id in list_of_volunteer_ids
    ])

    list_of_volunteer_names = list_of_volunteers.list_of_names()

    list_of_connected_cadets = [
        get_connected_cadet_names(
            object_store=object_store, event=event,
            volunteer=volunteer,
        )
        for volunteer in list_of_volunteers
    ]

    list_of_availability = [
        data_from_volunteers_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            keyname="availablity",
            default=empty_day_selector,
        ).days_available_as_str()
        for volunteer in list_of_volunteers
    ]

    list_of_preferred_duties = [
        data_from_volunteers_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            keyname="preferred_duties",
            default="",
        )
        for volunteer in list_of_volunteers
    ]

    list_of_same_different = [
        data_from_volunteers_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            keyname="same_or_different",
            default="",
        )
        for volunteer in list_of_volunteers
    ]
    list_of_notes = [
        data_from_volunteers_at_event_data_or_empty(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            keyname="notes",
            default="",
        )
        for volunteer in list_of_volunteers
    ]

    list_of_skills = [
        get_skills_string(object_store=object_store,
                          volunteer=volunteer,
                          default="")
        for volunteer in list_of_volunteers
    ]
    list_of_role_group = [
        get_role_group(object_store=object_store,
 event=event,             volunteer=volunteer)
        for volunteer in list_of_volunteers
    ]
    list_of_boats = [
        get_patrol_boat(object_store=object_store,
 event=event,             volunteer=volunteer
)
        for volunteer in list_of_volunteers
    ]

    df = pd.DataFrame(
        {
            ROW_ID: list_of_row_ids,
            "Volunteer": list_of_volunteer_names,
            "Cadets": list_of_connected_cadets,
            "Availability": list_of_availability,
            "Preferred": list_of_preferred_duties,
            "Same or different": list_of_same_different,
            "Notes": list_of_notes,
            "Skills": list_of_skills,
            "Role and Group": list_of_role_group,
            "Patrol boat": list_of_boats,
        }
    )

    df = df.sort_values(ROW_ID)

    return df

from app.backend.registration_data.cadet_registration_data import get_dict_of_cadets_with_registration_data
from app.backend.volunteers.connected_cadets import get_list_of_cadets_associated_with_volunteer

def get_connected_cadet_names(
    object_store: ObjectStore,event: Event, volunteer: Volunteer, default=""
):
    registered_cadets = get_dict_of_cadets_with_registration_data(object_store=object_store, event=event).list_of_active_cadets()
    connected_cadets = get_list_of_cadets_associated_with_volunteer(object_store=object_store, volunteer=volunteer)

    connected_and_at_event = ListOfCadets([
        cadet for cadet in connected_cadets if cadet in registered_cadets
    ])
    names= connected_and_at_event.list_of_names()

    return ", ".join(names)

from app.backend.volunteers.skills import get_dict_of_existing_skills_for_volunteer

def get_skills_string(object_store: ObjectStore, volunteer: Volunteer, default=""):
    skills = get_dict_of_existing_skills_for_volunteer(object_store=object_store, volunteer=volunteer)
    return str(skills)

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import get_role_and_group_on_day_for_event_and_volunteer


def get_role_group(
    object_store: ObjectStore,  volunteer: Volunteer, event: Event, default=""
):

    role_dict = dict(
        [
            (
                day,
                str(get_role_and_group_on_day_for_event_and_volunteer(object_store=object_store,
                                                                  event=event,
                                                                  volunteer=volunteer,
                                                                  day=day))
            )
            for day in event.days_in_event()
        ]
    )

    return day_item_dict_as_string_or_single_if_identical(role_dict)

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import get_name_of_boat_allocated_to_volunteer_on_day_at_event

def get_patrol_boat(
    object_store: ObjectStore,  volunteer: Volunteer, event: Event, default=""
):
    boat_name_dict = dict(
        [
            (
                day,
                get_name_of_boat_allocated_to_volunteer_on_day_at_event(object_store=object_store,
                                                                event=event,
                                                                volunteer=volunteer,
                                                                day=day,
                                                                default=default),
            )
            for day in event.days_in_event()
        ]
    )
    return day_item_dict_as_string_or_single_if_identical(boat_name_dict)

from app.backend.registration_data.volunteer_registration_data import get_dict_of_registration_data_for_volunteers_at_event

def data_from_volunteers_at_event_data_or_empty(
    object_store: ObjectStore,
    event: Event,
        volunteer: Volunteer,    keyname: str,
    default="",
):
    volunteers_at_event_data = get_dict_of_registration_data_for_volunteers_at_event(object_store=object_store, event=event)
    try:
        data_for_volunteer = volunteers_at_event_data.get_data_for_volunteer(volunteer=volunteer)
    except MissingData:
        return default

    return getattr(
        data_for_volunteer, keyname
    )
