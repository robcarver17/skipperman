from app.frontend.events.clothing.ENTRY_clothing import (
    display_form_view_for_clothing_requirements,
    post_form_view_for_clothing_requirements,
)
from app.frontend.events.food.ENTRY_food import (
    display_form_view_for_food_requirements,
    post_form_view_for_food_requirements,
)
from app.frontend.events.ENTRY_view_events import (
    display_form_view_of_events,
    post_form_view_of_events,
)
from app.frontend.events.add_event import (
    display_form_view_for_add_event,
    post_form_view_for_add_event,
)
from app.frontend.events.view_individual_events import (
    display_form_view_individual_event,
    post_form_view_individual_event,
)
from app.frontend.events.import_data.upload_event_file import (
    display_form_upload_event_file,
    post_form_upload_event_file,
)
from app.frontend.events.mapping.ENTRY_event_field_mapping import (
    display_form_event_field_mapping,
    post_form_event_field_mapping,
)
from app.frontend.events.mapping.upload_field_mapping import (
    display_form_for_upload_custom_field_mapping,
    post_form_for_upload_custom_field_mapping,
)
from app.frontend.events.mapping.template_field_mapping import (
    display_form_for_choose_template_field_mapping,
    post_form_for_choose_template_field_mapping,
)
from app.frontend.events.mapping.upload_template_field_mapping import (
    display_form_for_upload_template_field_mapping,
    post_form_for_upload_template_field_mapping,
)
from app.frontend.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
    post_form_for_clone_event_field_mapping,
)
from app.frontend.events.mapping.download_field_mapping import (
    display_form_for_download_field_mapping,
    post_form_for_download_field_mapping,
)

from app.frontend.events.cadets_at_event.iteratively_identify_cadets_in_import_stage import (
    display_form_identify_cadets_during_import,
    post_form_add_cadet_ids_during_import,
)
from app.frontend.events.cadets_at_event.interactively_update_records_of_cadets_at_event import (
    display_form_interactively_update_cadets_at_event,
    post_form_interactively_update_cadets_at_event,
)

from app.frontend.events.import_data.import_controller import (
    import_controller,
    post_import_controller,
)

from app.frontend.events.import_data.import_wa_file import (
    display_form_import_event_file,
    post_form_import_event_file,
)

from app.frontend.events.group_allocation.ENTRY_allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)
from app.frontend.events.group_allocation.add_cadet_partner import (
    display_add_cadet_partner,
    post_form_add_cadet_partner,
)
from app.frontend.events.registration_details.add_unregistered_cadet import (
    display_add_unregistered_cadet_from_registration_form,
    post_form_add_unregistered_cadet_from_registration_form,
)
from app.frontend.events.volunteer_identification.ENTRY_volunteer_identification import (
    display_form_volunteer_identification,
    post_form_volunteer_identification,
)
from app.frontend.events.volunteer_identification.add_volunteers_to_event import (
    post_add_volunteers_to_event,
    display_add_volunteers_to_event,
)

from app.frontend.events.registration_details.ENTRY_edit_registration_details import (
    display_form_edit_registration_details,
    post_form_edit_registration_details,
)
from app.frontend.events.volunteer_rota.ENTRY1_display_main_rota_page import (
    display_form_view_for_volunteer_rota,
    post_form_view_for_volunteer_rota,
)
from app.frontend.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import (
    display_form_edit_cadet_connections_from_rota,
    post_form_edit_cadet_connections_from_rota,
)

from app.frontend.events.volunteer_rota.edit_volunteer_skills_from_rota import (
    display_form_edit_individual_volunteer_skills_from_rota,
    post_form_edit_individual_volunteer_skills_from_rota,
)
from app.frontend.events.volunteer_rota.add_volunteer_to_rota import (
    display_form_add_new_volunteer_to_rota_at_event,
    post_form_add_new_volunteer_to_rota_at_event,
)
from app.frontend.events.patrol_boats.ENTRY_allocate_patrol_boats import (
    display_form_view_for_patrol_boat_allocation,
    post_form_view_for_patrol_boat_allocation,
)

from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)
from app.frontend.events.mapping.create_mapping import (
    display_form_for_create_custom_field_mapping,
    post_form_for_create_custom_field_mapping,
)
from app.frontend.events.import_data.ENTRY_import_choose import (
    display_form_choose_import_source,
    post_form_choose_import_source,
)
from app.frontend.events.import_data.wa_import_gateway import (
    display_form_WA_import_gateway,
    post_form_WA_import_gateway,
)

