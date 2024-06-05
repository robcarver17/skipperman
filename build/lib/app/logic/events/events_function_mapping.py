from app.logic.events.clothing.ENTRY_clothing import display_form_view_for_clothing_requirements, \
    post_form_view_for_clothing_requirements
from app.logic.events.food.ENTRY_food import display_form_view_for_food_requirements, \
    post_form_view_for_food_requirements
from app.logic.events.ENTRY_view_events import (
    display_form_view_of_events,
    post_form_view_of_events,
)
from app.logic.events.add_event import (
    display_form_view_for_add_event,
    post_form_view_for_add_event,
)
from app.logic.events.view_individual_events import (
    display_form_view_individual_event,
    post_form_view_individual_event,
)
from app.logic.events.import_wa.upload_event_file import (
    display_form_upload_event_file,
    post_form_upload_event_file,
)
from app.logic.events.mapping.ENTRY_event_field_mapping import (
    display_form_event_field_mapping,
    post_form_event_field_mapping,
)
from app.logic.events.mapping.upload_field_mapping import (
    display_form_for_upload_custom_field_mapping,
    post_form_for_upload_custom_field_mapping,
)
from app.logic.events.mapping.template_field_mapping import (
    display_form_for_choose_template_field_mapping,
    post_form_for_choose_template_field_mapping,
)
from app.logic.events.mapping.upload_template_field_mapping import display_form_for_upload_template_field_mapping, \
    post_form_for_upload_template_field_mapping
from app.logic.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
    post_form_for_clone_event_field_mapping,
)
from app.logic.events.mapping.download_template_field_mapping import (
    display_form_for_download_template_field_mapping,
    post_form_for_download_template_field_mapping,
)
from app.logic.events.import_wa.import_wa_file import (
    display_form_import_event_file,
    post_form_import_event_file,
)
from app.logic.events.cadets_at_event.iteratively_add_cadet_ids_in_wa_import_stage import (
    display_form_add_cadet_ids_during_import,
    post_form_add_cadet_ids_during_import
)
from app.logic.events.cadets_at_event.interactively_update_records_of_cadets_at_event import (
    display_form_interactively_update_cadets_at_event, post_form_interactively_update_cadets_at_event,
)
from app.logic.events.import_wa.update_existing_event import (
    display_form_update_existing_event,
    post_form_update_existing_event,
)

from app.logic.events.import_wa.import_controller import import_controller, post_import_controller

from app.logic.events.group_allocation.ENTRY_allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)
from app.logic.events.group_allocation.add_cadet_partner import display_add_cadet_partner, post_form_add_cadet_partner
from app.logic.events.volunteer_allocation.volunteer_identification import \
    display_form_volunteer_identification, post_form_volunteer_identification
from app.logic.events.volunteer_allocation.add_volunteers_to_event import post_form_add_volunteers_to_event, display_add_volunteers_to_event

from app.logic.events.registration_details.edit_registration_details import display_form_edit_registration_details, post_form_edit_registration_details
from app.logic.events.volunteer_rota.ENTRY1_display_main_rota_page import display_form_view_for_volunteer_rota, post_form_view_for_volunteer_rota
from app.logic.events.volunteer_rota.edit_volunteer_details_from_rota import post_form_confirm_volunteer_details_from_rota, display_form_confirm_volunteer_details_from_rota
from app.logic.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import display_form_edit_cadet_connections_from_rota, post_form_edit_cadet_connections_from_rota

from app.logic.events.volunteer_rota.edit_volunteer_skills_from_rota import display_form_edit_individual_volunteer_skills_from_rota, post_form_edit_individual_volunteer_skills_from_rota
from app.logic.events.volunteer_rota.add_volunteer_to_rota import display_form_add_new_volunteer_to_rota_at_event, post_form_add_new_volunteer_to_rota_at_event
from app.logic.events.patrol_boats.ENTRY_allocate_patrol_boats import display_form_view_for_patrol_boat_allocation, post_form_view_for_patrol_boat_allocation

from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings
from app.logic.events.mapping.create_mapping import display_form_for_create_custom_field_mapping, post_form_for_create_custom_field_mapping

event_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_view_of_events, post_form_view_of_events):
                {
                    (display_form_view_for_add_event, post_form_view_for_add_event):0,
                    (display_form_view_individual_event, post_form_view_individual_event):
                        {
                            (display_form_upload_event_file, post_form_upload_event_file):0,
                            (display_form_allocate_cadets, post_form_allocate_cadets):
                                {
                                    (display_add_cadet_partner, post_form_add_cadet_partner): 0
                                }
                            ,
                            (display_form_edit_registration_details, post_form_edit_registration_details):0,
                            (display_form_view_for_volunteer_rota, post_form_view_for_volunteer_rota):
                                {
                                    (display_form_add_new_volunteer_to_rota_at_event, post_form_add_new_volunteer_to_rota_at_event):0,
                                    (display_form_confirm_volunteer_details_from_rota, post_form_confirm_volunteer_details_from_rota):0,
                                    (display_form_edit_cadet_connections_from_rota, post_form_edit_cadet_connections_from_rota):0,
                                    (display_form_edit_individual_volunteer_skills_from_rota, post_form_edit_individual_volunteer_skills_from_rota):0
                                },
                            (display_form_view_for_patrol_boat_allocation, post_form_view_for_patrol_boat_allocation):0,
                            (display_form_update_existing_event, post_form_update_existing_event): 0,
                            (display_form_view_for_food_requirements, post_form_view_for_food_requirements):0,
                            (display_form_view_for_clothing_requirements, post_form_view_for_clothing_requirements):0,

                            (display_form_event_field_mapping, post_form_event_field_mapping):
                                {
                                    (display_form_for_choose_template_field_mapping, post_form_for_choose_template_field_mapping):
                                        {
                                            (display_form_for_upload_template_field_mapping, post_form_for_upload_template_field_mapping):0,

                                        },
                                    (display_form_for_clone_event_field_mapping, post_form_for_clone_event_field_mapping):0,
                                    (display_form_for_create_custom_field_mapping, post_form_for_create_custom_field_mapping):
                                        {
                                            (display_form_for_download_template_field_mapping, post_form_for_download_template_field_mapping):0,
                                            (display_form_for_upload_custom_field_mapping, post_form_for_upload_custom_field_mapping):0,
                                        },
                                },
                            (display_form_import_event_file, post_form_import_event_file): 0,
                            (import_controller, post_import_controller):
                                {
                                    (display_form_add_cadet_ids_during_import,post_form_add_cadet_ids_during_import):0,
                                    (display_form_interactively_update_cadets_at_event,post_form_interactively_update_cadets_at_event):0,

                                    (display_form_volunteer_identification, post_form_volunteer_identification):0,
                                    (display_add_volunteers_to_event,post_form_add_volunteers_to_event):0,


}

                        },

                }
        }
    )
)