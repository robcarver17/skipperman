from typing import Union

from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.volunteer_rota_summary import get_summary_list_of_roles_and_groups_for_events
from app.data_access.configuration.fixed import *
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import *
from app.logic.events.volunteer_rota.swapping import update_if_swap_button_pressed
from app.logic.events.volunteer_rota.add_volunteer_to_rota import display_form_add_new_volunteer_to_rota_at_event

from app.logic.events.volunteer_rota.parse_volunteer_table import *
from app.logic.events.volunteer_rota.rota_state import save_sorts_to_state, get_sorts_from_state
from app.logic.events.volunteer_rota.volunteer_table_buttons import from_day_button_value_to_day
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state
from app.logic.volunteers.ENTRY_view_volunteers import all_sort_types as all_volunteer_name_sort_types
from app.logic.events.volunteer_rota.render_volunteer_table import get_volunteer_table

ADD_NEW_VOLUNTEER_BUTTON_LABEL = "Add new volunteer to rota"

def display_form_view_for_volunteer_rota(interface: abstractInterface) -> Form:
    sort_by_volunteer_name, sort_by_day = get_sorts_from_state(interface)
    event =get_event_from_state(interface)
    title = "Volunteer rota for event %s" % str(event)

    summary_of_filled_roles =  get_summary_list_of_roles_and_groups_for_events(event)
    volunteer_table_with_day_reordering = get_volunteer_table(event=event,
                                                              interface=interface,
                                                              sort_by_day=sort_by_day,
                                                              sort_by_volunteer_name=sort_by_volunteer_name)

    save_button = get_saved_button(interface)
    by_name_sort_buttons = get_volunteer_name_sort_buttons(interface)
    footer_buttons = get_footer_buttons_for_rota(interface)

    return Form(
        ListOfLines(
            [
                title,
                _______________,
                _______________,
                summary_of_filled_roles,
                _______________,
                instructions,
                _______________,
                by_name_sort_buttons,
                footer_buttons,
                _______________,
                save_button,
                volunteer_table_with_day_reordering,
                save_button,
                _______________,
                footer_buttons
            ]
        )
    )

def get_saved_button(interface: abstractInterface):
    if is_ready_to_swap(interface):
        return ""
    return Button(SAVE_CHANGES, big=True)


def get_volunteer_name_sort_buttons(interface: abstractInterface):
    if is_ready_to_swap(interface):
        return ""
    return Line([Button(sort_by) for sort_by in all_volunteer_name_sort_types])


instructions = ListOfLines(["Always click SAVE after making any non button change",
                            Line(["Key for buttons - Copy: ",
                                        COPY_SYMBOL1, COPY_SYMBOL2,
                                        " , Swap: ", SWAP_SHORTHAND1, SWAP_SHORTHAND2, ", ",
                                        'Raincheck: make unavailable: ', NOT_AVAILABLE_SHORTHAND ,
                                        'Available, but role undefined', AVAILABLE_SHORTHAND]),

                            "Click on any day to sort by group and role, or sort volunteers by name",
                            "Click on volunteer names to edit food requirements and days attending, or remove from event. Click on location to see and edit connected cadets. Click on skills to edit volunteer skills.",
                            "Click on 'unavailable' days to make a volunteer available. Select role = unavailable to make a volunteer unavailable",
                            "Save after selecting role to see group allocations where relevant.",
                            "You can copy roles/groups to other days to avoid tiresome re-entry"])


def get_footer_buttons_for_rota(interface: abstractInterface):
    if is_ready_to_swap(interface):
        return ""
    return Line([
        Button(ADD_NEW_VOLUNTEER_BUTTON_LABEL),
        Button(BACK_BUTTON_LABEL)
    ])

def post_form_view_for_volunteer_rota(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()


    if last_button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)

    ## sort options
    elif last_button_pressed in all_volunteer_name_sort_types:
        save_sorts_to_state(interface=interface, sort_by_volunteer_name=last_button_pressed)
        return display_form_view_for_volunteer_rota(interface=interface)

    elif last_button_pressed in get_all_day_sort_buttons(interface):
        sort_by_day = from_day_button_value_to_day(last_button_pressed)
        save_sorts_to_state(interface=interface, sort_by_day=sort_by_day)
        return display_form_view_for_volunteer_rota(interface)

    ## Actions which result in new forms
    elif last_button_pressed==ADD_NEW_VOLUNTEER_BUTTON_LABEL:
        return add_new_volunteer_form(interface)

    elif last_button_pressed in get_list_of_volunteer_name_buttons(interface):
        return action_if_volunteer_button_pressed(interface=interface,
                                                  volunteer_button=last_button_pressed)

    elif last_button_pressed in get_all_location_buttons(interface):
        return action_if_location_button_pressed(interface=interface, location_button=last_button_pressed)

    elif last_button_pressed in get_all_skill_buttons(interface):
        return action_if_volunteer_skills_button_pressed(interface=interface, volunteer_skills_button=last_button_pressed)

    ## Updates to form, display form again
    if last_button_pressed in get_all_make_available_buttons(interface):
        update_if_make_available_button_pressed(available_button=last_button_pressed, interface=interface)

    elif last_button_pressed in get_all_copy_buttons(interface):
        update_if_copy_button_pressed(interface=interface, copy_button=last_button_pressed)

    elif last_button_pressed in get_all_swap_buttons(interface):
        update_if_swap_button_pressed(interface=interface, swap_button = last_button_pressed)

    elif last_button_pressed in get_all_make_unavailable_buttons(interface):
        update_if_make_unavailable_button_pressed(interface=interface, unavailable_button=last_button_pressed)

    elif last_button_pressed in get_all_remove_role_buttons(interface):
        update_if_remove_role_button_pressed(interface=interface, remove_button=last_button_pressed)

    elif last_button_pressed==SAVE_CHANGES:
        update_if_save_button_pressed_in_rota_page(interface)
    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_view_for_volunteer_rota(interface=interface)




def add_new_volunteer_form(interface :abstractInterface):
    return interface.get_new_form_given_function(display_form_add_new_volunteer_to_rota_at_event)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_view_for_volunteer_rota)


