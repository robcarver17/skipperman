
from typing import List

from app.backend.volunteers.volunteer_rota import dict_of_groups_for_dropdown, \
    dict_of_roles_for_dropdown, sort_volunteer_data_for_event_by_name_sort_order, \
    sort_volunteer_data_for_event_by_day_sort_order
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody, get_data_to_be_stored
from app.backend.volunteers.volunteers import get_volunteer_from_volunteer_id
from app.logic.events.volunteer_rota.volunteer_table_buttons import get_location_button, get_skills_button, \
    get_unavailable_button_value_for_volunteer_on_day, copy_button_value_for_volunteer_in_role_on_day, \
    get_buttons_for_days_at_event
from app.objects.abstract_objects.abstract_lines import Line

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput

from app.objects.events import Event
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.objects.day_selectors import Day
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent

from app.objects.constants import arg_not_passed

def get_volunteer_table(event: Event,
                        sort_by_volunteer_name: str=arg_not_passed,
                        sort_by_day: Day=arg_not_passed
                        )-> Table:
    top_row = get_top_row_for_table(event)
    other_rows = get_body_of_table_at_event(event=event,
                                            sort_by_volunteer_name=sort_by_volunteer_name,
                                            sort_by_day=sort_by_day)

    return Table(
        [top_row]+other_rows
    )


def get_top_row_for_table(event: Event) -> RowInTable:
    buttons_for_days_at_event_as_str = get_buttons_for_days_at_event(event)

    return RowInTable([
        "Volunteer (click to edit food/days)",
        "Cadet location (click to edit connections)",
        "Preferred duties",
        "Same/different preference",
        "Skills",
        "Previous role"
    ]+buttons_for_days_at_event_as_str+
    ["Other information from registration"]
                      )


def get_body_of_table_at_event(event: Event,
                               sort_by_volunteer_name: str=arg_not_passed,
                               sort_by_day: Day=arg_not_passed
                               ) -> List[RowInTable]:

    data_to_be_stored = get_data_to_be_stored(event)

    list_of_volunteers_at_event = get_sorted_list_of_volunteers_at_event(
        data_to_be_stored=data_to_be_stored,
        sort_by_day=sort_by_day,
        sort_by_volunteer_name=sort_by_volunteer_name
    )

    other_rows = [get_row_for_volunteer_at_event(
                                                 volunteer_at_event=volunteer_at_event,
                                                 data_to_be_stored=data_to_be_stored)

                  for volunteer_at_event in list_of_volunteers_at_event]

    return other_rows

def get_sorted_list_of_volunteers_at_event(
        data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
        sort_by_volunteer_name: str=arg_not_passed,
                               sort_by_day: Day=arg_not_passed
                                ):

    list_of_volunteers_at_event = data_to_be_stored.list_of_volunteers_at_event

    if sort_by_volunteer_name is not arg_not_passed:
        list_of_volunteers_at_event = sort_volunteer_data_for_event_by_name_sort_order(
            list_of_volunteers_at_event, sort_order=sort_by_volunteer_name)
    elif sort_by_day is not arg_not_passed:
        print("SORTBY %s" % sort_by_day.name)
        list_of_volunteers_at_event = sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event, sort_by_day=sort_by_day,
            data_to_be_stored=data_to_be_stored)

    return list_of_volunteers_at_event

def get_row_for_volunteer_at_event(data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
                                   volunteer_at_event: VolunteerAtEvent) -> RowInTable:

    volunteer = get_volunteer_from_volunteer_id(volunteer_at_event.volunteer_id)
    name_button = Button(volunteer.name)
    location = get_location_button(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event)
    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different
    other_information = volunteer_at_event.any_other_information
    skills_button = get_skills_button(volunteer=volunteer, data_to_be_stored=data_to_be_stored)
    previous = data_to_be_stored.dict_of_volunteers_with_last_roles[volunteer_at_event.volunteer_id]

    day_inputs = [get_allocation_inputs_for_day_and_volunteer(
        data_to_be_stored=data_to_be_stored,
        volunteer_at_event=volunteer_at_event,
        day=day
    ) for day in data_to_be_stored.event.weekdays_in_event()]

    return RowInTable([
        name_button,
        location,
        preferred,
        same_different,
        skills_button,
        previous
    ]+day_inputs+
    [other_information])



def get_allocation_inputs_for_day_and_volunteer(volunteer_at_event: VolunteerAtEvent,
                                                 day: Day,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingTableBody
                                                 ) -> Line:

    volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(day)
    volunteer_in_role_at_event_on_day = data_to_be_stored.volunteer_in_role_at_event_on_day(
        day=day,
        volunteer_id=volunteer_at_event.volunteer_id
    )
    if volunteer_available_on_day:
        return get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_in_role_at_event_on_day,
                                                                          data_to_be_stored=data_to_be_stored)
    else:
        unavailable_button = Button("Make available", value=get_unavailable_button_value_for_volunteer_on_day(
            volunteer_id=volunteer_at_event.volunteer_id,
            day=day
        ))
        return Line([unavailable_button])


def get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingTableBody) -> Line:

    role_input = get_allocation_input_for_role(volunteer_in_role_at_event_on_day)
    group_input = get_allocation_input_for_group(volunteer_in_role_at_event_on_day)
    copy_button = Button(label="Copy", value = copy_button_value_for_volunteer_in_role_on_day(
        volunteer_in_role_at_event_on_day
    ))

    no_role_set = volunteer_in_role_at_event_on_day.no_role_set
    group_required_given_role = volunteer_in_role_at_event_on_day.requires_group
    copy_button_required = not data_to_be_stored.all_roles_match_across_event(volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id)

    all_elements = [role_input] ## always have this

    if no_role_set:
        pass
    else:
        ## if no role, then no need for a copy or group button
        if group_required_given_role:
            all_elements.append(group_input)
        if copy_button_required:
            all_elements.append(copy_button)

    return Line(all_elements)


def get_allocation_input_for_role(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> dropDownInput:
    return dropDownInput(
        input_label = "",
        input_name=input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_roles_for_dropdown(),
        default_label=volunteer_in_role_at_event_on_day.role
    )

def input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return "ROLE_%s_%s" % (volunteer_in_role_at_event_on_day.volunteer_id,
                           volunteer_in_role_at_event_on_day.day.name)


def get_allocation_input_for_group(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> dropDownInput:
    return dropDownInput(
        input_label = "",
        input_name=input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_groups_for_dropdown(),
        default_label=volunteer_in_role_at_event_on_day.group.group_name
    )

def input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return "GROUP_%s_%s" % (volunteer_in_role_at_event_on_day.volunteer_id,
                            volunteer_in_role_at_event_on_day.day.name)

