from app.logic.abstract_logic_api import LogicApi
from app.objects.abstract_objects.form_function_mapping import INITIAL_STATE
from app.logic.reporting.ENTRY_view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.logic.reporting.rota.report_rota import *

from app.logic.reporting.allocations.report_group_allocations import *


class ReportingLogicApi(LogicApi):
    @property
    def display_form_name_function_mapping(self) -> dict:
        return {
                INITIAL_STATE:
                    display_form_view_of_reports,
                GROUP_ALLOCATION_REPORT_STAGE:
                     display_form_report_group_allocation,
                REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
                     display_form_for_report_group_additional_options,
                GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_report_group_allocation_all_options,
                CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_group_arrangement_options_allocation_report,
                CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
                     display_form_for_report_group_allocation_print_options,

                ROTA_REPORT_STAGE:
                    display_form_report_rota,
            GENERIC_OPTIONS_IN_ROTA_REPORT_STATE:
                    display_form_for_rota_report_all_options,
            REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE:
                display_form_for_rota_report_additional_options,
            CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE:
                display_form_for_group_arrangement_options_rota_report,
            CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE:
                display_form_for_rota_report_print_options

        }

    @property
    def post_form_name_function_mapping(self) -> dict:
        return {
        INITIAL_STATE:
             post_form_view_of_reports,
         GROUP_ALLOCATION_REPORT_STAGE:
             post_form_report_group_allocation,
         GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_all_options,
         REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
             post_form_for_report_group_additional_options,
         CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
             post_form_for_group_arrangement_options_allocation_report,
         CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_print_options,

            ROTA_REPORT_STAGE:
                post_form_report_rota,
            GENERIC_OPTIONS_IN_ROTA_REPORT_STATE:
                post_form_for_rota_report_all_options,
            REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE:
                post_form_for_rota_report_additional_options,
            CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE:
                post_form_for_group_arrangement_options_rota_report,
            CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE:
                post_form_for_rota_report_print_options
        }
