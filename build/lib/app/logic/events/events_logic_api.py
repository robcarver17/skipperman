from typing import Union
from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.forms_and_interfaces.abstract_form import Form, File

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
    display_form_for_upload_template_field_mapping,
    post_form_for_upload_template_field_mapping,
)
from app.logic.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
    post_form_for_clone_event_field_mapping,
)
from app.logic.events.mapping.check_mapping import display_form_check_field_mapping, post_form_check_field_mapping
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
from app.logic.events.import_wa.interactively_update_master_records import (
    display_form_interactively_update_master_records,
    post_form_interactively_update_master_records,
)
from app.logic.events.import_wa.update_existing_event import (
    display_form_update_existing_event,
    post_form_uupdate_existing_event,
)

from app.logic.events.allocation.allocate_cadets_to_groups import (
    display_form_allocate_cadets,
    post_form_allocate_cadets,
)

from app.logic.events.constants import *


class EventLogicApi(AbstractLogicApi):
    def get_displayed_form_given_form_name(self, form_name: str) -> Form:
        print("get form name %s" % form_name)
        if form_name == INITIAL_STATE:
            return display_form_view_of_events()
        elif form_name == ADD_EVENT_STAGE:
            return display_form_view_for_add_event(self.interface)
        elif form_name == VIEW_EVENT_STAGE:
            return display_form_view_individual_event(self.interface)

        elif form_name == WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return display_form_upload_event_file(self.interface)

        elif form_name == WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE:
            return display_form_event_field_mapping(self.interface)
        elif form_name == WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            return display_form_for_upload_custom_field_mapping(self.interface)
        elif form_name == WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            return display_form_for_clone_event_field_mapping(self.interface)
        elif form_name == WA_CHECK_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return display_form_check_field_mapping(self.interface)

        elif form_name == WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return display_form_for_choose_template_field_mapping(self.interface)
        elif form_name == WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return display_form_for_upload_template_field_mapping(self.interface)
        elif form_name == WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE:
            return display_form_for_download_template_field_mapping(self.interface)

        elif form_name == WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return display_form_import_event_file(self.interface)
        elif form_name == WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            return display_form_iteratively_add_cadets_during_import(self.interface)
        elif form_name == WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
            return display_form_interactively_update_master_records(self.interface)

        elif form_name == WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return display_form_update_existing_event(self.interface)

        elif form_name == WA_ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE:
            return display_form_allocate_cadets(self.interface)

        else:
            raise Exception("Form name %s not recognised" % form_name)

    def get_posted_form_given_form_name_without_checking_for_redirection(
        self, form_name: str
    ) -> Union[Form, File]:
        print("post form name %s" % form_name)
        if form_name == INITIAL_STATE:
            return post_form_view_of_events(self.interface)
        elif form_name == ADD_EVENT_STAGE:
            return post_form_view_for_add_event(self.interface)
        elif form_name == VIEW_EVENT_STAGE:
            return post_form_view_individual_event(self.interface)
        elif form_name == WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return post_form_upload_event_file(self.interface)
        elif form_name == WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE:
            return post_form_event_field_mapping(self.interface)
        elif form_name == WA_UPLOAD_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            return post_form_for_upload_custom_field_mapping(self.interface)
        elif form_name == WA_CLONE_EVENT_MAPPING_IN_VIEW_EVENT_STAGE:
            return post_form_for_clone_event_field_mapping(self.interface)
        elif form_name == WA_CHECK_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return post_form_check_field_mapping(self.interface)

        elif form_name == WA_SELECT_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return post_form_for_choose_template_field_mapping(self.interface)
        elif form_name == WA_UPLOAD_MAPPING_TEMPLATE_IN_VIEW_EVENT_STAGE:
            return post_form_for_upload_template_field_mapping(self.interface)
        elif form_name == WA_DOWNLOAD_EVENT_TEMPLATE_MAPPING_IN_VIEW_EVENT_STAGE:
            return post_form_for_download_template_field_mapping(self.interface)

        elif form_name == WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return post_form_import_event_file(self.interface)
        elif form_name == WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            return post_form_iteratively_add_cadets_during_import(self.interface)
        elif form_name == WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
            return post_form_interactively_update_master_records(self.interface)

        elif form_name == WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return post_form_uupdate_existing_event(self.interface)

        elif form_name == WA_ALLOCATE_CADETS_IN_VIEW_EVENT_STAGE:
            return post_form_allocate_cadets(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)
