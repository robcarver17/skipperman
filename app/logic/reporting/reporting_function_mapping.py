from app.logic.reporting.ENTRY_view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.logic.reporting.rota.report_rota import *

from app.logic.reporting.allocations.report_group_allocations import *

from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings



reporting_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
    {
        (display_form_view_of_reports, post_form_view_of_reports): {

            (display_form_report_group_allocation,post_form_report_group_allocation) : {
                    (display_form_for_report_group_allocation_generic_options,post_form_for_report_group_allocation_generic_options):
                        {
                            (display_form_for_report_group_additional_options,post_form_for_report_group_additional_options): 0,
                            (display_form_for_group_arrangement_options_allocation_report,post_form_for_group_arrangement_options_allocation_report): 0,
                            (display_form_for_report_group_allocation_print_options,post_form_for_report_group_allocation_print_options): 0

                        }
            },
            (display_form_report_rota, post_form_report_rota): {
                    (display_form_for_rota_report_generic_options,post_form_for_rota_report_generic_options):
                        {
                                (display_form_for_rota_report_additional_options,post_form_for_rota_report_additional_options):0,
                                ( display_form_for_group_arrangement_options_rota_report,post_form_for_group_arrangement_options_rota_report):0,
                                (  display_form_for_rota_report_print_options,post_form_for_rota_report_print_options): 0
                        }
            }}

    }
    )
)
