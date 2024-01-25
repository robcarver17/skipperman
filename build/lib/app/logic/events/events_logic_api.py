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
from app.logic.events.import_wa.iteratively_add_cadets_in_wa_import_stage import (
    display_form_iteratively_add_cadets_during_import,
    post_form_iteratively_add_cadets_during_import,
)
from app.logic.events.update_master.interactively_update_master_records import (
    display_form_interactively_update_master_records, post_form_interactively_update_master_records,
)
from app.logic.events.import_wa.update_existing_event import (
    display_form_update_existing_event,
    post_form_uupdate_existing_event,
)

from app.logic.events.allocation.allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)
from app.logic.events.volunteer_allocation.volunteer_extraction_given_master_file import display_form_volunteer_extraction_from_master_records_initalise_loop, post_form_volunteer_extraction_initialise_from_master_records, display_form_volunteer_extraction_from_master_records_looping, post_form_volunteer_extraction_from_master_records_looping
from app.logic.events.volunteer_allocation.verify_volunteers_if_cadet_deleted import display_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled, post_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled
from app.logic.events.volunteer_allocation.volunteer_selection import post_form_volunteer_selection_for_cadet_at_event
from app.logic.events.volunteer_allocation.add_volunteers_to_cadet import \
    display_form_add_volunteers_to_cadet_initialise, post_form_add_volunteers_to_cadet_initialise, \
    display_form_add_volunteers_to_cadet_loop, post_form_add_volunteers_to_cadet_loop, \
    add_specific_volunteer_for_cadet_at_event
from app.logic.events.volunteer_allocation.confirm_volunteer_details import display_form_confirm_volunteer_details, post_form_confirm_volunteer_details
from app.logic.events.volunteer_allocation.volunteer_selection import display_form_volunteer_selection_for_cadet_at_event, post_form_volunteer_selection_for_cadet_at_event

from app.logic.events.registration_details.edit_registration_details import display_form_edit_registration_details, post_form_edit_registration_details
from app.logic.events.constants import *


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
                WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE: display_form_iteratively_add_cadets_during_import,
                WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE: display_form_interactively_update_master_records,

                WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE: display_form_volunteer_extraction_from_master_records_initalise_loop,
                WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE: display_form_volunteer_extraction_from_master_records_looping,
                WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE: display_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled,
                WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_INIT_IN_VIEW_EVENT_STAGE: display_form_add_volunteers_to_cadet_initialise,
                WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE: display_form_add_volunteers_to_cadet_loop,

                WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE:display_form_volunteer_selection_for_cadet_at_event,
                WA_VOLUNTEER_EXTRACTION_ADD_DETAILS_IN_VIEW_EVENT_STAGE: display_form_confirm_volunteer_details,

                WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE: display_form_update_existing_event,
                ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE: display_form_allocate_cadets,
                EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE: display_form_edit_registration_details
                }

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
        WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            post_form_iteratively_add_cadets_during_import,
        WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
            post_form_interactively_update_master_records,

        WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE:
            post_form_volunteer_extraction_initialise_from_master_records,

        WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE: post_form_volunteer_extraction_from_master_records_looping,
        WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE: post_form_volunteer_extraction_from_master_records_if_cadet_is_deleted_or_cancelled,
        WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE: post_form_volunteer_selection_for_cadet_at_event,
        WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_INIT_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_cadet_initialise,

        WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE: post_form_add_volunteers_to_cadet_loop,

        WA_VOLUNTEER_EXTRACTION_ADD_DETAILS_IN_VIEW_EVENT_STAGE: post_form_confirm_volunteer_details,

            WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            post_form_uupdate_existing_event,

        ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE:
            post_form_allocate_cadets,

        EDIT_CADET_REGISTRATION_DATA_IN_VIEW_EVENT_STAGE:
            post_form_edit_registration_details,


        }

