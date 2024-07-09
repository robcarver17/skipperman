from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form

from app.logic.events.volunteer_rota.swapping import update_if_swap_button_pressed
from app.logic.events.volunteer_rota.add_volunteer_to_rota import (
    display_form_add_new_volunteer_to_rota_at_event,
)

from app.logic.events.volunteer_rota.parse_volunteer_table import *
from app.logic.events.volunteer_rota.rota_state import (
    save_sorts_to_state,
    get_sorts_and_filters_from_state,
    clear_all_filters,
)
from app.logic.events.volunteer_rota.volunteer_table_buttons import (
    from_day_button_value_to_day,
)
from app.logic.events.volunteer_rota.volunteer_targets import (
    get_volunteer_targets_table_and_save_button,
)
from app.logic.events.volunteer_rota.warnings import warn_on_all_volunteers
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state
from app.logic.volunteers.ENTRY_view_volunteers import (
    all_sort_types as all_volunteer_name_sort_types,
)
from app.logic.events.volunteer_rota.render_volunteer_table import get_volunteer_table
from app.logic.events.volunteer_rota.elements_in_volunteer_rota_page import (
    get_filters_and_buttons,
    APPLY_FILTER_BUTTON_LABEL,
    get_header_buttons_for_rota,
    get_summary_table,
    instructions,
    ADD_NEW_VOLUNTEER_BUTTON_LABEL,
    SORT_BY_CADET_LOCATION,
    CLEAR_FILTERS_BUTTON_LABEL,
    get_summary_group_table,
    download_matrix_button,
)
from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_volunteer_rota(interface: abstractInterface) -> Form:
    sorts_and_filters = get_sorts_and_filters_from_state(interface)
    print(sorts_and_filters)
    event = get_event_from_state(interface)
    title = Heading("Volunteer rota for event %s" % str(event), centred=True, size=4)
    summary_of_filled_roles = get_summary_table(interface=interface, event=event)
    summary_group_table = get_summary_group_table(interface=interface, event=event)
    targets = get_volunteer_targets_table_and_save_button(
        interface=interface, event=event
    )
    warnings = warn_on_all_volunteers(interface)
    volunteer_table = get_volunteer_table(
        event=event, interface=interface, sorts_and_filters=sorts_and_filters
    )

    header_buttons = get_header_buttons_for_rota(interface)
    material_around_table = get_filters_and_buttons(interface=interface, event=event)
    form = Form(
        ListOfLines(
            [
                header_buttons,
                title,
                _______________,
                _______________,
                summary_of_filled_roles,
                _______________,
                summary_group_table,
                _______________,
                targets,
                _______________,
                warnings,
                _______________,
                instructions,
                _______________,
                material_around_table.before_table,
                _______________,
                volunteer_table,
                _______________,
                material_around_table.after_table,
            ]
        )
    )
    return form


def post_form_view_for_volunteer_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == cancel_menu_button.name:
        return previous_form(interface)

    ## Always do this unless we pressed back
    save_all_information_and_filter_state_in_rota_page(interface)

    ### BUTTONS: HAS TO BE ONE BIG IF
    ## This may reverse what we did before with filter updates, that's fine
    if last_button_pressed == CLEAR_FILTERS_BUTTON_LABEL:
        clear_all_filters(interface)

    ## File
    elif download_matrix_button.pressed(last_button_pressed):
        filename = save_volunteer_matrix_and_return_filename(interface)
        return File(filename)

    ## Actions which result in new forms
    elif last_button_pressed == ADD_NEW_VOLUNTEER_BUTTON_LABEL:
        return add_new_volunteer_form(interface)
    elif last_button_pressed in get_list_of_volunteer_name_buttons(interface):
        return action_if_volunteer_button_pressed(
            interface=interface, volunteer_button=last_button_pressed
        )

    elif last_button_pressed in get_all_location_buttons(interface):
        return action_if_location_button_pressed(
            interface=interface, location_button=last_button_pressed
        )

    elif last_button_pressed in get_all_skill_buttons(interface):
        return action_if_volunteer_skills_button_pressed(
            interface=interface, volunteer_skills_button=last_button_pressed
        )

    ## SORTS
    elif last_button_pressed in all_volunteer_name_sort_types:
        save_sorts_to_state(
            interface=interface, sort_by_volunteer_name=last_button_pressed
        )
    elif last_button_pressed in get_all_day_sort_buttons(interface):
        sort_by_day = from_day_button_value_to_day(last_button_pressed)
        save_sorts_to_state(interface=interface, sort_by_day=sort_by_day)
    elif last_button_pressed == SORT_BY_CADET_LOCATION:
        save_sorts_to_state(interface=interface, sort_by_location=True)

    ## Updates to form, display form again
    elif last_button_pressed in get_all_make_available_buttons(interface):
        update_if_make_available_button_pressed(
            available_button=last_button_pressed, interface=interface
        )

    elif last_button_pressed in get_all_make_unavailable_buttons(interface):
        update_if_make_unavailable_button_pressed(
            interface=interface, unavailable_button=last_button_pressed
        )

    elif last_button_pressed in get_all_remove_role_buttons(interface):
        update_if_remove_role_button_pressed(
            interface=interface, remove_button=last_button_pressed
        )

    elif last_button_pressed in get_all_copy_buttons(interface):
        update_if_copy_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

    elif last_button_pressed in get_all_swap_buttons(interface):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )

    elif last_button_pressed in [save_menu_button.name, APPLY_FILTER_BUTTON_LABEL]:
        ## already saved
        pass
    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_view_for_volunteer_rota(interface=interface)


def add_new_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_add_new_volunteer_to_rota_at_event
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_volunteer_rota
    )
