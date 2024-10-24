from app.OLD_backend.volunteers.volunteers import get_volunteer_from_id

from app.frontend.forms.form_utils import get_dict_of_skills_from_form
from app.frontend.forms import is_ready_to_swap
from app.frontend.events.volunteer_rota.button_values import from_known_button_to_volunteer_id_and_day, \
    from_location_button_to_volunteer_id, from_skills_button_to_volunteer_id, \
    get_dict_of_volunteer_name_buttons_and_volunteer_ids
from app.frontend.events.volunteer_rota.volunteer_targets import save_volunteer_targets

from app.data_access.file_access import temp_file_name


from app.OLD_backend.volunteers.volunteer_allocation import (
    make_volunteer_unavailable_on_day,
    make_volunteer_available_on_day,
)
from app.OLD_backend.rota.volunteer_rota import (
    delete_role_at_event_for_volunteer_on_day,
    load_list_of_volunteers_at_event,
)
from app.OLD_backend.rota.volunteer_matrix import get_volunteer_matrix
from app.frontend.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import (
    display_form_edit_cadet_connections_from_rota,
)
from app.frontend.events.volunteer_rota.edit_volunteer_details_from_rota import (
    display_form_confirm_volunteer_details_from_rota,
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
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_rota.parse_data_fields_in_rota import (
    update_details_from_form_for_volunteer_at_event,
)
from app.frontend.events.volunteer_rota.volunteer_table_buttons import *
from app.frontend.shared.volunteer_state import update_state_with_volunteer_id
from app.objects.abstract_objects.abstract_form import NewForm




def save_all_information_and_filter_state_in_rota_page(interface: abstractInterface):
    ready_to_swap = is_ready_to_swap(interface)
    if ready_to_swap:
        return

    save_all_information_in_rota_page(interface)
    save_volunteer_targets(interface)
    update_filters(interface)



def save_all_information_in_rota_page(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = interface.cache.get_from_cache(load_list_of_volunteers_at_event,
        event=event)

    for volunteer_at_event in list_of_volunteers_at_event:
        try:
            update_details_from_form_for_volunteer_at_event(
                interface=interface,
                volunteer_at_event=volunteer_at_event,
            )
        except Exception as e:
            ## perfectly fine if
            print(
                "Can't volunteer %s: error code %s probably because was filtered out"
                % (str(volunteer_at_event), str(e))
            )



def action_if_volunteer_button_pressed(
    interface: abstractInterface, volunteer_button: str
) -> NewForm:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict = get_dict_of_volunteer_name_buttons_and_volunteer_ids(
        interface=interface, event=event
    )

    volunteer_id = volunteer_name_buttons_dict[volunteer_button]
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(
        display_form_confirm_volunteer_details_from_rota
    )


def action_if_location_button_pressed(
    interface: abstractInterface, location_button: str
) -> NewForm:
    volunteer_id = from_location_button_to_volunteer_id(location_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(
        display_form_edit_cadet_connections_from_rota
    )


def action_if_volunteer_skills_button_pressed(
    interface: abstractInterface, volunteer_skills_button: str
) -> NewForm:
    volunteer_id = from_skills_button_to_volunteer_id(volunteer_skills_button)
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer_id)

    return interface.get_new_form_given_function(
        display_form_edit_individual_volunteer_skills_from_rota
    )


def update_if_make_available_button_pressed(
    interface: abstractInterface, available_button: str
):
    volunteer_id, day = from_known_button_to_volunteer_id_and_day(available_button)
    volunteer = get_volunteer_from_id(data_layer=interface.data, volunteer_id=volunteer_id)
    event = get_event_from_state(interface)
    make_volunteer_available_on_day(
        data_layer=interface.data, event=event, volunteer=volunteer, day=day
    )


def update_if_make_unavailable_button_pressed(
    interface: abstractInterface, unavailable_button: str
):
    volunteer_id, day = from_known_button_to_volunteer_id_and_day(unavailable_button)
    volunteer = get_volunteer_from_id(data_layer=interface.data, volunteer_id=volunteer_id)
    event = get_event_from_state(interface)
    make_volunteer_unavailable_on_day(
        data_layer=interface.data, event=event, volunteer=volunteer, day=day
    )


def update_if_remove_role_button_pressed(
    interface: abstractInterface, remove_button: str
):

    volunteer_id, day = from_known_button_to_volunteer_id_and_day(remove_button)
    volunteer = get_volunteer_from_id(data_layer=interface.data, volunteer_id=volunteer_id)
    event = get_event_from_state(interface)
    delete_role_at_event_for_volunteer_on_day(
        data_layer=interface.data, event=event, volunteer=volunteer, day=day
    )





def save_volunteer_matrix_and_return_filename(interface: abstractInterface) -> str:
    event = get_event_from_state(interface)
    sorts_and_filters = get_sorts_and_filters_from_state(interface)
    volunteer_matrix = get_volunteer_matrix(
        cache=interface.cache, event=event, sorts_and_filters=sorts_and_filters
    )
    filename = temp_file_name()
    volunteer_matrix.to_csv(filename)

    return filename

def update_filters(interface: abstractInterface):
    update_volunteer_skills_filter(interface)
    update_volunteer_availability_filter(interface)


def update_volunteer_skills_filter(interface: abstractInterface):
    dict_of_skills = get_dict_of_skills_from_form(
        interface=interface,
        field_name=SKILLS_FILTER
    )

    save_skills_filter_to_state(interface=interface, dict_of_skills=dict_of_skills)


def update_volunteer_availability_filter(interface: abstractInterface):
    event = get_event_from_state(interface)
    availabilty_filter_dict = dict(
        [
            (
                day.name,
                update_volunteer_availability_for_day(interface=interface, day=day),
            )
            for day in event.weekdays_in_event()
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
