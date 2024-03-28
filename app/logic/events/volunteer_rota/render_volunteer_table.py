
from typing import List, Union

from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.volunteer_rota import dict_of_groups_for_dropdown, \
    dict_of_roles_for_dropdown, get_sorted_and_filtered_list_of_volunteers_at_event
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingTableBody, get_data_to_be_stored, \
    RotaSortsAndFilters
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.data_access.configuration.configuration import VOLUNTEER_SKILLS
from app.data_access.configuration.fixed import COPY_SYMBOL1, NOT_AVAILABLE_SHORTHAND, AVAILABLE_SHORTHAND
from app.logic.events.volunteer_rota.rota_state import get_skills_filter_from_state
from app.logic.events.volunteer_rota.volunteer_table_buttons import get_location_button, get_skills_button, \
    make_available_button_value_for_volunteer_on_day, copy_button_value_for_volunteer_in_role_on_day, \
    get_buttons_for_days_at_event, unavailable_button_value_for_volunteer_in_role_on_day, remove_role_button_value_for_volunteer_in_role_on_day
from app.logic.events.volunteer_rota.swapping import get_swap_button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput, textInput, checkboxInput

from app.objects.events import Event
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.objects.day_selectors import Day
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent

SKILLS_FILTER = "skills_filter"

def get_volunteer_skills_filter(interface: abstractInterface):
    dict_of_labels = dict([(skill, skill) for skill in VOLUNTEER_SKILLS])
    dict_of_checked = get_skills_filter_from_state(interface)
    return checkboxInput(input_label="Filter for volunteers with these skills",
                         dict_of_checked=dict_of_checked,
                         dict_of_labels=dict_of_labels,
                         input_name=SKILLS_FILTER,
                         line_break=False)


def get_volunteer_table(event: Event,
                        interface: abstractInterface,
                        sorts_and_filters: RotaSortsAndFilters
                        )-> Table:
    hide_buttons = is_ready_to_swap(interface)

    top_row = get_top_row_for_table(event=event, hide_buttons=hide_buttons, interface=interface)
    other_rows = get_body_of_table_at_event(event=event,
                                            interface=interface,
                                            hide_buttons=hide_buttons,
                                            sorts_and_filters=sorts_and_filters)

    return Table(
        [top_row]+other_rows,
        has_column_headings=True, has_row_headings=True
    )


def get_top_row_for_table(interface: abstractInterface, event: Event, hide_buttons: bool) -> RowInTable:
    buttons_for_days_at_event_as_str = get_buttons_for_days_at_event(event=event, hide_buttons=hide_buttons)

    return RowInTable([
        "Volunteer (click to edit days available)",
        "Cadet location (click to edit connections)",
        "Preferred duties",
        "Same/different preference",
        "Skills",
        "Previous role"
    ]+buttons_for_days_at_event_as_str+
    ["Notes",
     "Other information from registration"]
                      )


def get_body_of_table_at_event(event: Event,
                               interface: abstractInterface,
                               sorts_and_filters: RotaSortsAndFilters,
                               hide_buttons: bool = False

                               ) -> List[RowInTable]:

    data_to_be_stored = get_data_to_be_stored(event)

    list_of_volunteers_at_event = get_sorted_and_filtered_list_of_volunteers_at_event(
        data_to_be_stored=data_to_be_stored,
        sorts_and_filters=sorts_and_filters
    )

    other_rows = [get_row_for_volunteer_at_event(hide_buttons=hide_buttons,
                                                 volunteer_at_event=volunteer_at_event,
                                                 data_to_be_stored=data_to_be_stored,
                                                 interface=interface)

                  for volunteer_at_event in list_of_volunteers_at_event]

    return other_rows


