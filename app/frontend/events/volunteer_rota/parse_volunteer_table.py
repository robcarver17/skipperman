from app.backend.rota.sorting_and_filtering import (
    get_sorted_and_filtered_dict_of_volunteers_at_event,
)
from app.frontend.events.volunteer_rota.edit_volunteer_details_from_rota import \
    update_volunteer_availability_at_event_from_rota_with_form_contents
from app.frontend.events.volunteer_rota.button_values import \
    last_button_pressed_was_make_all_days_unavailable_for_volunteer, \
    last_button_pressed_was_make_unavailable_for_specific_day_button, remove_role_button_type, \
    remove_role_across_button_type, volunteer_from_remove_role_across_days_button

from app.frontend.forms.form_utils import get_dict_of_skills_from_form

from app.frontend.events.volunteer_rota.button_values import (
    from_location_button_to_volunteer,
    from_skills_button_to_volunteer,
    volunteer_and_day_from_make_available_button, volunteer_from_make_unavailable_across_days_button,
    volunteer_and_day_from_make_unavailable_on_specific_day_button,
    volunteer_and_day_from_remove_role_on_specific_day_button,
)

from app.data_access.init_directories import temp_file_name_in_download_directory

from app.backend.rota.changes import delete_role_at_event_for_volunteer_on_day
from app.backend.volunteers.volunteers_at_event import (
    make_volunteer_available_on_day,
    make_volunteer_unavailable_on_day,
    is_volunteer_currently_available_for_only_one_day, delete_volunteer_at_event,
)
from app.backend.rota.volunteer_matrix import get_volunteer_matrix
from app.frontend.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import (
    display_form_edit_cadet_connections_from_rota,
)
from app.frontend.events.volunteer_rota.edit_volunteer_skills_from_rota import (
    display_form_edit_individual_volunteer_skills_from_rota,
)
from app.frontend.events.volunteer_rota.elements_in_volunteer_rota_page import (
    SKILLS_FILTER,
    get_available_filter_name_for_day,
    from_filter_entry_to_option,
)
from app.frontend.events.volunteer_rota.rota_state import (
    save_skills_filter_to_state,
    save_availablity_filter_to_state,
    get_sorts_and_filters_from_state,
)
from app.frontend.events.volunteer_rota.parse_data_fields_in_rota import (
    update_details_from_form_for_volunteer_at_event,
)
from app.frontend.events.volunteer_rota.volunteer_table_buttons import *
from app.frontend.shared.buttons import volunteer_from_button_pressed, is_button_of_type
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.volunteer_state import update_state_with_volunteer_id, clear_volunteer_id_in_state, \
    is_volunteer_id_set_in_state, get_volunteer_from_state
from app.objects.abstract_objects.abstract_form import NewForm
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def save_all_information_in_rota_page(interface: abstractInterface):
    event = get_event_from_state(interface)
    sorts_and_filters = get_sorts_and_filters_from_state(interface)

    dict_of_volunteers_at_event_with_event_data = (
        get_sorted_and_filtered_dict_of_volunteers_at_event(
            object_store=interface.object_store,
            event=event,
            sorts_and_filters=sorts_and_filters,
        )
    )

    for (
        volunteer,
        volunteer_at_event_data,
    ) in dict_of_volunteers_at_event_with_event_data.items():
        update_details_from_form_for_volunteer_at_event(
            interface=interface,
            volunteer=volunteer,
            volunteer_at_event_data=volunteer_at_event_data,
        )


def action_if_volunteer_button_pressed(
    interface: abstractInterface, volunteer_button: str
):
    volunteer = volunteer_from_button_pressed(object_store=interface.object_store,
                                              value_of_button_pressed=volunteer_button)
    if is_volunteer_id_set_in_state(interface):
        action_if_volunteer_button_pressed_and_volunteer_in_state(interface=interface,
                                                                  volunteer=volunteer)
    else:
        action_if_volunteer_button_pressed_and_no_volunteer_set_in_state(interface=interface,
                                                                         volunteer=volunteer)


def action_if_volunteer_button_pressed_and_volunteer_in_state(
    interface: abstractInterface, volunteer: Volunteer
):
    volunteer_in_state = get_volunteer_from_state(interface)
    if volunteer_in_state == volunteer:
        event = get_event_from_state(interface)
        update_volunteer_availability_at_event_from_rota_with_form_contents(interface=interface, event=event, volunteer=volunteer_in_state)
        clear_volunteer_id_in_state(interface)
    else:
        ## select another one
        update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)

def action_if_volunteer_button_pressed_and_no_volunteer_set_in_state(
    interface: abstractInterface, volunteer: Volunteer
):
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)


def action_if_location_button_pressed(
    interface: abstractInterface, location_button: str
) -> NewForm:
    volunteer = from_location_button_to_volunteer(object_store=interface.object_store,
                                                  location_button_name=location_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)

    return interface.get_new_form_given_function(
        display_form_edit_cadet_connections_from_rota
    )


