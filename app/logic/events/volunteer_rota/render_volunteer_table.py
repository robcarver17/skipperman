
from typing import List, Union

from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.volunteer_rota import dict_of_groups_for_dropdown, \
    dict_of_roles_for_dropdown, get_sorted_and_filtered_list_of_volunteers_at_event
from app.backend.volunteers.volunteer_rota_data import DataToBeStoredWhilstConstructingVolunteerRotaPage, get_data_to_be_stored_for_volunteer_rota_page, \
    RotaSortsAndFilters
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.data_access.configuration.fixed import COPY_SYMBOL1, NOT_AVAILABLE_SHORTHAND, AVAILABLE_SHORTHAND
from app.logic.events.volunteer_rota.volunteer_table_buttons import get_location_button, get_skills_button, \
    make_available_button_value_for_volunteer_on_day, copy_button_value_for_volunteer_in_role_on_day, \
    get_buttons_for_days_at_event, unavailable_button_value_for_volunteer_in_role_on_day, remove_role_button_value_for_volunteer_in_role_on_day
from app.logic.events.volunteer_rota.swapping import get_swap_button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput, textInput

from app.objects.events import Event
from app.objects.volunteers_at_event import VolunteerAtEvent
from app.objects.day_selectors import Day
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent




def get_volunteer_table(event: Event,
                        interface: abstractInterface,
                        sorts_and_filters: RotaSortsAndFilters
                        )-> Table:
    ready_to_swap = is_ready_to_swap(interface)

    top_row = get_top_row_for_table(event=event, ready_to_swap=ready_to_swap)
    other_rows = get_body_of_table_at_event(event=event,
                                            interface=interface,
                                            ready_to_swap=ready_to_swap,
                                            sorts_and_filters=sorts_and_filters)

    return Table(
        [top_row]+other_rows,
        has_column_headings=True, has_row_headings=True
    )


def get_top_row_for_table(event: Event, ready_to_swap: bool) -> RowInTable:
    buttons_for_days_at_event_as_str = get_buttons_for_days_at_event(event=event, ready_to_swap=ready_to_swap)

    return RowInTable([
        "Volunteer (click to edit days available/ )",
        "Cadet location (click to edit connections)",
        "Preferred duties",
        "Same/different preference",
        "Skills (click to edit)",
        "Previous role"
    ]+buttons_for_days_at_event_as_str+
    ["Volunteer notes (editable)",
     "Other information from registration"]
                      )


def get_body_of_table_at_event(event: Event,
                               interface: abstractInterface,
                               sorts_and_filters: RotaSortsAndFilters,
                               ready_to_swap: bool = False

                               ) -> List[RowInTable]:

    data_to_be_stored = get_data_to_be_stored_for_volunteer_rota_page(interface=interface, event=event)

    list_of_volunteers_at_event = get_sorted_and_filtered_list_of_volunteers_at_event(
        data_to_be_stored=data_to_be_stored,
        sorts_and_filters=sorts_and_filters
    )

    other_rows = [get_row_for_volunteer_at_event(ready_to_swap=ready_to_swap,
                                                 volunteer_at_event=volunteer_at_event,
                                                 data_to_be_stored=data_to_be_stored,
                                                 interface=interface)

                  for volunteer_at_event in list_of_volunteers_at_event]

    return other_rows


def get_row_for_volunteer_at_event(data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                   volunteer_at_event: VolunteerAtEvent,
                                   interface: abstractInterface,
                                   ready_to_swap:bool= False) -> RowInTable:


    first_part = get_first_part_of_row_for_volunteer_at_event(data_to_be_stored=data_to_be_stored,
                                                              interface=interface,
                                                              ready_to_swap=ready_to_swap,
                                                              volunteer_at_event=volunteer_at_event)

    day_inputs = [get_allocation_inputs_for_day_and_volunteer(
        ready_to_swap=ready_to_swap,
        data_to_be_stored=data_to_be_stored,
        volunteer_at_event=volunteer_at_event,
        day=day,
        interface=interface
    ) for day in data_to_be_stored.event.weekdays_in_event()]

    last_part = get_last_part_of_row_for_volunteer_at_event(volunteer_at_event=volunteer_at_event,
                                                            ready_to_swap=ready_to_swap)

    return RowInTable(first_part+day_inputs+last_part)

