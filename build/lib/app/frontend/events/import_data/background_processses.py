from app.backend.groups.previous_groups import \
    update_dict_of_group_names_for_events_and_cadets_persistent_version_from_core_data
from app.backend.volunteers.volunteers_with_most_common_role_and_group_at_event import \
    update_dict_of_volunteers_with_most_common_role_and_group_across_events_from_core_data
from app.frontend.form_handler import initial_state_form
from app.objects.abstract_objects.abstract_form import NewForm

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

def display_call_to_update_background_data_during_import(
        interface: abstractInterface,
) -> NewForm:
    #update_dict_of_group_names_for_events_and_cadets_persistent_version_from_core_data(interface.object_store)
    #update_dict_of_volunteers_with_most_common_role_and_group_across_events_from_core_data(interface.object_store)

    #### BOTH OF THESE ARE TOO SLOW

    return interface.get_new_display_form_for_parent_of_function(
        display_call_to_update_background_data_during_import
    )

def post_call_to_update_background_data_during_import(
        interface: abstractInterface,
) -> NewForm:
    interface.log_error(
        "Serious error: should never get to post_call_to_update_background_data_during_import"
    )
    return initial_state_form()
