from app.frontend.reporting.ENTRY_view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.frontend.reporting.rota.report_rota import *
from app.frontend.reporting.allocations.report_group_allocations import *
from app.frontend.reporting.boats.report_boats import *
from app.frontend.reporting.rollcall_and_contacts.rollcall_report import *
from app.frontend.reporting.sailors.ENTRY_report_sailors import *
from app.frontend.reporting.sailors.qualification_status import *
from app.frontend.reporting.patrol_boats.report_patrol_boats import *
from app.frontend.reporting.all_event_data.ENTRY_all_event_data import (
    display_form_for_all_event_data_report,
    post_form_for_for_all_event_data_report,
)
from app.frontend.reporting.data_dumps.ENTRY_data_dump import (
    display_form_for_data_dump_report,
    post_form_for_data_dump_report,
)
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)


reporting_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_view_of_reports, post_form_view_of_reports): {
                (
                    display_form_report_group_allocation,
                    post_form_report_group_allocation,
                ): {
                    (
                        display_form_for_report_group_allocation_all_options,
                        post_form_for_report_group_allocation_all_options,
                    ): {
                        (
                            display_form_for_report_group_additional_options,
                            post_form_for_report_group_additional_options,
                        ): 0,
                        (
                            display_form_for_group_arrangement_options_allocation_report,
                            post_form_for_group_arrangement_options_allocation_report,
                        ): 0,
                        (
                            display_form_for_report_group_allocation_print_options,
                            post_form_for_report_group_allocation_print_options,
                        ): 0,
                    }
                },
                (display_form_report_rota, post_form_report_rota): {
                    (
                        display_form_for_rota_report_all_options,
                        post_form_for_rota_report_all_options,
                    ): {
                        (
                            display_form_for_rota_report_additional_options,
                            post_form_for_rota_report_additional_options,
                        ): 0,
                        (
                            display_form_for_group_arrangement_options_rota_report,
                            post_form_for_group_arrangement_options_rota_report,
                        ): 0,
                        (
                            display_form_for_rota_report_print_options,
                            post_form_for_rota_report_print_options,
                        ): 0,
                    }
                },
                (display_form_report_patrol_boats, post_form_report_patrol_boats): {
                    (
                        display_form_for_patrol_boats_all_options,
                        post_form_for_patrol_boats_report_all_options,
                    ): {
                        (
                            display_form_for_patrol_boats_additional_options,
                            post_form_for_patrol_boats_report_additional_options,
                        ): 0,
                        (
                            display_form_for_patrol_boats_arrangement_options_report,
                            post_form_for_group_arrangement_options_patrol_boats_report,
                        ): 0,
                        (
                            display_form_for_patrol_boats_report_print_options,
                            post_form_for_patrol_boats_report_print_options,
                        ): 0,
                    }
                },
                (display_form_report_boat, post_form_report_boat): {
                    (
                        display_form_for_boat_report_all_options,
                        post_form_for_boat_report_all_options,
                    ): {
                        (
                            display_form_for_boat_report_additional_options,
                            post_form_for_boat_report_additional_options,
                        ): 0,
                        (
                            display_form_for_group_arrangement_options_boat_report,
                            post_form_for_group_arrangement_options_boat_report,
                        ): 0,
                        (
                            display_form_for_boat_report_print_options,
                            post_form_for_boat_report_print_options,
                        ): 0,
                    }
                },
                (display_form_report_rollcall, post_form_report_rollcall): {
                    (
                        display_form_for_rollcall_report_all_options,
                        post_form_for_rollcall_report_all_options,
                    ): {
                        (
                            display_form_for_rollcall_report_additional_options,
                            post_form_for_rollcall_report_additional_options,
                        ): 0,
                        (
                            display_form_for_group_arrangement_options_rollcall_report,
                            post_form_for_group_arrangement_options_rollcall_report,
                        ): 0,
                        (
                            display_form_for_rollcall_report_print_options,
                            post_form_for_rollcall_report_print_options,
                        ): 0,
                    }
                },
                (
                    display_form_for_sailors_report,
                    post_form_for_sailors_report,
                ): {
                    (
                        display_form_for_qualification_status_report,
                        post_form_for_qualification_status_report,
                    ): 0
                },
                (
                    display_form_for_all_event_data_report,
                    post_form_for_for_all_event_data_report,
                ): 0,
                (display_form_for_data_dump_report, post_form_for_data_dump_report): 0,
            }
        }
    )
)