def get_first_part_of_row_for_volunteer_at_event(data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                   volunteer_at_event: VolunteerAtEvent,
                                   interface: abstractInterface,
                                   ready_to_swap:bool= False) -> list:

    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_at_event.volunteer_id)
    volunteer_name = volunteer.name

    name_button =  volunteer_name if ready_to_swap else Button(volunteer_name)
    location = get_location_button(data_to_be_stored=data_to_be_stored, volunteer_at_event=volunteer_at_event, ready_to_swap=ready_to_swap)

    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different
    skills_button = get_skills_button(volunteer=volunteer, data_to_be_stored=data_to_be_stored, ready_to_swap=ready_to_swap)
    previous = data_to_be_stored.dict_of_volunteers_with_last_roles[volunteer_at_event.volunteer_id]


    return [
        name_button,
        location,
        preferred,
        same_different,
        skills_button,
        previous
    ]


def get_last_part_of_row_for_volunteer_at_event(
                                   volunteer_at_event: VolunteerAtEvent,
                                    ready_to_swap: bool = False

) -> list:

    if ready_to_swap:
        return ['', '']
    other_information = volunteer_at_event.any_other_information
    notes = get_notes_input(volunteer_at_event=volunteer_at_event)

    return [notes, other_information]


def get_allocation_inputs_for_day_and_volunteer(volunteer_at_event: VolunteerAtEvent,
                                                day: Day,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                                ready_to_swap: bool,
                                                interface: abstractInterface
                                                ) -> Line:

    volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(day)
    if volunteer_available_on_day:
        return get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_at_event=volunteer_at_event,
                                                                          data_to_be_stored=data_to_be_stored,
                                                                          ready_to_swap=ready_to_swap,
                                                                          day=day,
                                                                          interface=interface)
    else:
        return get_allocation_inputs_for_day_and_volunteer_when_unavailable(
            day=day,
            volunteer_at_event=volunteer_at_event,
            ready_to_swap=ready_to_swap
        )


def get_allocation_inputs_for_day_and_volunteer_when_available(volunteer_at_event: VolunteerAtEvent,
                                                day: Day,
                                                data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                                ready_to_swap: bool,
                                                interface: abstractInterface
                                                ) -> Line:

    volunteer_in_role_at_event_on_day = data_to_be_stored.volunteer_in_role_at_event_on_day(
        day=day,
        volunteer_id=volunteer_at_event.volunteer_id
    )
    return get_allocation_inputs_for_day_and_volunteer_in_role_when_available(volunteer_in_role_at_event_on_day,
                                                                          data_to_be_stored=data_to_be_stored,
                                                                          ready_to_swap=ready_to_swap,
                                                                          interface=interface)


def get_allocation_inputs_for_day_and_volunteer_when_unavailable(volunteer_at_event: VolunteerAtEvent,
                                                day: Day,
                                                ready_to_swap: bool,
                                                ) -> Line:

    if ready_to_swap:
        return Line(["Unavailable"])
    else:
        make_available_button = Button("Make available", value=make_available_button_value_for_volunteer_on_day(
            volunteer_id=volunteer_at_event.volunteer_id,
            day=day
        ))
        return Line([make_available_button])



def get_allocation_inputs_for_day_and_volunteer_in_role_when_available(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                                               data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
                                                               interface: abstractInterface,
                                                               ready_to_swap: bool) -> Line:

    group_and_role_inputs = get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap
    )
    buttons = get_allocation_inputs_buttons_in_role_when_available(
        interface=interface,
        data_to_be_stored=data_to_be_stored,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap
    )
    return Line(group_and_role_inputs+buttons)