def get_row_for_volunteer_at_event(data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
                                   volunteer_at_event: VolunteerAtEvent,
                                   interface: abstractInterface,
                                   hide_buttons:bool= False) -> RowInTable:

    volunteer = get_volunteer_from_id(volunteer_at_event.volunteer_id)
    volunteer_name = volunteer.name

    name_button =  volunteer_name if hide_buttons else Button(volunteer_name)
    location = get_location_button(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event, hide_buttons=hide_buttons)
    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different
    other_information = volunteer_at_event.any_other_information
    notes = get_notes_input(volunteer_at_event=volunteer_at_event)
    skills_button = get_skills_button(volunteer=volunteer, data_to_be_stored=data_to_be_stored, hide_buttons=hide_buttons)
    previous = data_to_be_stored.dict_of_volunteers_with_last_roles[volunteer_at_event.volunteer_id]

    day_inputs = [get_allocation_inputs_for_day_and_volunteer(
        hide_buttons=hide_buttons,
        data_to_be_stored=data_to_be_stored,
        volunteer_at_event=volunteer_at_event,
        day=day,
        interface=interface
    ) for day in data_to_be_stored.event.weekdays_in_event()]

    return RowInTable([
        name_button,
        location,
        preferred,
        same_different,
        skills_button,
        previous
    ]+day_inputs+
    [notes, other_information])



def get_allocation_inputs_for_day_and_volunteer(volunteer_at_event: VolunteerAtEvent,
                                                 day: Day,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
                                                hide_buttons: bool,
                                                interface: abstractInterface
                                                 ) -> Line:

    volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(day)
    volunteer_in_role_at_event_on_day = data_to_be_stored.volunteer_in_role_at_event_on_day(
        day=day,
        volunteer_id=volunteer_at_event.volunteer_id
    )
    if volunteer_available_on_day:
        return get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_in_role_at_event_on_day,
                                                                          data_to_be_stored=data_to_be_stored,
                                                                          hide_buttons=hide_buttons,
                                                                          interface=interface)
    else:
        if hide_buttons:
            return Line(["Unavailable"])
        else:
            make_available_button = Button("Make available", value=make_available_button_value_for_volunteer_on_day(
                volunteer_id=volunteer_at_event.volunteer_id,
                day=day
            ))
            return Line([make_available_button])



def get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingTableBody,
                                                               interface: abstractInterface,
                                                               hide_buttons: bool) -> Line:

    role_input = get_allocation_input_for_role(volunteer_in_role_at_event_on_day, hide_buttons=hide_buttons)
    group_input = get_allocation_input_for_group(volunteer_in_role_at_event_on_day, hide_buttons=hide_buttons)
    copy_button = Button(label=COPY_SYMBOL1, value = copy_button_value_for_volunteer_in_role_on_day(
        volunteer_in_role_at_event_on_day
    ))
    swap_button = get_swap_button(volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day, interface=interface)
    make_unavailable_button = Button(label=NOT_AVAILABLE_SHORTHAND, value = unavailable_button_value_for_volunteer_in_role_on_day(
        volunteer_in_role_at_event_on_day
    ))
    remove_role_button =  Button(label=AVAILABLE_SHORTHAND, value = remove_role_button_value_for_volunteer_in_role_on_day(
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
        if copy_button_required and not hide_buttons:
            all_elements.append(copy_button)
        all_elements.append(swap_button)
        if not hide_buttons:
            all_elements.append(remove_role_button)
            all_elements.append(make_unavailable_button)

    return Line(all_elements)


def get_allocation_input_for_role(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent, hide_buttons: bool) -> Union[dropDownInput, str]:
    if hide_buttons:
        return volunteer_in_role_at_event_on_day.role
    return dropDownInput(
        input_label = "",
        input_name=input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_roles_for_dropdown(),
        default_label=volunteer_in_role_at_event_on_day.role
    )

def input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return "ROLE_%s_%s" % (volunteer_in_role_at_event_on_day.volunteer_id,
                           volunteer_in_role_at_event_on_day.day.name)


def get_allocation_input_for_group(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent, hide_buttons: bool) -> dropDownInput:
    if hide_buttons:
        return volunteer_in_role_at_event_on_day.group.group_name

    return dropDownInput(
        input_label = "",
        input_name=input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_groups_for_dropdown(),
        default_label=volunteer_in_role_at_event_on_day.group.group_name
    )

def input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return "GROUP_%s_%s" % (volunteer_in_role_at_event_on_day.volunteer_id,
                            volunteer_in_role_at_event_on_day.day.name)




def get_notes_input(volunteer_at_event: VolunteerAtEvent) -> textInput:
    return textInput(
        value=volunteer_at_event.notes,
        input_name=input_name_for_notes_and_volunteer(volunteer_at_event),
        input_label=""
    )

def input_name_for_notes_and_volunteer(volunteer_at_event: VolunteerAtEvent) -> str:
    return "NOTES_%s" % (volunteer_at_event.volunteer_id)