from app.frontend.events.clothing.automatically_get_clothing_data_from_cadets import (
    display_call_to_update_cadet_clothing_at_event_during_import,
    post_call_to_update_cadet_clothing_at_event_during_import,
)
from app.frontend.events.food.automatically_get_food_data import (
    display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
    post_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
)
from app.frontend.events.group_allocation.add_unregistered_cadet import (
    display_add_unregistered_cadet_from_allocation_form,
    post_form_add_unregistered_cadet_from_allocation_form,
)
from app.frontend.events.group_allocation.change_sort_order import (
    display_change_sort_order,
    post_change_sort_order,
)
from app.frontend.events.volunteer_rota.copy_menu import (
    display_form_volunteer_copy_menu,
    post_form_volunteer_copy_menu,
)
from app.frontend.events.patrol_boats.copy_menu import (
    display_form_patrol_boat_copy_menu,
    post_form_patrol_boat_copy_menu,
)

event_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_view_of_events, post_form_view_of_events): {
                (display_form_view_for_add_event, post_form_view_for_add_event): 0,
                (display_form_view_individual_event, post_form_view_individual_event): {
                    (
                        display_form_choose_import_source,
                        post_form_choose_import_source,
                    ): {
                        (display_form_WA_import_gateway, post_form_WA_import_gateway): {
                            (
                                display_form_upload_event_file,
                                post_form_upload_event_file,
                            ): 0,
                            (
                                display_form_import_event_file,
                                post_form_import_event_file,
                            ): {
                                (import_controller, post_import_controller): {
                                    (
                                        display_form_identify_cadets_during_import,
                                        post_form_add_cadet_ids_during_import,
                                    ): 0,
                                    (
                                        display_form_interactively_update_cadets_at_event,
                                        post_form_interactively_update_cadets_at_event,
                                    ): 0,
                                    (
                                        display_form_volunteer_identification,
                                        post_form_volunteer_identification,
                                    ): 0,
                                    (
                                        display_add_volunteers_to_event,
                                        post_add_volunteers_to_event,
                                    ): 0,
                                    (
                                        display_call_to_update_cadet_clothing_at_event_during_import,
                                        post_call_to_update_cadet_clothing_at_event_during_import,
                                    ): 0,
                                    (
                                        display_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
                                        post_call_to_update_food_for_cadets_and_volunteers_from_registration_data_on_import,
                                    ): 0,
                                },
                            },
                            (
                                display_form_event_field_mapping,
                                post_form_event_field_mapping,
                            ): {
                                (
                                    display_form_for_choose_template_field_mapping,
                                    post_form_for_choose_template_field_mapping,
                                ): {
                                    (
                                        display_form_for_upload_template_field_mapping,
                                        post_form_for_upload_template_field_mapping,
                                    ): 0,
                                },
                                (
                                    display_form_for_clone_event_field_mapping,
                                    post_form_for_clone_event_field_mapping,
                                ): 0,
                                (
                                    display_form_for_create_custom_field_mapping,
                                    post_form_for_create_custom_field_mapping,
                                ): {
                                    (
                                        display_form_for_download_field_mapping,
                                        post_form_for_download_field_mapping,
                                    ): 0,
                                    (
                                        display_form_for_upload_custom_field_mapping,
                                        post_form_for_upload_custom_field_mapping,
                                    ): 0,
                                },
                            },
                        },
                    },
                    (display_form_allocate_cadets, post_form_allocate_cadets): {
                        (display_add_cadet_partner, post_form_add_cadet_partner): 0,
                        (display_change_sort_order, post_change_sort_order): 0,
                        (
                            display_add_unregistered_cadet_from_allocation_form,
                            post_form_add_unregistered_cadet_from_allocation_form,
                        ): 0,
                    },
                    (
                        display_form_edit_registration_details,
                        post_form_edit_registration_details,
                    ): {
                        (
                            display_add_unregistered_cadet_from_registration_form,
                            post_form_add_unregistered_cadet_from_registration_form,
                        ): 0
                    },
                    (
                        display_form_view_for_volunteer_rota,
                        post_form_view_for_volunteer_rota,
                    ): {
                        (
                            display_form_add_new_volunteer_to_rota_at_event,
                            post_form_add_new_volunteer_to_rota_at_event,
                        ): 0,
                        (
                            display_form_edit_cadet_connections_from_rota,
                            post_form_edit_cadet_connections_from_rota,
                        ): 0,
                        (
                            display_form_edit_individual_volunteer_skills_from_rota,
                            post_form_edit_individual_volunteer_skills_from_rota,
                        ): 0,
                        (
                            display_form_volunteer_copy_menu,
                            post_form_volunteer_copy_menu,
                        ): 0,
                    },
                    (
                        display_form_view_for_patrol_boat_allocation,
                        post_form_view_for_patrol_boat_allocation,
                    ): {
                        (
                            display_form_patrol_boat_copy_menu,
                            post_form_patrol_boat_copy_menu,
                        ): 0
                    },
                    (
                        display_form_view_for_food_requirements,
                        post_form_view_for_food_requirements,
                    ): 0,
                    (
                        display_form_view_for_clothing_requirements,
                        post_form_view_for_clothing_requirements,
                    ): 0,
                },
            }
        }
    )
)
