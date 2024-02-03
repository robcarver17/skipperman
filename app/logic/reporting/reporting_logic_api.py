from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.reporting.view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.logic.reporting.allocations.report_group_allocations import *


class ReportingLogicApi(AbstractLogicApi):
    @property
    def dict_of_display_forms(self) -> dict:
        return {
                INITIAL_STATE:
                    display_form_view_of_reports,
                GROUP_ALLOCATION_REPORT_STAGE:
                     display_form_report_group_allocation,
                REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
                     display_form_for_report_group_additional_options,
                GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_report_group_allocation_generic_options,
                CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_group_arrangement_options_allocation_report,
                CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_report_group_allocation_print_options
            }

    @property
    def dict_of_posted_forms(self) -> dict:
        return {
        INITIAL_STATE:
             post_form_view_of_reports,
         GROUP_ALLOCATION_REPORT_STAGE:
             post_form_report_group_allocation,
         REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
             post_form_for_report_group_allocation_options,
         GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_generic_options,
         CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
             post_form_for_group_arrangement_options_allocation_report,
         CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_print_options
        }
