from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE

from app.logic.events.view_events import (
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
    post_form_uupdate_existing_event,
)

from app.logic.events.import_wa.import_controller import import_controller, post_import_controller

from app.logic.events.allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)
from app.logic.events.volunteer_allocation.volunteer_identification import \
    display_form_volunteer_identification_initalise_loop, post_form_volunteer_identification_initialise, \
    display_form_volunteer_identification_from_mapped_event_data, post_form_volunteer_identification_looping, \
    identify_volunteers_in_specific_row_initialise, identify_volunteers_in_specific_row_loop, \
    post_form_add_volunteers_to_cadet_initialise, post_form_add_volunteers_to_cadet_loop
from app.logic.events.volunteer_rota.verify_volunteers_if_cadet_deleted import display_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled, post_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled
from app.logic.events.volunteer_allocation.add_volunteers_to_event import loop_over_volunteers_identified_in_event, post_form_confirm_volunteer_details
from app.logic.events.volunteer_allocation.volunteer_selection import display_form_volunteer_selection_at_event, post_form_volunteer_selection

from app.logic.events.registration_details.edit_registration_details import display_form_edit_registration_details, post_form_edit_registration_details
from app.logic.events.volunteer_rota.display_main_rota_page import display_form_view_for_volunteer_rota, post_form_view_for_volunteer_rota
from app.logic.events.volunteer_rota.edit_volunteer_details_from_rota import post_form_confirm_volunteer_details_from_rota, display_form_confirm_volunteer_details_from_rota
from app.logic.events.volunteer_rota.edit_cadet_connections_for_event_from_rota import display_form_edit_cadet_connections_from_rota, post_form_edit_cadet_connections_from_rota

from app.logic.events.constants import *
from app.logic.events.volunteer_rota.edit_volunteer_skills_from_rota import display_form_edit_individual_volunteer_skills_from_rota, post_form_edit_individual_volunteer_skills_from_rota
from app.logic.events.volunteer_rota.add_volunteer_to_rota import display_form_add_new_volunteer_to_rota_at_event, post_form_add_new_volunteer_to_rota_at_event

class EventLogicApi(AbstractLogicApi):
    @property
    def dict_of_display_forms(self) -> dict:
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

                WA_VOLUNTEER_IDENITIFICATION_INITIALISE_IN_VIEW_EVENT_STAGE: display_form_volunteer_identification_initalise_loop,
                WA_VOLUNTEER_IDENITIFICATION_LOOP_IN_VIEW_EVENT_STAGE: display_form_volunteer_identification_from_mapped_event_data,
                WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE: display_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled,
                WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_INIT_IN_VIEW_EVENT_STAGE: identify_volunteers_in_specific_row_initialise,
                WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_LOOP_IN_VIEW_EVENT_STAGE: identify_volunteers_in_specific_row_loop,

                WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE:display_form_volunteer_selection_at_event,
                VOLUNTEER_DETAILS_LOOP_IN_VIEW_EVENT_STAGE: loop_over_volunteers_identified_in_event,

                WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE: display_form_update_existing_event,

                ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE: display_form_allocate_cadets,
                EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE: display_form_edit_registration_details,
                EDIT_VOLUNTEER_ROTA_EVENT_STAGE: display_form_view_for_volunteer_rota,
                EDIT_VOLUNTEER_DETAILS_FROM_ROTA_EVENT_STAGE: display_form_confirm_volunteer_details_from_rota,
                EDIT_CADET_CONNECTIONS_FROM_ROTA_EVENT_STAGE: display_form_edit_cadet_connections_from_rota,
                EDIT_VOLUNTEER_SKILLS_FROM_ROTA_EVENT_STAGE: display_form_edit_individual_volunteer_skills_from_rota,
                ADD_NEW_VOLUNTEER_TO_ROTA_EVENT_STAGE: display_form_add_new_volunteer_to_rota_at_event}

    @property
    def dict_of_posted_forms(self) -> dict:
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
            post_form_volunteer_identification_initialise,

        WA_VOLUNTEER_IDENITIFICATION_LOOP_IN_VIEW_EVENT_STAGE: post_form_volunteer_identification_looping,
        WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE: post_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled,
        WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE: post_form_volunteer_selection,
        WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_INIT_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_cadet_initialise,

        WA_IDENTIFY_VOLUNTEERS_IN_SPECIFIC_ROW_LOOP_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_cadet_loop,

        VOLUNTEER_DETAILS_LOOP_IN_VIEW_EVENT_STAGE: post_form_confirm_volunteer_details,

            WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            post_form_uupdate_existing_event,

        ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE:
            post_form_allocate_cadets,

        EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE:
            post_form_edit_registration_details,

        EDIT_VOLUNTEER_ROTA_EVENT_STAGE: post_form_view_for_volunteer_rota,
        EDIT_VOLUNTEER_DETAILS_FROM_ROTA_EVENT_STAGE: post_form_confirm_volunteer_details_from_rota,
        EDIT_CADET_CONNECTIONS_FROM_ROTA_EVENT_STAGE: post_form_edit_cadet_connections_from_rota,
        EDIT_VOLUNTEER_SKILLS_FROM_ROTA_EVENT_STAGE: post_form_edit_individual_volunteer_skills_from_rota,
        ADD_NEW_VOLUNTEER_TO_ROTA_EVENT_STAGE: post_form_add_new_volunteer_to_rota_at_event
        }