def get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                                               interface: abstractInterface,
                                                               ready_to_swap: bool) -> list:

    role_input = get_allocation_input_for_role(interface=interface, volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                               ready_to_swap=ready_to_swap)

    role_already_set = not volunteer_in_role_at_event_on_day.no_role_set
    group_required_given_role = volunteer_in_role_at_event_on_day.requires_group


    all_elements = [role_input] ## always have this

    if role_already_set and group_required_given_role:
        group_input = get_allocation_input_for_group(interface=interface, volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                                     ready_to_swap=ready_to_swap)
        all_elements.append(group_input)

    return all_elements


def get_allocation_inputs_buttons_in_role_when_available(
        volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
        data_to_be_stored: DataToBeStoredWhilstConstructingVolunteerRotaPage,
        interface: abstractInterface,
        ready_to_swap: bool) -> list:

    ## create the buttons
    make_unavailable_button = get_make_unavailable_button_for_volunteer(volunteer_in_role_at_event_on_day)
    copy_button = get_copy_button_for_volunteer(volunteer_in_role_at_event_on_day)
    remove_role_button = get_remove_role_button_for_volunteer(volunteer_in_role_at_event_on_day)
    swap_button = get_swap_button(volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                  interface=interface)


    no_role_set = volunteer_in_role_at_event_on_day.no_role_set
    if no_role_set:
        ## if no role, then no need for a copy swap or group button
        if ready_to_swap:
            return []
        else:
            return [make_unavailable_button]

    if ready_to_swap:
        ## If hiding, then we're halfway through swapping and that's all we will see
        return [swap_button]

    copy_button_required = not data_to_be_stored.all_roles_match_across_event(
        volunteer_id=volunteer_in_role_at_event_on_day.volunteer_id)

    all_buttons =[]
    if copy_button_required:
        all_buttons.append(copy_button)

    all_buttons.append(swap_button)
    all_buttons.append(remove_role_button)
    all_buttons.append(make_unavailable_button)

    return all_buttons

def get_copy_button_for_volunteer(        volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> Button:
    return Button(label=COPY_SYMBOL1, value=copy_button_value_for_volunteer_in_role_on_day(
        volunteer_in_role_at_event_on_day
    ))

def get_make_unavailable_button_for_volunteer(        volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> Button:
    return Button(label=NOT_AVAILABLE_SHORTHAND,
                                     value=unavailable_button_value_for_volunteer_in_role_on_day(
                                         volunteer_in_role_at_event_on_day
                                     ))

def get_remove_role_button_for_volunteer(        volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> Button:
    return  Button(label=AVAILABLE_SHORTHAND, value=remove_role_button_value_for_volunteer_in_role_on_day(
        volunteer_in_role_at_event_on_day
    ))


def get_allocation_input_for_role(interface: abstractInterface, volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                  ready_to_swap: bool) -> Union[dropDownInput, str]:
    dict_of_role_options = dict_of_roles_for_dropdown(interface)
    if ready_to_swap:
        return volunteer_in_role_at_event_on_day.role
    return dropDownInput(
        input_label = "",
        input_name=input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_role_options,
        default_label=volunteer_in_role_at_event_on_day.role
    )

def input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent) -> str:
    return "ROLE_%s_%s" % (volunteer_in_role_at_event_on_day.volunteer_id,
                           volunteer_in_role_at_event_on_day.day.name)


def get_allocation_input_for_group(interface: abstractInterface, volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent, ready_to_swap: bool) -> dropDownInput:
    if ready_to_swap:
        return " (%s)" % volunteer_in_role_at_event_on_day.group.group_name

    dict_of_group_options = dict_of_groups_for_dropdown(interface)

    return dropDownInput(
        input_label = "",
        input_name=input_name_for_group_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_group_options,
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


