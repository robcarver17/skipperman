from typing import Union

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_last_role_or_none_for_volunteer_at_previous_events,
)
from app.data_access.store.object_store import ObjectStore

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)

from app.data_access.configuration.fixed import (
    COPY_OVERWRITE_SYMBOL,
    COPY_FILL_SYMBOL,
    NOT_AVAILABLE_SHORTHAND,
    REMOVE_SHORTHAND,
)
from app.frontend.events.volunteer_rota.button_values import (
    button_value_for_day,
    name_of_volunteer_button,
    copy_overwrite_button_value_for_volunteer_in_role_on_day,
    copy_fill_button_value_for_volunteer_in_role_on_day,
    unavailable_button_value_for_volunteer_in_role_on_day,
    remove_role_button_value_for_volunteer_in_role_on_day,
    copy_previous_role_button_name_from_volunteer_id,
    location_button_name_from_volunteer_id,
    skills_button_name_from_volunteer_id,
)
from app.frontend.events.volunteer_rota.swapping import get_swap_button, has_role_on_day

from app.objects.abstract_objects.abstract_lines import Line

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.rota.volunteer_table import (
    all_roles_and_groups_match_across_event,
    volunteer_has_empty_available_days_without_role,
    volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match,
)

from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    get_cadet_location_string_for_volunteer,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import Volunteer


def get_location_button(
    object_store: ObjectStore,
    volunteer_data_at_event: AllEventDataForVolunteer,
    ready_to_swap: bool,
) -> Button:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=volunteer_data_at_event.event
    )

    location = get_cadet_location_string_for_volunteer(
        volunteer_data_at_event=volunteer_data_at_event,
        cadets_at_event_data=cadets_at_event_data,
    )

    if ready_to_swap:
        return location

    return Button(
        label=location,
        value=location_button_name_from_volunteer_id(
            volunteer_data_at_event.volunteer.id
        ),
    )


def get_skills_button(
    volunteer_data_at_event: AllEventDataForVolunteer,
    ready_to_swap: bool,
) -> Button:
    dict_of_skills = volunteer_data_at_event.volunteer_skills
    skill_label = dict_of_skills.skills_held_as_str()
    if len(skill_label)==0:
        skill_label = "Click to add skills"

    if ready_to_swap:
        return skill_label
    return Button(
        label=skill_label,
        value=skills_button_name_from_volunteer_id(
            volunteer_id=volunteer_data_at_event.volunteer.id
        ),
    )


def copy_previous_role_button_or_blank(
    object_store: ObjectStore,
    volunteer_data_at_event: AllEventDataForVolunteer,
    ready_to_swap: bool,
) -> Union[Button, str]:
    previous_role = get_last_role_or_none_for_volunteer_at_previous_events(
        object_store=object_store,
        avoid_event=volunteer_data_at_event.event,
        volunteer=volunteer_data_at_event.volunteer,
    )
    if previous_role is None:
        return ""

    if ready_to_swap:
        return str(previous_role)

    return Button(
        label=str(previous_role),
        value=copy_previous_role_button_name_from_volunteer_id(
            volunteer_data_at_event.volunteer.id
        ),
    )


#


### SORT BUTTONS
def get_buttons_for_days_at_event(event: Event, ready_to_swap: bool):
    if ready_to_swap:
        return event.days_in_event_as_list_of_string()
    else:
        return [
            Line([button_for_day(day), " (click to sort group/role)"])
            for day in event.days_in_event()
        ]


def button_for_day(day: Day) -> Button:
    return Button(day.name, value=button_value_for_day(day))


def get_volunteer_button_or_string(volunteer: Volunteer, ready_to_swap: bool):
    if ready_to_swap:
        return volunteer.name
    else:
        return Button(label=volunteer.name, value=name_of_volunteer_button(volunteer))


def get_allocation_inputs_buttons_in_role_when_available(
    interface: abstractInterface,
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
    ready_to_swap: bool,
) -> list:
    ## create the buttons
    make_unavailable_button = get_make_unavailable_button_for_volunteer(
        volunteer_data_at_event=volunteer_data_at_event, day=day
    )
    remove_role_button = get_remove_role_button_for_volunteer(
        volunteer_data_at_event=volunteer_data_at_event, day=day
    )
    swap_button = get_swap_button(
        volunteer_data_at_event=volunteer_data_at_event,
        day=day,
        interface=interface,
    )

    no_role_set = not has_role_on_day(
        volunteer_data_at_event=volunteer_data_at_event, current_day=day
    )
    if no_role_set:
        ## if no role, then no need for a copy swap or group button
        if ready_to_swap:
            return []
        else:
            return [make_unavailable_button]

    if ready_to_swap:
        ## If hiding, then we're halfway through swapping and that's all we will see
        return [swap_button]

    all_buttons = get_copy_buttons_for_volunteer(
        volunteer_data_at_event=volunteer_data_at_event, day=day
    )
    all_buttons.append(swap_button)
    all_buttons.append(remove_role_button)
    all_buttons.append(make_unavailable_button)

    return all_buttons


def get_copy_buttons_for_volunteer(
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
):
    any_copy_possible = not all_roles_and_groups_match_across_event(volunteer_data_at_event)

    copy_fill_possible = volunteer_has_empty_available_days_without_role(
        volunteer_data_at_event
    )
    copy_ovewrite_required = (
        not volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match(
            volunteer_data_at_event
        )
    )

    overwrite_copy_button = get_overwrite_copy_button_for_volunteer(
        volunteer=volunteer_data_at_event.volunteer, day=day
    )
    fill_copy_button = get_fill_copy_button_for_volunteer(
        volunteer=volunteer_data_at_event.volunteer, day=day
    )

    all_buttons = []
    if any_copy_possible:
        if copy_ovewrite_required:
            all_buttons.append(overwrite_copy_button)
        if copy_fill_possible:
            all_buttons.append(fill_copy_button)

    return all_buttons


def get_overwrite_copy_button_for_volunteer(
    volunteer: Volunteer,
    day: Day,
) -> Button:
    return Button(
        label=COPY_OVERWRITE_SYMBOL,
        value=copy_overwrite_button_value_for_volunteer_in_role_on_day(
            volunteer=volunteer, day=day
        ),
    )


def get_fill_copy_button_for_volunteer(
    volunteer: Volunteer,
    day: Day,
) -> Button:
    return Button(
        label=COPY_FILL_SYMBOL,
        value=copy_fill_button_value_for_volunteer_in_role_on_day(
            volunteer=volunteer, day=day
        ),
    )


def get_make_unavailable_button_for_volunteer(
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
) -> Button:
    return Button(
        label=NOT_AVAILABLE_SHORTHAND,
        value=unavailable_button_value_for_volunteer_in_role_on_day(
            volunteer=volunteer_data_at_event.volunteer, day=day
        ),
    )


def get_remove_role_button_for_volunteer(
    volunteer_data_at_event: AllEventDataForVolunteer, day: Day
) -> Button:
    return Button(
        label=REMOVE_SHORTHAND,
        value=remove_role_button_value_for_volunteer_in_role_on_day(
            volunteer=volunteer_data_at_event.volunteer, day=day
        ),
    )
