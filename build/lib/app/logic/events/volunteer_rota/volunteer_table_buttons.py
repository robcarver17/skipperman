from typing import Tuple

from app.backend.data.volunteer_allocation import load_list_of_volunteers_at_event
from app.backend.volunteers.volunteer_rota import get_cadet_location_string, \
    str_dict_skills
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody
from app.backend.volunteers.volunteers import get_volunteer_from_volunteer_id
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import Volunteer
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent


def get_location_button(data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
                                   volunteer_at_event: VolunteerAtEvent) -> Button:
    location = get_cadet_location_string(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event)

    return Button(label=location,
                  value=location_button_name_from_volunteer_id(volunteer_at_event.volunteer_id))


def location_button_name_from_volunteer_id(volunteer_id: str) -> str:
    return "LOCATION_%s" % volunteer_id


def get_skills_button(volunteer: Volunteer,
                      data_to_be_stored: DataToBeStoredWhilstConstructingTableBody
                      )-> Button:
    return Button(label = str_dict_skills(volunteer=volunteer, data_to_be_stored=data_to_be_stored),
                  value = skills_button_name_from_volunteer_id(volunteer_id=volunteer.id))


def skills_button_name_from_volunteer_id(volunteer_id: str) -> str:
    return "SKILL_%s" % volunteer_id


def list_of_all_location_button_names(event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    return [location_button_name_from_volunteer_id(volunteer_at_event.volunteer_id)
            for volunteer_at_event in list_of_volunteers_at_event]


def list_of_all_skills_buttons(event: Event):
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    return [skills_button_name_from_volunteer_id(volunteer_at_event.volunteer_id)
            for volunteer_at_event in list_of_volunteers_at_event]


def from_location_button_to_volunteer_id(location_button_name: str) -> str:
    __, volunteer_id = location_button_name.split("_")

    return volunteer_id


def from_skills_button_to_volunteer_id(skills_button_name: str) -> str:
    __, volunteer_id = skills_button_name.split("_")

    return volunteer_id


def get_dict_of_volunteer_name_buttons_and_volunteer_ids(event: Event)-> dict:
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteer_ids = list_of_volunteers_at_event.list_of_volunteer_ids

    return dict([(
        get_volunteer_from_volunteer_id(volunteer_id).name,
        volunteer_id)
            for volunteer_id in list_of_volunteer_ids])


def get_unavailable_button_value_for_volunteer_on_day(volunteer_id: str,
                                                day: Day) -> str:
    return "UNAVAILABLE_%s_%s" % (volunteer_id, day.name)


def from_unavailable_button_value_to_volunteer_and_day(button_value:str) -> Tuple[str, Day]:
    __, volunteer_id, day_name = button_value.split("_")

    return volunteer_id, Day[day_name]


def get_list_of_unavailable_button_values(event: Event) -> list:
    ## Strictly speaking this will include buttons that aren't visible, but quicker and easier trhan checking
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteer_ids = list_of_volunteers_at_event.list_of_volunteer_ids
    list_of_days = event.weekdays_in_event()

    all_button_values =[]
    for id in list_of_volunteer_ids:
        for day in list_of_days:
            all_button_values.append(get_unavailable_button_value_for_volunteer_on_day(volunteer_id=id, day=day))

    return all_button_values

def copy_button_value_for_volunteer_in_role_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return copy_button_value_for_volunteer_id_and_day(volunteer_in_role_at_event_on_day.volunteer_id, volunteer_in_role_at_event_on_day.day)

def copy_button_value_for_volunteer_id_and_day(volunteer_id: str, day: Day) -> str:
    return "COPY_%s_%s" % (volunteer_id, day.name)

def from_copy_button_to_volunteer_id_and_day(copy_button_text: str) -> Tuple[str, Day]:
    __, id, day_name = copy_button_text.split("_")

    return id, Day[day_name]

def get_list_of_copy_buttons(event: Event):
    all_buttons = []
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteer_ids = list_of_volunteers_at_event.list_of_volunteer_ids
    for day in event.weekdays_in_event():
        for id in list_of_volunteer_ids:
            all_buttons.append(copy_button_value_for_volunteer_id_and_day(id, day))

    return all_buttons


def get_buttons_for_days_at_event(event: Event):
    buttons_for_days_at_event_as_str = [button_for_day(day) for day in event.weekdays_in_event()]
    return buttons_for_days_at_event_as_str


def button_for_day(day:Day) -> Button:
    return Button(day.name, value=button_value_for_day(day))


def button_value_for_day(day: Day):
    return "DAY_%s" % day.name

def get_list_of_day_button_values(event: Event):
    return [button_value_for_day(day) for day in event.weekdays_in_event()]

def from_day_button_value_to_day(day_button_value: str) -> Day:
    __, day_name = day_button_value.split("_")
    return Day[day_name]