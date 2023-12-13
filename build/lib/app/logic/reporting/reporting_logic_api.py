from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.reporting.view_list_of_reports import (
    display_form_view_of_reports,
    post_form_view_of_reports,
)
from app.logic.reporting.allocations.report_group_allocations import *


class ReportingLogicApi(AbstractLogicApi):
    def get_displayed_form_given_form_name(self, form_name: str):
        if form_name == INITIAL_STATE:
            return display_form_view_of_reports(self.interface)

        elif form_name == GROUP_ALLOCATION_REPORT_STAGE:
            return display_form_report_group_allocation(self.interface)
        elif form_name == REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
            return display_form_for_report_group_additional_options(self.interface)
        elif form_name == GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
            return display_form_for_report_group_allocation_generic_options(
                self.interface
            )
        elif form_name == CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
            return display_form_for_group_arrangement_options_allocation_report(self.interface)
        elif form_name == CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
            return display_form_for_report_group_allocation_print_options(
                self.interface
            )
        else:
            raise Exception("Form name %s not recognised" % form_name)

    def get_posted_form_given_form_name_without_checking_for_redirection(
        self, form_name: str
    ) -> Form:
        if form_name == INITIAL_STATE:
            return post_form_view_of_reports(self.interface)

        elif form_name == GROUP_ALLOCATION_REPORT_STAGE:
            return post_form_report_group_allocation(self.interface)
        elif form_name == REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT:
            return post_form_for_report_group_allocation_options(self.interface)
        elif form_name == GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE:
            return post_form_for_report_group_allocation_generic_options(self.interface)
        elif form_name == CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE:
            return post_form_for_group_arrangement_options_allocation_report(self.interface)
        elif form_name == CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE:
            return post_form_for_report_group_allocation_print_options(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)
