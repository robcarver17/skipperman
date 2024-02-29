from typing import Union, List

from app.backend.volunteers.patrol_boats import volunteer_is_on_same_boat_for_all_days
from app.backend.volunteers.volunteer_rota import is_possible_to_copy_roles_for_non_grouped_roles_only
from app.data_access.configuration.fixed import COPY_SYMBOL1, BOAT_SHORTHAND, BOAT_AND_ROLE_SHORTHAND, ROLE_SHORTHAND
from app.logic.events.patrol_boats.patrol_boat_buttons import generic_button_name_for_volunteer_in_boat_at_event_on_day, \
    get_list_of_generic_buttons_for_each_volunteer_day_combo
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event

COPY_BOAT_BUTTON_LABEL = Line([COPY_SYMBOL1, BOAT_SHORTHAND])
COPY_BOTH_BUTTON_LABEL = Line([COPY_SYMBOL1, BOAT_AND_ROLE_SHORTHAND])
COPY_ROLE_BUTTON_LABEL = Line([COPY_SYMBOL1, ROLE_SHORTHAND])


def get_copy_buttons_for_boat_allocation(day: Day,
                                         event: Event,
                                         volunteer_id: str)-> list:
    copy_boat_button = get_copy_button_for_boat_copy_in_boat_rota(volunteer_id=volunteer_id, event=event, day=day)
    copy_both_button = get_copy_button_for_role_and_boat_in_rota(volunteer_id=volunteer_id, event=event, day=day)
    copy_role_button = get_copy_button_for_role_in_boat_rota(volunteer_id=volunteer_id, event=event, day=day)

    return [copy_boat_button, copy_role_button, copy_both_button]


def get_copy_button_for_boat_copy_in_boat_rota(day: Day,
                                               event: Event,
                                               volunteer_id: str) -> Union[Button,str]:

    copy_button_name = copy_button_name_for_boat_copy_in_boat_at_event_on_day(day=day,
                                                                              volunteer_id=volunteer_id,
                                                                              )

    if is_possible_to_copy_boat_allocation(event=event, volunteer_id=volunteer_id):
        return Button(
            label=COPY_BOAT_BUTTON_LABEL,
            value=copy_button_name
        )
    else:
        return ""


def get_copy_button_for_role_in_boat_rota(day: Day,
                                                event: Event,
                                                volunteer_id: str) -> Union[Button,str]:

    copy_button_name = copy_button_name_for_volunteer_role_in_boat_at_event_on_day(day=day,
                                                                         volunteer_id=volunteer_id,
                                                                         )

    if is_possible_to_copy_roles_for_non_grouped_roles_only(event=event, volunteer_id=volunteer_id):

        return Button(
            label=COPY_ROLE_BUTTON_LABEL,
            value=copy_button_name
        )
    else:
        return ""


def get_copy_button_for_role_and_boat_in_rota( day: Day,
                                                event: Event,
                                                volunteer_id: str) -> Union[Button,str]:

    copy_button_name = copy_button_name_for_both_volunteer_role_and_boat_at_event_on_day(day=day,
                                                                                         volunteer_id=volunteer_id,
                                                                                         )

    if is_possible_to_copy_boat_and_role_allocation(event=event, volunteer_id=volunteer_id):
        return Button(
            label=COPY_BOTH_BUTTON_LABEL,
            value=copy_button_name
        )
    else:
        return ""


def is_possible_to_copy_boat_allocation(event: Event,
                                                volunteer_id: str):
    copy_button_required = not volunteer_is_on_same_boat_for_all_days(
        volunteer_id=volunteer_id, event=event)

    return copy_button_required


def is_possible_to_copy_boat_and_role_allocation(event: Event,
                                                volunteer_id: str):
    boat_possible = is_possible_to_copy_boat_allocation(event=event, volunteer_id=volunteer_id)
    role_possible = is_possible_to_copy_roles_for_non_grouped_roles_only(event=event, volunteer_id=volunteer_id)

    return boat_possible and role_possible


COPY_BOAT = "copyBoatButton"
COPY_ROLE = "copyRoleButton"
COPY_BOTH = "copyBothButton"


def copy_button_name_for_boat_copy_in_boat_at_event_on_day(day: Day,
                                                           volunteer_id: str)-> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(button_type=COPY_BOAT, day=day,
                                                                     volunteer_id=volunteer_id)


def copy_button_name_for_volunteer_role_in_boat_at_event_on_day(day: Day,
                                                volunteer_id: str) -> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(button_type=COPY_ROLE, day=day,
                                                                     volunteer_id=volunteer_id)


def copy_button_name_for_both_volunteer_role_and_boat_at_event_on_day(day: Day,
                                                                      volunteer_id: str)-> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(button_type=COPY_BOTH, day=day,
                                                                     volunteer_id=volunteer_id)


def get_list_of_all_types_of_copy_buttons(event: Event)-> List[str]:
    return get_list_of_all_copy_boat_buttons_for_boat_allocation(event)+\
            get_list_of_all_copy_role_buttons_for_boat_allocation(event)+\
            get_list_of_all_copy_both_buttons_for_boat_allocation(event)


def get_list_of_all_copy_boat_buttons_for_boat_allocation(event:Event)-> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        event=event,
        button_name_function=copy_button_name_for_boat_copy_in_boat_at_event_on_day
    )


def get_list_of_all_copy_role_buttons_for_boat_allocation(event:Event)-> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        event=event,
        button_name_function=copy_button_name_for_volunteer_role_in_boat_at_event_on_day
    )


def get_list_of_all_copy_both_buttons_for_boat_allocation(event:Event)-> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        event=event,
        button_name_function=copy_button_name_for_both_volunteer_role_and_boat_at_event_on_day
    )
