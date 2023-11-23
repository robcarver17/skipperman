from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.abstract_form import Form

from app.logic.events.view_events import display_form_view_of_events, post_form_view_of_events
from app.logic.events.add_event import display_form_view_for_add_event, post_form_view_for_add_event
from app.logic.events.view_individual_events import display_form_view_individual_event, post_form_view_individual_event
from app.logic.events.upload_event_file import display_form_upload_event_file, post_form_upload_event_file
from app.logic.events.import_wa_file import display_form_import_event_file, post_form_import_event_file
from app.logic.events.iteratively_add_cadets_in_wa_import_stage import display_form_iteratively_add_cadets_during_import, post_form_iteratively_add_cadets_during_import
from app.logic.events.interactively_remove_duplicates import display_form_interactively_remove_duplicates_during_import, post_form_interactively_remove_duplicates_during_import
from app.logic.events.interactively_update_master_records import display_form_interactively_update_master_records, post_form_interactively_update_master_records

from app.logic.events.constants import *

class EventLogicApi(AbstractLogicApi):
    def get_displayed_form_given_form_name(self, form_name: str) -> Form:
        if form_name==INITIAL_STATE:
            return display_form_view_of_events()
        elif form_name==ADD_EVENT_STAGE:
            return display_form_view_for_add_event(self.interface)
        elif form_name==VIEW_EVENT_STAGE:
            return display_form_view_individual_event(self.interface)
        elif form_name==WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return display_form_upload_event_file(self.interface)
        elif form_name==WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return display_form_import_event_file(self.interface)
        elif form_name==WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            pass
        elif form_name==WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            return display_form_iteratively_add_cadets_during_import(self.interface)
        elif form_name==WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE:
            return display_form_interactively_remove_duplicates_during_import(self.interface)
        elif form_name==WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
            return display_form_interactively_update_master_records(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)

    def get_posted_form_given_form_name_without_checking_for_redirection(self, form_name: str) -> Form:
        if form_name==INITIAL_STATE:
            return post_form_view_of_events(self.interface)
        elif form_name == ADD_EVENT_STAGE:
            return post_form_view_for_add_event(self.interface)
        elif form_name == VIEW_EVENT_STAGE:
            return post_form_view_individual_event(self.interface)
        elif form_name == WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return post_form_upload_event_file(self.interface)
        elif form_name == WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            return post_form_import_event_file(self.interface)
        elif form_name == WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE:
            pass
        elif form_name == WA_ADD_CADET_IDS_ITERATION_IN_VIEW_EVENT_STAGE:
            return post_form_iteratively_add_cadets_during_import(self.interface)
        elif form_name == WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE:
            return post_form_interactively_remove_duplicates_during_import(self.interface)
        elif form_name == WA_PROCESS_ROWS_ITERATION_IN_VIEW_EVENT_STAGE:
            return post_form_interactively_update_master_records(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)

