from typing import Union

from app.backend.volunteers.volunteer_rota_summary import get_summary_list_of_roles_and_groups_for_events
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import *
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
    #### FIXME STAB THROUGH CHANGED CADETS FIRSTS
    sort_by_volunteer_name, sort_by_day = get_sorts_from_state(interface)
    event =get_event_from_state(interface)
    title = "Volunteer rota for event %s" % str(event)

    summary_of_filled_roles =  get_summary_list_of_roles_and_groups_for_events(event)
    volunteer_table_with_day_reordering = get_volunteer_table(event=event,
                                                              sort_by_day=sort_by_day,
                                                              sort_by_volunteer_name=sort_by_volunteer_name)

    footer_buttons = get_footer_buttons_for_rota()

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
                volunteer_name_sort_buttons,
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

save_button = Button(SAVE_CHANGES, big=True)


instructions = ListOfLines(["SAVE CHANGES BEFORE SORTING OR COPYING! Click on any day to sort by group and role, or sort volunteers by name",
                            "Click on volunteer names to edit food requirements and days attending, or remove from event. Click on location to see and edit connected cadets. Click on skills to edit volunteer skills.",
                            "Click on 'unavailable' days to make a volunteer available. Select role = unavailable to make a volunteer unavailable",
                            "Save after selecting role to see group allocations where relevant.",
                            "You can copy roles/groups to other days to avoid tiresome re-entry (clicking copy will save that volunteer/day first, but make sure you save other changes first before copying)"])

volunteer_name_sort_buttons = Line([Button(sort_by) for sort_by in all_volunteer_name_sort_types])

def get_footer_buttons_for_rota():
    return Line([
        Button(ADD_NEW_VOLUNTEER_BUTTON_LABEL),
        Button(BACK_BUTTON_LABEL)
    ])

def post_form_view_for_volunteer_rota(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()


    if last_button_pressed==BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(display_form_view_for_volunteer_rota)


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
        return interface.get_new_display_form_given_function(display_form_add_new_volunteer_to_rota_at_event)

    elif last_button_pressed in get_list_of_volunteer_name_buttons(interface):
        return action_if_volunteer_button_pressed(interface=interface,
                                                  volunteer_button=last_button_pressed)

    elif last_button_pressed in get_all_location_buttons(interface):
        return action_if_location_button_pressed(interface=interface, location_button=last_button_pressed)

    elif last_button_pressed in get_all_skill_buttons(interface):
        return action_if_volunteer_skills_button_pressed(interface=interface, volunteer_skills_button=last_button_pressed)

    ## Updates to form, display form again
    elif last_button_pressed in get_all_unavailable_buttons(interface):
        update_if_make_available_button_pressed(unavailable_button=last_button_pressed, interface=interface)
        return display_form_view_for_volunteer_rota(interface=interface)

    elif last_button_pressed in get_all_copy_buttons(interface):
        update_if_copy_button_pressed(interface=interface, copy_button=last_button_pressed)
        return display_form_view_for_volunteer_rota(interface=interface)

    elif last_button_pressed==SAVE_CHANGES:
        update_if_save_button_pressed_in_rota_page(interface)
        return display_form_view_for_volunteer_rota(interface=interface)

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)





