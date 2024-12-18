from app.backend.clothing.summarise_clothing import summarise_clothing
from app.frontend.events.clothing.downloads import (
    export_committee_clothing,
    export_clothing_colours,
    export_all_clothing,
)
from app.frontend.events.clothing.parse_clothing import (
    save_clothing_data,
    distribute_colour_groups,
    clear_all_colours,
)
from app.frontend.events.clothing.render_clothing import *
from app.objects.composed.clothing_at_event import all_sort_types

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import cancel_menu_button, save_menu_button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_clothing_requirements(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    title = Heading(
        "Clothing requirements for event %s" % str(event), centred=True, size=4
    )

    button_bar = get_button_bar_for_clothing(interface=interface)
    clothing_table = get_clothing_table(interface=interface, event=event)
    summary = summarise_clothing(object_store=interface.object_store, event=event)
    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                summary,
                _______________,
                sort_buttons_for_clothing,
                clothing_table,
                _______________,
            ]
        )
    )


def post_form_view_for_clothing_requirements(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    ### save
    if save_menu_button.pressed(last_button_pressed):
        save_clothing_data(interface)
        interface.flush_cache_to_store()

    elif distribute_action_button.pressed(last_button_pressed):
        distribute_colour_groups(interface)
        interface.flush_cache_to_store()

    elif clear_all_colours_button.pressed(last_button_pressed):
        clear_all_colours(interface)
        interface.flush_cache_to_store()


    elif last_button_pressed in all_sort_types:
        sort_order = interface.last_button_pressed()
        save_sort_order(interface=interface, sort_order=sort_order)

    elif filter_all_button.pressed(last_button_pressed):
        set_to_showing_all(interface)

    elif filter_committee_button.pressed(last_button_pressed):
        set_to_showing_only_committee(interface)


    elif export_committee_button.pressed(last_button_pressed):
        return export_committee_clothing(interface)
    elif export_all_clothing_button.pressed(last_button_pressed):
        return export_all_clothing(interface)
    elif export_colours_button.pressed(last_button_pressed):
        return export_clothing_colours(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


    return display_form_view_for_clothing_requirements(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_clothing_requirements
    )
