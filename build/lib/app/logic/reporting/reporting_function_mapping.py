from app.logic.reporting.ENTRY_view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.logic.reporting.rota.report_rota import *

from app.logic.reporting.allocations.report_group_allocations import *
from app.objects.abstract_objects.form_function_mapping import FormNameFunctionNameMapping, \
    DisplayAndPostFormFunctionMaps, INITIAL_STATE

# STAGES

GROUP_ALLOCATION_REPORT_STAGE = "group_allocation_report"
ROTA_REPORT_STAGE = "rota_report"

## GROUP ALLOCATION

GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE = "generic_options_in_group_allocation_state"
REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT = (
    "report_additional_options_in_group_allocation_state"
)
CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE = (
    "change_group_layout_in_group_allocation_state"
)
CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE = (
    "change_print_options_in_group_allocation_state"
)

## ROTA
GENERIC_OPTIONS_IN_ROTA_REPORT_STATE = "generic_options_in_rota_report_state"
REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE = (
    "rota_report_additional_options_in_state"
)
CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE = (
    "change_group_layout_in_rota_report_state"
)
CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE = (
    "change_print_options_in_rota_report_state"
)

reporting_function_mapping = DisplayAndPostFormFunctionMaps(
    display_mappings=FormNameFunctionNameMapping(
        mapping_dict={
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
                     display_form_for_report_group_allocation_print_options,

                ROTA_REPORT_STAGE:
                    display_form_report_rota,
            GENERIC_OPTIONS_IN_ROTA_REPORT_STATE:
                    display_form_for_rota_report_generic_options,
            REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE:
                display_form_for_rota_report_additional_options,
            CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE:
                display_form_for_group_arrangement_options_rota_report,
            CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE:
                display_form_for_rota_report_print_options

        },
    parent_child_dict=
    {
    display_form_view_of_reports: (display_form_report_group_allocation, display_form_report_rota),
        display_form_report_group_allocation: (display_form_for_report_group_allocation_generic_options,),
            display_form_for_report_group_allocation_generic_options: (display_form_for_report_group_additional_options, display_form_for_group_arrangement_options_allocation_report, display_form_for_report_group_allocation_print_options),
        display_form_report_rota: (display_form_for_rota_report_generic_options,),
            display_form_for_rota_report_generic_options: (display_form_for_rota_report_additional_options, display_form_for_group_arrangement_options_rota_report, display_form_for_rota_report_print_options)
    }),
    post_mappings=FormNameFunctionNameMapping({
        INITIAL_STATE:
             post_form_view_of_reports,
         GROUP_ALLOCATION_REPORT_STAGE:
             post_form_report_group_allocation,
         GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_generic_options,
         REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
             post_form_for_report_group_additional_options,
         CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
             post_form_for_group_arrangement_options_allocation_report,
         CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
             post_form_for_report_group_allocation_print_options,

            ROTA_REPORT_STAGE:
                post_form_report_rota,
            GENERIC_OPTIONS_IN_ROTA_REPORT_STATE:
                post_form_for_rota_report_generic_options,
            REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE:
                post_form_for_rota_report_additional_options,
            CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE:
                post_form_for_group_arrangement_options_rota_report,
            CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE:
                post_form_for_rota_report_print_options
        })

)
