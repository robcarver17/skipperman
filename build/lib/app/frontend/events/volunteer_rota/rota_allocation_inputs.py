from typing import Union, List

from app.objects.groups import Group

from app.backend.rota.volunteer_table import get_dict_of_roles_for_dropdown, get_dict_of_groups_for_dropdown
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup
from app.objects.volunteers import Volunteer

from app.objects.roles_and_teams import RolesWithSkillIds

from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer

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


def get_allocation_inputs_for_volunteer(
    interface: abstractInterface,
    volunteer_data_at_event: AllEventDataForVolunteer,
    ready_to_swap: bool = False,
) -> List[ListOfLines]:
    day_inputs = [
        get_allocation_inputs_for_day_and_volunteer(
            ready_to_swap=ready_to_swap,
            interface=interface,
            volunteer_data_at_event=volunteer_data_at_event,
            day=day,
        )
        for day in volunteer_data_at_event.event.weekdays_in_event()
    ]

    return day_inputs


def get_allocation_inputs_for_day_and_volunteer(
    interface: abstractInterface,
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:
    volunteer_available_on_day = volunteer_data_at_event.registration_data.availablity.available_on_day(day)
    if volunteer_available_on_day:
        return get_allocation_inputs_for_day_and_volunteer_when_available(
            interface=interface,
            volunteer_data_at_event=volunteer_data_at_event,
            ready_to_swap=ready_to_swap,
            day=day,
        )
    else:
        return get_allocation_inputs_for_day_and_volunteer_when_unavailable(
            day=day, volunteer_data_at_event=volunteer_data_at_event, ready_to_swap=ready_to_swap
        )



def get_allocation_inputs_for_day_and_volunteer_when_unavailable(
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:
    if ready_to_swap:
        return ListOfLines(["Unavailable"])
    else:
        make_available_button = Button(
            "Make available",
            value=make_available_button_value_for_volunteer_on_day(
                volunteer_id=volunteer_data_at_event.volunteer.id, day=day
            ),
        )
        return ListOfLines([make_available_button])

def get_allocation_inputs_for_day_and_volunteer_when_available(
    interface: abstractInterface,
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
    ready_to_swap: bool,
) -> ListOfLines:

    role_and_group = volunteer_data_at_event.roles_and_groups.role_and_group_on_day(day)

    group_and_role_inputs = get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(
        volunteer=volunteer_data_at_event.volunteer,
        interface=interface,
        role_and_group=role_and_group,
        day=day,
        ready_to_swap=ready_to_swap,
    )
    buttons = get_allocation_inputs_buttons_in_role_when_available(
        interface=interface,
        ready_to_swap=ready_to_swap,
        volunteer_data_at_event=volunteer_data_at_event,
        day=day
    )
    return ListOfLines([group_and_role_inputs, buttons]).add_Lines()


def get_role_and_group_allocation_inputs_for_day_and_volunteer_in_role_when_available(
    interface: abstractInterface,
        volunteer: Volunteer,
        role_and_group: RoleAndGroup,
        day: Day,
        ready_to_swap: bool,
) -> list:
    role = role_and_group.role
    group = role_and_group.group

    role_input = get_allocation_input_for_role(
        interface=interface,
        role=role,
        ready_to_swap=ready_to_swap,
        day=day,
        volunteer=volunteer
    )

    role_already_set = not role.is_no_role_set()
    group_required_given_role = role.associate_sailing_group

    all_elements = [role_input]  ## always have this

    if role_already_set and group_required_given_role:
        group_input = get_allocation_input_for_group(
            interface=interface,
            volunteer=volunteer,
            day=day,
            group=group,
            ready_to_swap=ready_to_swap,
        )
        all_elements.append(group_input)

    return all_elements




def get_allocation_input_for_role(
    interface: abstractInterface,
    volunteer: Volunteer,
    role: Union[RolesWithSkillIds, RoleWithSkills],
    day: Day,
    ready_to_swap: bool,
) -> Union[dropDownInput, str]:
    dict_of_roles_for_dropdown = get_dict_of_roles_for_dropdown(interface.object_store)

    if ready_to_swap:
        return role.name
    return dropDownInput(
        input_label="",
        input_name=input_name_for_role_and_volunteer(day=day, volunteer=volunteer),
        dict_of_options=dict_of_roles_for_dropdown,
        default_label=role.name,
    )


def input_name_for_role_and_volunteer(
    day: Day,
        volunteer: Volunteer,

) -> str:
    return "ROLE_%s_%s" % (
        volunteer.id,
        day.name,
    )


def get_allocation_input_for_group(
        interface: abstractInterface,
    group: Group,
        volunteer: Volunteer,
        day: Day,
    ready_to_swap: bool,
) -> Union[dropDownInput, str]:
    if ready_to_swap:
        return " (%s)" % group.name

    dict_of_groups_for_dropdown = get_dict_of_groups_for_dropdown(interface.object_store)
    return dropDownInput(
        input_label="",
        input_name=input_name_for_group_and_volunteer(
            volunteer=volunteer, day=day
        ),
        dict_of_options=dict_of_groups_for_dropdown,
        default_label=group.name,
    )


def input_name_for_group_and_volunteer(
        volunteer: Volunteer,
        day: Day,
) -> str:
    return "GROUP_%s_%s" % (
        volunteer.id,
        day.name,
    )
