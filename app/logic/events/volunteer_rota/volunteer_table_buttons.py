from typing import Union

from app.OLD_backend.rota.volunteer_history import get_previous_role_and_group_for_volunteer_at_event

from app.data_access.configuration.fixed import COPY_OVERWRITE_SYMBOL, COPY_FILL_SYMBOL, NOT_AVAILABLE_SHORTHAND, \
    REMOVE_SHORTHAND
from app.data_access.data_layer.ad_hoc_cache import AdHocCache
from app.logic.events.volunteer_rota.button_values import button_value_for_day, name_of_volunteer_button, \
    copy_overwrite_button_value_for_volunteer_in_role_on_day, copy_fill_button_value_for_volunteer_in_role_on_day, \
    unavailable_button_value_for_volunteer_in_role_on_day, remove_role_button_value_for_volunteer_in_role_on_day, \
    copy_previous_role_button_name_from_volunteer_id, location_button_name_from_volunteer_id, \
    skills_button_name_from_volunteer_id
from app.logic.events.volunteer_rota.swapping import get_swap_button

from app.objects.abstract_objects.abstract_lines import Line

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.rota.volunteer_rota import (
    all_roles_match_across_event, volunteer_has_empty_available_days_without_role,
    volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match,
)

from app.OLD_backend.rota.rota_cadet_and_volunteer_data import get_cadet_location_string, get_str_dict_skills
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.primtive_with_id.volunteers import Volunteer
from app.objects.volunteers_at_event import DEPRECATE_VolunteerAtEvent
from app.objects.primtive_with_id.volunteer_roles_and_groups import VolunteerWithIdInRoleAtEvent


def get_location_button(
    cache: AdHocCache,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    ready_to_swap: bool,
) -> Button:
    location = cache.get_from_cache(get_cadet_location_string,
         volunteer_at_event=volunteer_at_event
    )
    if ready_to_swap:
        return location

    return Button(
        label=location,
        value=location_button_name_from_volunteer_id(volunteer_at_event.volunteer_id),
    )


def get_skills_button(
        cache: AdHocCache,
    volunteer: Volunteer,
    ready_to_swap: bool,
) -> Button:
    skill_label = get_str_dict_skills(
        cache=cache,
        volunteer=volunteer,
    )
    if ready_to_swap:
        return skill_label
    return Button(
        label=skill_label,
        value=skills_button_name_from_volunteer_id(volunteer_id=volunteer.id),
    )



def copy_previous_role_button_or_blank(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    cache: AdHocCache,
    ready_to_swap: bool,
) -> Union[Button, str]:
    previous_role = get_previous_role_and_group_for_volunteer_at_event(cache=cache,
                                                                       volunteer_at_event=volunteer_at_event)

    if previous_role.missing:
        return ""
    if ready_to_swap:
        return str(previous_role)

    return Button(
        label=str(previous_role),
        value=copy_previous_role_button_name_from_volunteer_id(
            volunteer_at_event.volunteer_id
        ),
    )


#

### SORT BUTTONS
def get_buttons_for_days_at_event(event: Event, ready_to_swap: bool):
    if ready_to_swap:
        return event.weekdays_in_event_as_list_of_string()
    else:
        return [
            Line([button_for_day(day), " (click to sort group/role)"])
            for day in event.weekdays_in_event()
        ]


def button_for_day(day: Day) -> Button:
    return Button(day.name, value=button_value_for_day(day))


def get_volunteer_button_or_string(volunteer_at_event: DEPRECATE_VolunteerAtEvent, ready_to_swap:bool):
    if ready_to_swap:
        return volunteer_at_event.name
    else:
        return Button(name_of_volunteer_button(volunteer_at_event))


def get_allocation_inputs_buttons_in_role_when_available(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    event: Event,
    interface: abstractInterface,
    ready_to_swap: bool,
) -> list:
    ## create the buttons
    make_unavailable_button = get_make_unavailable_button_for_volunteer(
        volunteer_in_role_at_event_on_day
    )
    remove_role_button = get_remove_role_button_for_volunteer(
        volunteer_in_role_at_event_on_day
    )
    swap_button = get_swap_button(
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        interface=interface,
    )

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

    all_buttons = get_copy_buttons_for_volunteer(
        cache=interface.cache,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        event=event
    )
    all_buttons.append(swap_button)
    all_buttons.append(remove_role_button)
    all_buttons.append(make_unavailable_button)

    return all_buttons


def get_copy_buttons_for_volunteer(
    cache: AdHocCache,
        event: Event,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
):
    any_copy_possible = not all_roles_match_across_event(
        cache=cache,
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day
    )

    copy_fill_possible = (
        volunteer_has_empty_available_days_without_role(
            cache=cache,
            event=event,
            volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day
        )
    )
    copy_ovewrite_required = not volunteer_has_at_least_one_day_in_role_and_all_roles_and_groups_match(
        cache=cache,
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day
    )

    overwrite_copy_button = get_overwrite_copy_button_for_volunteer(
        volunteer_in_role_at_event_on_day
    )
    fill_copy_button = get_fill_copy_button_for_volunteer(
        volunteer_in_role_at_event_on_day
    )

    all_buttons = []
    if any_copy_possible:
        if copy_ovewrite_required:
            all_buttons.append(overwrite_copy_button)
        if copy_fill_possible:
            all_buttons.append(fill_copy_button)

    return all_buttons




def get_overwrite_copy_button_for_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> Button:
    return Button(
        label=COPY_OVERWRITE_SYMBOL,
        value=copy_overwrite_button_value_for_volunteer_in_role_on_day(
            volunteer_in_role_at_event_on_day
        ),
    )


def get_fill_copy_button_for_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> Button:
    return Button(
        label=COPY_FILL_SYMBOL,
        value=copy_fill_button_value_for_volunteer_in_role_on_day(
            volunteer_in_role_at_event_on_day
        ),
    )


def get_make_unavailable_button_for_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> Button:
    return Button(
        label=NOT_AVAILABLE_SHORTHAND,
        value=unavailable_button_value_for_volunteer_in_role_on_day(
            volunteer_in_role_at_event_on_day
        ),
    )


def get_remove_role_button_for_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> Button:
    return Button(
        label=REMOVE_SHORTHAND,
        value=remove_role_button_value_for_volunteer_in_role_on_day(
            volunteer_in_role_at_event_on_day
        ),
    )
