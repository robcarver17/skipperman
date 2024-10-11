from typing import List

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.frontend.forms import is_ready_to_swap
from app.OLD_backend.rota.sorting_and_filtering import RotaSortsAndFilters, \
    get_sorted_and_filtered_list_of_volunteers_at_event
from app.frontend.events.volunteer_rota.rota_allocation_inputs import get_allocation_inputs_for_volunteer
from app.frontend.events.volunteer_rota.volunteer_table_buttons import (
    get_location_button,
    get_skills_button,
    get_buttons_for_days_at_event,
    copy_previous_role_button_or_blank,
    get_volunteer_button_or_string,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    make_long_thing_detail_box, )

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import textInput

from app.objects.events import Event
from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent


def get_volunteer_table(
    event: Event, interface: abstractInterface, sorts_and_filters: RotaSortsAndFilters
) -> Table:
    ready_to_swap = is_ready_to_swap(interface)

    top_row = get_top_row_for_table(event=event, ready_to_swap=ready_to_swap)
    other_rows = get_body_of_table_at_event(
        event=event,
        interface=interface,
        ready_to_swap=ready_to_swap,
        sorts_and_filters=sorts_and_filters,
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
    sorts_and_filters: RotaSortsAndFilters,
    ready_to_swap: bool = False,
) -> List[RowInTable]:

    list_of_volunteers_at_event = (
        get_sorted_and_filtered_list_of_volunteers_at_event(
            cache=interface.cache,
            event=event,
            sorts_and_filters=sorts_and_filters,
        )
    )

    other_rows = [
        get_row_for_volunteer_at_event(
            ready_to_swap=ready_to_swap,
            interface=interface,
            volunteer_at_event=volunteer_at_event,
        )
        for volunteer_at_event in list_of_volunteers_at_event
    ]

    return other_rows


def get_row_for_volunteer_at_event(
    interface: abstractInterface,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    ready_to_swap: bool = False,
) -> RowInTable:
    first_part = get_first_part_of_row_for_volunteer_at_event(
        cache=interface.cache,
        volunteer_at_event=volunteer_at_event,
        ready_to_swap=ready_to_swap,
    )

    day_inputs = get_allocation_inputs_for_volunteer(interface=interface,
                                                     volunteer_at_event=volunteer_at_event,
                                                     ready_to_swap=ready_to_swap)

    last_part = get_last_part_of_row_for_volunteer_at_event(
        volunteer_at_event=volunteer_at_event, ready_to_swap=ready_to_swap
    )

    return RowInTable(first_part + day_inputs + last_part)


def get_first_part_of_row_for_volunteer_at_event(
    cache: AdHocCache,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    ready_to_swap: bool
) -> list:

    name_button = get_volunteer_button_or_string(volunteer_at_event=volunteer_at_event, ready_to_swap=ready_to_swap)
    location = get_location_button(
        cache=cache,
        volunteer_at_event=volunteer_at_event,
        ready_to_swap=ready_to_swap,
    )

    preferred = volunteer_at_event.preferred_duties
    same_different = volunteer_at_event.same_or_different
    skills_button = get_skills_button(
        cache=cache,
        volunteer=volunteer_at_event.volunteer,
        ready_to_swap=ready_to_swap,
    )
    previous_role_copy_button = copy_previous_role_button_or_blank(
        cache=cache,
        volunteer_at_event=volunteer_at_event,
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
    volunteer_at_event: DEPRECATE_VolunteerAtEvent, ready_to_swap: bool = False
) -> list:
    if ready_to_swap:
        return ["", ""]
    other_information = make_long_thing_detail_box(
        volunteer_at_event.any_other_information
    )
    notes = get_notes_input(volunteer_at_event=volunteer_at_event)

    return [notes, other_information]


def get_notes_input(volunteer_at_event: DEPRECATE_VolunteerAtEvent) -> textInput:
    return textInput(
        value=volunteer_at_event.notes,
        input_name=input_name_for_notes_and_volunteer(volunteer_at_event),
        input_label="",
    )


def input_name_for_notes_and_volunteer(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> str:
    return "NOTES_%s" % (volunteer_at_event.volunteer_id)
