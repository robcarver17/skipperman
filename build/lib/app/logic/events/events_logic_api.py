from app.logic.abstract_logic_api import LogicApi
from app.objects.abstract_objects.form_function_mapping import INITIAL_STATE

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
from app.logic.events.mapping.event_field_mapping import (
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
    post_form_add_cadet_ids_during_import,
)
from app.logic.events.cadets_at_event.interactively_update_records_of_cadets_at_event import (
    display_form_interactively_update_cadets_at_event, post_form_interactively_update_cadets_at_event,
)
from app.logic.events.import_wa.update_existing_event import (
    display_form_update_existing_event,
    post_form_update_existing_event,
)

from app.logic.events.import_wa.import_controller import import_controller, post_import_controller

from app.logic.events.group_allocation.allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)
from app.logic.events.volunteer_allocation.volunteer_identification import \
    display_form_volunteer_identification, process_volunteer_on_next_row_of_event_data, post_form_volunteer_identification_looping, \
    next_volunteer_in_current_row, \
    post_form_add_volunteers_to_cadet_loop, display_form_volunteer_selection_at_event, post_form_volunteer_identification
from app.logic.events.volunteer_rota.verify_volunteers_if_cadet_at_event_changed import \
    post_form_volunteer_rota_check, next_cadet_in_loop, display_form_volunteer_rota_check
from app.logic.events.volunteer_allocation.add_volunteers_to_event import next_volunteer_in_event, post_form_add_volunteers_to_event, display_add_volunteers_to_event

from app.logic.events.registration_details.edit_registration_details import display_form_edit_registration_details, post_form_edit_registration_details
from app.logic.events.volunteer_rota.display_main_rota_page import display_form_view_for_volunteer_rota, post_form_view_for_volunteer_rota
from app.logic.events.volunteer_rota.edit_volunteer_details_from_rota import post_form_confirm_volunteer_details_from_rota, display_form_confirm_volunteer_details_from_rota
from app.logic.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import display_form_edit_cadet_connections_from_rota, post_form_edit_cadet_connections_from_rota

from app.logic.events.volunteer_rota.edit_volunteer_skills_from_rota import display_form_edit_individual_volunteer_skills_from_rota, post_form_edit_individual_volunteer_skills_from_rota
from app.logic.events.volunteer_rota.add_volunteer_to_rota import display_form_add_new_volunteer_to_rota_at_event, post_form_add_new_volunteer_to_rota_at_event

class EventLogicApi(LogicApi):
    @property
    def display_form_name_function_mapping(self) -> dict:
        return {INITIAL_STATE:display_form_view_of_events,
                ADD_EVENT_STAGE: display_form_view_for_add_event,
                VIEW_EVENT_STAGE: display_form_view_individual_event,
                WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE: display_form_upload_event_file,

                WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE: display_form_event_field_mapping,
                WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE: display_form_for_upload_custom_field_mapping,
                WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE: display_form_for_clone_event_field_mapping,
                WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE: display_form_for_choose_template_field_mapping,
                WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE: display_form_for_upload_template_field_mapping,
                WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE: display_form_for_download_template_field_mapping,
                WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE: display_form_import_event_file,

                WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE: import_controller,
                WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE: display_form_add_cadet_ids_during_import,
                WA_UPDATE_CADETS_AT_EVENT_IN_VIEW_EVENT_STAGE: display_form_interactively_update_cadets_at_event,

                WA_VOLUNTEER_IDENITIFICATION_INITIALISE_IN_VIEW_EVENT_STAGE: display_form_volunteer_identification,
                WA_VOLUNTEER_IDENITIFICATION_LOOP_IN_VIEW_EVENT_STAGE: process_volunteer_on_next_row_of_event_data,


                WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_LOOP_IN_VIEW_EVENT_STAGE: next_volunteer_in_current_row,

                WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE:display_form_volunteer_selection_at_event,

                VOLUNTEER_DETAILS_INITIALISE_IN_VIEW_EVENT_STAGE: display_add_volunteers_to_event,
                VOLUNTEER_DETAILS_LOOP_IN_VIEW_EVENT_STAGE: next_volunteer_in_event,

                WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE: display_form_update_existing_event,

                ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE: display_form_allocate_cadets,
                EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE: display_form_edit_registration_details,

                VOLUNTEER_ROTA_INITIALISE_LOOP_IN_VIEW_EVENT_STAGE: display_form_volunteer_rota_check,
                VOLUNTEER_ROTA_CHECK_LOOP_IN_VIEW_EVENT_STAGE: next_cadet_in_loop,

                EDIT_VOLUNTEER_ROTA_EVENT_STAGE: display_form_view_for_volunteer_rota,
                EDIT_VOLUNTEER_DETAILS_FROM_ROTA_EVENT_STAGE: display_form_confirm_volunteer_details_from_rota,
                EDIT_CADET_CONNECTIONS_FROM_ROTA_EVENT_STAGE: display_form_edit_cadet_connections_from_rota,
                EDIT_VOLUNTEER_SKILLS_FROM_ROTA_EVENT_STAGE: display_form_edit_individual_volunteer_skills_from_rota,
                ADD_NEW_VOLUNTEER_TO_ROTA_EVENT_STAGE: display_form_add_new_volunteer_to_rota_at_event}

    @property
    def post_form_name_function_mapping(self) -> dict:
        return {
        INITIAL_STATE:
            post_form_view_of_events,
        ADD_EVENT_STAGE:
            post_form_view_for_add_event,
        VIEW_EVENT_STAGE:
            post_form_view_individual_event,
        WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            post_form_upload_event_file,
        WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE:
            post_form_event_field_mapping,
        WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            post_form_for_upload_custom_field_mapping,
        WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            post_form_for_clone_event_field_mapping,

        WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            post_form_for_choose_template_field_mapping,
        WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            post_form_for_upload_template_field_mapping,
        WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE:
            post_form_for_download_template_field_mapping,

        WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            post_form_import_event_file,

        WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE:
            post_import_controller,

        WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            post_form_add_cadet_ids_during_import,
        WA_UPDATE_CADETS_AT_EVENT_IN_VIEW_EVENT_STAGE:
            post_form_interactively_update_cadets_at_event,

        WA_VOLUNTEER_IDENITIFICATION_INITIALISE_IN_VIEW_EVENT_STAGE:
            post_form_volunteer_identification,

        WA_VOLUNTEER_IDENITIFICATION_LOOP_IN_VIEW_EVENT_STAGE: post_form_volunteer_identification_looping,
        WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE: post_form_volunteer_identification,

        WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_LOOP_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_cadet_loop,

        VOLUNTEER_DETAILS_LOOP_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_event,

            WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            post_form_update_existing_event,

        ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE:
            post_form_allocate_cadets,

        EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE:
            post_form_edit_registration_details,


        VOLUNTEER_ROTA_CHECK_LOOP_IN_VIEW_EVENT_STAGE: post_form_volunteer_rota_check,

        EDIT_VOLUNTEER_ROTA_EVENT_STAGE: post_form_view_for_volunteer_rota,
        EDIT_VOLUNTEER_DETAILS_FROM_ROTA_EVENT_STAGE: post_form_confirm_volunteer_details_from_rota,
        EDIT_CADET_CONNECTIONS_FROM_ROTA_EVENT_STAGE: post_form_edit_cadet_connections_from_rota,
        EDIT_VOLUNTEER_SKILLS_FROM_ROTA_EVENT_STAGE: post_form_edit_individual_volunteer_skills_from_rota,
        ADD_NEW_VOLUNTEER_TO_ROTA_EVENT_STAGE: post_form_add_new_volunteer_to_rota_at_event
        }

