from app.backend.clothing.summarise_clothing import summarise_clothing
from app.frontend.events.clothing.automatically_get_clothing_data_from_cadets import (
    update_cadet_clothing_at_event,
)
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
from app.frontend.events.clothing.render_clothing import (
    get_button_bar_for_clothing,
    get_clothing_table,
    GET_CLOTHING_FOR_CADETS,
    sort_buttons_for_clothing,
    save_sort_order,
    FILTER_COMMITTEE_BUTTON_LABEL,
    FILTER_ALL_BUTTON_LABEL,
    DISTRIBUTE_ACTION_BUTTON_LABEL,
    set_to_showing_all,
    set_to_showing_only_committee,
    CLEAR_ALL_COLOURS,
    EXPORT_COLOURS,
    EXPORT_ALL,
    EXPORT_COMMITTEE,
)
from app.objects.composed.clothing_at_event import all_sort_types

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    SAVE_BUTTON_LABEL,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_clothing_requirements(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    title = Heading(
        "Clothing requirements for event %s" % str(event), centred=True, size=4
    )

    button_bar = get_button_bar_for_clothing(interface=interface, event=event)
    clothing_table = get_clothing_table(interface=interface, event=event)
    summary = summarise_clothing(interface=interface, event=event)
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

    if last_button_pressed == CANCEL_BUTTON_LABEL:
        return previous_form(interface)

    ### save
    save_clothing_data(interface)

    if last_button_pressed == SAVE_BUTTON_LABEL:
        pass

    elif last_button_pressed in all_sort_types:
        sort_order = interface.last_button_pressed()
        save_sort_order(interface=interface, sort_order=sort_order)

    elif last_button_pressed == FILTER_ALL_BUTTON_LABEL:
        set_to_showing_all(interface)

    elif last_button_pressed == GET_CLOTHING_FOR_CADETS:
        update_cadet_clothing_at_event(interface)

    elif last_button_pressed == DISTRIBUTE_ACTION_BUTTON_LABEL:
        distribute_colour_groups(interface)

    elif last_button_pressed == CLEAR_ALL_COLOURS:
        clear_all_colours(interface)

    elif last_button_pressed == FILTER_COMMITTEE_BUTTON_LABEL:
        set_to_showing_only_committee(interface)

    elif last_button_pressed == EXPORT_COMMITTEE:
        return export_committee_clothing(interface)
    elif last_button_pressed == EXPORT_ALL:
        return export_all_clothing(interface)
    elif last_button_pressed == EXPORT_COLOURS:
        return export_clothing_colours(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_view_for_clothing_requirements(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_clothing_requirements
    )
