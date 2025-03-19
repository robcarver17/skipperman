from typing import List

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer, \
    DictOfAllEventDataForVolunteers
from app.objects.volunteers import Volunteer

from app.frontend.forms.swaps import is_ready_to_swap
from app.backend.rota.sorting_and_filtering import (
    RotaSortsAndFilters,
    get_sorted_and_filtered_dict_of_volunteers_at_event,
)
from app.frontend.events.volunteer_rota.rota_allocation_inputs import (
    get_allocation_inputs_for_volunteer,
)
from app.frontend.events.volunteer_rota.volunteer_table_buttons import (
    get_location_button,
    get_skills_button,
    get_buttons_for_days_at_event,
    copy_previous_role_button_or_blank,
    get_volunteer_name_cell,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    make_long_thing_detail_box,
)

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import textInput

from app.objects.events import Event


def get_volunteer_table(
    event: Event, interface: abstractInterface, sorts_and_filters: RotaSortsAndFilters
) -> Table:
    dict_of_volunteers_at_event_with_event_data = (
        get_sorted_and_filtered_dict_of_volunteers_at_event(
            object_store=interface.object_store,
            event=event,
            sorts_and_filters=sorts_and_filters,
        )
    )
    if len(dict_of_volunteers_at_event_with_event_data)==0:
        return Table([])

    ready_to_swap = is_ready_to_swap(interface)

    top_row = get_top_row_for_table(event=event, ready_to_swap=ready_to_swap)
    other_rows = get_body_of_table_at_event(
        event=event,
        interface=interface,
        ready_to_swap=ready_to_swap,
        dict_of_volunteers_at_event_with_event_data=dict_of_volunteers_at_event_with_event_data
    )

    return Table(
        [top_row] + other_rows, has_column_headings=True, has_row_headings=True
    )


def get_top_row_for_table(event: Event, ready_to_swap: bool) -> RowInTable:
    buttons_for_days_at_event_as_str = get_buttons_for_days_at_event(
        event=event, ready_to_swap=ready_to_swap
    )

    return RowInTable(
        [
            "Volunteer (click to edit days available/ )",
            "Cadet location (click to edit connections)",
            "Preferred duties from form",
            "Same/different preference from form",
            "Skills (click to edit)",
            "Previous role (click to fill and overwrite over all days at this event)",
        ]
        + buttons_for_days_at_event_as_str
        + ["Volunteer notes (editable)", "Other information from registration"]
    )


def get_body_of_table_at_event(
    event: Event,
    interface: abstractInterface,
    dict_of_volunteers_at_event_with_event_data: DictOfAllEventDataForVolunteers,
    ready_to_swap: bool = False,
) -> List[RowInTable]:
    dict_of_all_cadet_event_data = get_dict_of_all_event_info_for_cadets(object_store=interface.object_store, event=event)

    other_rows = [
        get_row_for_volunteer_at_event(
            ready_to_swap=ready_to_swap,
            volunteer=volunteer,
            volunteer_data_at_event=volunteer_data_at_event,
            dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
            interface=interface,
        )
        for volunteer, volunteer_data_at_event in dict_of_volunteers_at_event_with_event_data.items()
    ]

    return other_rows


def get_row_for_volunteer_at_event(
    interface: abstractInterface,
    volunteer: Volunteer,
    volunteer_data_at_event: AllEventDataForVolunteer,
dict_of_all_cadet_event_data: DictOfAllEventInfoForCadets,

    ready_to_swap: bool = False,
) -> RowInTable:
    first_part = get_first_part_of_row_for_volunteer_at_event(
        interface=interface,
        volunteer=volunteer,
        volunteer_data_at_event=volunteer_data_at_event,
        dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
        ready_to_swap=ready_to_swap,
    )

    day_inputs = get_allocation_inputs_for_volunteer(
        volunteer_data_at_event=volunteer_data_at_event,
        ready_to_swap=ready_to_swap,
        interface=interface,
    )

    last_part = get_last_part_of_row_for_volunteer_at_event(
        volunteer_data_at_event=volunteer_data_at_event, ready_to_swap=ready_to_swap
    )

    return RowInTable(first_part + day_inputs + last_part)


def get_first_part_of_row_for_volunteer_at_event(
    interface: abstractInterface,
    volunteer: Volunteer,
    volunteer_data_at_event: AllEventDataForVolunteer,
dict_of_all_cadet_event_data: DictOfAllEventInfoForCadets,
    ready_to_swap: bool,
) -> list:
    name_button = get_volunteer_name_cell(
        volunteer=volunteer, ready_to_swap=ready_to_swap
    )
    location = get_location_button(
        dict_of_all_cadet_event_data=dict_of_all_cadet_event_data,
        ready_to_swap=ready_to_swap,
        volunteer_data_at_event=volunteer_data_at_event,
    )

    preferred = volunteer_data_at_event.registration_data.preferred_duties
    same_different = volunteer_data_at_event.registration_data.same_or_different
    skills_button = get_skills_button(
        volunteer_data_at_event=volunteer_data_at_event,
        ready_to_swap=ready_to_swap,
    )
    previous_role_copy_button = copy_previous_role_button_or_blank(
        object_store=interface.object_store,
        volunteer_data_at_event=volunteer_data_at_event,
        ready_to_swap=ready_to_swap,
    )

    return [
        name_button,
        location,
        preferred,
        same_different,
        skills_button,
        previous_role_copy_button,
    ]


def get_last_part_of_row_for_volunteer_at_event(
    volunteer_data_at_event: AllEventDataForVolunteer, ready_to_swap: bool = False
) -> list:
    if ready_to_swap:
        return ["", ""]
    other_information = make_long_thing_detail_box(
        volunteer_data_at_event.registration_data.any_other_information
    )
    notes = get_notes_input(volunteer_data_at_event)

    return [notes, other_information]


def get_notes_input(volunteer_data_at_event: AllEventDataForVolunteer) -> textInput:
    return textInput(
        value=volunteer_data_at_event.registration_data.notes,
        input_name=input_name_for_notes_and_volunteer(
            volunteer_data_at_event.volunteer
        ),
        input_label="",
    )


def input_name_for_notes_and_volunteer(
    volunteer: Volunteer,
) -> str:
    return "NOTES_%s" % volunteer.id
