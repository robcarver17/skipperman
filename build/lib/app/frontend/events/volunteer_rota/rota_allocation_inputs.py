from typing import Union, List

from app.objects.events import Event

from app.OLD_backend.rota.volunteer_rota import (
    get_volunteers_in_role_at_event_with_active_allocations,
    dict_of_roles_for_dropdown,
    dict_of_groups_for_dropdown,
)
from app.frontend.events.volunteer_rota.volunteer_table_buttons import (
    get_allocation_inputs_buttons_in_role_when_available,
)
from app.frontend.events.volunteer_rota.button_values import (
    make_available_button_value_for_volunteer_on_day,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.day_selectors import Day
from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent
from app.objects.volunteer_roles_and_groups_with_id import VolunteerWithIdInRoleAtEvent


def get_allocation_inputs_for_volunteer(
    interface: abstractInterface,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    ready_to_swap: bool = False,
) -> List[ListOfLines]:
    day_inputs = [
        get_allocation_inputs_for_day_and_volunteer(
            ready_to_swap=ready_to_swap,
            interface=interface,
            volunteer_at_event=volunteer_at_event,
            day=day,
        )
        for day in volunteer_at_event.event.weekdays_in_event()
    ]

    return day_inputs


def get_allocation_inputs_for_day_and_volunteer(
    interface: abstractInterface,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:
    volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(day)
    if volunteer_available_on_day:
        return get_allocation_inputs_for_day_and_volunteer_when_available(
            interface=interface,
            volunteer_at_event=volunteer_at_event,
            ready_to_swap=ready_to_swap,
            day=day,
        )
    else:
        return get_allocation_inputs_for_day_and_volunteer_when_unavailable(
            day=day, volunteer_at_event=volunteer_at_event, ready_to_swap=ready_to_swap
        )


def get_allocation_inputs_for_day_and_volunteer_when_available(
    interface: abstractInterface,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:
    cache = interface.cache

    volunteers_in_roles_at_event = cache.get_from_cache(
        get_volunteers_in_role_at_event_with_active_allocations,
        event=volunteer_at_event.event,
    )

    volunteer_in_role_at_event_on_day = (
        volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_at_event.volunteer_id, day=day
        )
    )

    return get_allocation_inputs_for_day_and_volunteer_in_role_when_available(
        interface=interface,
        event=volunteer_at_event.event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap,
    )


def get_allocation_inputs_for_day_and_volunteer_when_unavailable(
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:
    if ready_to_swap:
        return ListOfLines(["Unavailable"])
    else:
        make_available_button = Button(
            "Make available",
            value=make_available_button_value_for_volunteer_on_day(
                volunteer_id=volunteer_at_event.volunteer_id, day=day
            ),
        )
        return ListOfLines([make_available_button])


def get_allocation_inputs_for_day_and_volunteer_in_role_when_available(
    interface: abstractInterface,
    event: Event,
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    ready_to_swap: bool,
) -> ListOfLines:
    group_and_role_inputs = get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap,
    )
    buttons = get_allocation_inputs_buttons_in_role_when_available(
        interface=interface,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap,
        event=event,
    )
    return ListOfLines([group_and_role_inputs, buttons]).add_Lines()


def get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    ready_to_swap: bool,
) -> list:
    role_input = get_allocation_input_for_role(
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        ready_to_swap=ready_to_swap,
    )

    role_already_set = not volunteer_in_role_at_event_on_day.no_role_set
    group_required_given_role = volunteer_in_role_at_event_on_day.requires_group

    all_elements = [role_input]  ## always have this

    if role_already_set and group_required_given_role:
        group_input = get_allocation_input_for_group(
            volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
            ready_to_swap=ready_to_swap,
        )
        all_elements.append(group_input)

    return all_elements


def get_allocation_input_for_role(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    ready_to_swap: bool,
) -> Union[dropDownInput, str]:
    if ready_to_swap:
        return volunteer_in_role_at_event_on_day.role
    return dropDownInput(
        input_label="",
        input_name=input_name_for_role_and_volunteer(volunteer_in_role_at_event_on_day),
        dict_of_options=dict_of_roles_for_dropdown,
        default_label=volunteer_in_role_at_event_on_day.role,
    )


def input_name_for_role_and_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> str:
    return "ROLE_%s_%s" % (
        volunteer_in_role_at_event_on_day.volunteer_id,
        volunteer_in_role_at_event_on_day.day.name,
    )


def get_allocation_input_for_group(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
    ready_to_swap: bool,
) -> dropDownInput:
    if ready_to_swap:
        return " (%s)" % volunteer_in_role_at_event_on_day.group.name

    return dropDownInput(
        input_label="",
        input_name=input_name_for_group_and_volunteer(
            volunteer_in_role_at_event_on_day
        ),
        dict_of_options=dict_of_groups_for_dropdown,
        default_label=volunteer_in_role_at_event_on_day.group.name,
    )


def input_name_for_group_and_volunteer(
    volunteer_in_role_at_event_on_day: VolunteerWithIdInRoleAtEvent,
) -> str:
    return "GROUP_%s_%s" % (
        volunteer_in_role_at_event_on_day.volunteer_id,
        volunteer_in_role_at_event_on_day.day.name,
    )