def action_if_volunteer_skills_button_pressed(
    interface: abstractInterface, volunteer_skills_button: str
) -> NewForm:
    volunteer = from_skills_button_to_volunteer(object_store=interface.object_store,
                                                   skills_button_name=volunteer_skills_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)

    return interface.get_new_form_given_function(
        display_form_edit_individual_volunteer_skills_from_rota
    )


def update_if_make_available_button_pressed(
    interface: abstractInterface, available_button: str
):
    volunteer, day = volunteer_and_day_from_make_available_button(object_store=interface.object_store, button=available_button)
    event = get_event_from_state(interface)
    make_volunteer_available_on_day(
        object_store=interface.object_store, event=event, volunteer=volunteer, day=day
    )


def update_if_make_unavailable_button_pressed(
    interface: abstractInterface, unavailable_button: str
):
    if last_button_pressed_was_make_all_days_unavailable_for_volunteer(unavailable_button):
        update_if_make_unavailable_across_days_button_pressed(interface=interface,unavailable_button=unavailable_button)
    elif last_button_pressed_was_make_unavailable_for_specific_day_button(unavailable_button):
        update_if_make_unavailable_on_specific_day_button_pressed(interface=interface, unavailable_button=unavailable_button)
    else:
        raise Exception("Unavailable button %s uknown!" % unavailable_button)

def update_if_make_unavailable_across_days_button_pressed(
        interface: abstractInterface, unavailable_button: str
):
    volunteer = volunteer_from_make_unavailable_across_days_button(object_store=interface.object_store, button=unavailable_button)
    event = get_event_from_state(interface)
    delete_volunteer_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )


def update_if_make_unavailable_on_specific_day_button_pressed(
        interface: abstractInterface, unavailable_button: str
):

    volunteer, day = volunteer_and_day_from_make_unavailable_on_specific_day_button(
        object_store=interface.object_store,
        button=unavailable_button
    )
    event = get_event_from_state(interface)

    make_volunteer_unavailable_on_day(
        object_store=interface.object_store, event=event, volunteer=volunteer, day=day
    )


def update_if_remove_role_button_pressed(
    interface: abstractInterface, remove_button: str
):
    if is_button_of_type(remove_button, remove_role_button_type):
        update_if_remove_role_button_pressed_on_specific_day(interface=interface,
                                                             remove_button=remove_button)

    elif is_button_of_type(remove_button, remove_role_across_button_type):
        update_if_remove_role_button_pressed_across_days(interface=interface,
                                                         remove_button=remove_button)
    else:
        raise Exception("Button %s not a remove button" % remove_button)


def update_if_remove_role_button_pressed_on_specific_day(
        interface: abstractInterface, remove_button: str
):

    volunteer, day =volunteer_and_day_from_remove_role_on_specific_day_button(object_store=interface.object_store,
                                                                              button=remove_button)
    event = get_event_from_state(interface)
    delete_role_at_event_for_volunteer_on_day(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        day=day,
        delete_power_boat=True,
    )


def update_if_remove_role_button_pressed_across_days(
        interface: abstractInterface, remove_button: str
):

    volunteer =volunteer_from_remove_role_across_days_button(object_store=interface.object_store,
                                                                              button=remove_button)
    event = get_event_from_state(interface)
    for day in event.days_in_event():
        delete_role_at_event_for_volunteer_on_day(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            day=day,
            delete_power_boat=True,
        )


def save_volunteer_matrix_and_return_filename(interface: abstractInterface) -> str:
    event = get_event_from_state(interface)
    sorts_and_filters = get_sorts_and_filters_from_state(interface)
    volunteer_matrix = get_volunteer_matrix(
        object_store=interface.object_store,
        event=event,
        sorts_and_filters=sorts_and_filters,
    )
    filename = temp_file_name_in_download_directory()
    volunteer_matrix.to_csv(filename)

    return filename


def update_filters(interface: abstractInterface):
    update_volunteer_skills_filter(interface)
    update_volunteer_availability_filter(interface)


def update_volunteer_skills_filter(interface: abstractInterface):
    dict_of_skills = get_dict_of_skills_from_form(
        interface=interface, field_name=SKILLS_FILTER
    )
    if dict_of_skills is MISSING_FROM_FORM:
        print("missing from form")
        return

    save_skills_filter_to_state(interface=interface, dict_of_skills=dict_of_skills)


def update_volunteer_availability_filter(interface: abstractInterface):
    event = get_event_from_state(interface)
    availabilty_filter_dict = dict(
        [
            (
                day.name,
                update_volunteer_availability_for_day(interface=interface, day=day),
            )
            for day in event.days_in_event()
        ]
    )

    save_availablity_filter_to_state(
        interface=interface, availability_filter_dict=availabilty_filter_dict
    )


def update_volunteer_availability_for_day(
    interface: abstractInterface, day: Day
) -> str:
    form_entry_name = get_available_filter_name_for_day(day)
    form_value = interface.value_from_form(form_entry_name)
    option_chosen = from_filter_entry_to_option(form_value)
    return option_chosen
