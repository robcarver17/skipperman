import os
import datetime
from typing import List
import pandas as pd
from logic.data_and_interface import DataAndInterface
from interface.reporting.reporting_options import (
    ReportingOptions,
    ReportingOptionsForSpecificGroupsInReport,
    PrintOptions,
    ArrangeGroupsOptions,
    MarkedUpListFromDfParameters,
    adjust_reporting_options_to_reflect_passed_dataframe,
    describe_arrangement,
    ARRANGE_OPTIMISE,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
    POSSIBLE_ARRANGEMENTS,
)
from data_access.configuration.configuration import ALL_PAGESIZE, ALL_FONTS


def choose_reporting_options(
    df: pd.DataFrame,
    data_and_interface: DataAndInterface,
    default_markuplist_from_df_options: MarkedUpListFromDfParameters,
    default_title: str,
) -> ReportingOptionsForSpecificGroupsInReport:

    default_path = data_and_interface.interface.starting_directory_for_reporting
    default_path_and_filename = get_default_path_and_filename(
        default_path=default_path, default_title=default_title
    )

    report_options = get_default_report_options(
        df=df,
        default_markuplist_from_df_options=default_markuplist_from_df_options,
        default_title=default_title,
        default_path_and_filename=default_path_and_filename,
    )

    interactively_modify_report_options_in_place(
        data_and_interface=data_and_interface, report_options=report_options
    )

    return report_options


def get_default_path_and_filename(default_path: str, default_title: str) -> str:

    default_file_name = default_title.replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    default_file_name = "%s_%s.pdf" % (default_file_name, timestamp)

    default_path_and_filename = os.path.join(default_path, default_file_name)

    return default_path_and_filename


def get_default_report_options(
    df: pd.DataFrame,
    default_path_and_filename: str,
    default_title: str,
    default_markuplist_from_df_options: MarkedUpListFromDfParameters,
) -> ReportingOptionsForSpecificGroupsInReport:

    print_options = PrintOptions(
        path_and_filename=default_path_and_filename,
        title_str=default_title,
    )

    arrange_group_options = ArrangeGroupsOptions()

    reporting_options_before_adjustment = ReportingOptions(
        marked_up_list_from_df=default_markuplist_from_df_options,  ## report specific
        arrange_groups=arrange_group_options,
        print_options=print_options,
    )

    reporting_options = adjust_reporting_options_to_reflect_passed_dataframe(
        df=df, reporting_options_before_adjustment=reporting_options_before_adjustment
    )

    return reporting_options


def interactively_modify_report_options_in_place(
    data_and_interface: DataAndInterface,
    report_options: ReportingOptionsForSpecificGroupsInReport,
):

    interface = data_and_interface.interface
    still_choosing = True
    while still_choosing:
        dict_of_descriptions = report_options_as_dict_of_str(report_options)
        report_options_interactive_dict = OptionsInteractiveDict(dict_of_descriptions)
        menu_options = (
            report_options_interactive_dict.list_of_menu_options_including_no_change()
        )
        choice = interface.get_choice_from_adhoc_menu(
            menu_options,
            prompt="Choose configuration to change, or choose no changes required",
        )

        if report_options_interactive_dict.menu_choice_is_no_change(choice):
            return  ## in place changes return nothing

        ## change reporting options in place
        key_of_option_chosen = report_options_interactive_dict.key_of_chosen_option(
            choice
        )
        modify_a_single_reporting_option(
            data_and_interface=data_and_interface,
            key_of_option_chosen=key_of_option_chosen,
            report_options=report_options,
        )


NO_CHANGES = "No changes required"


class OptionsInteractiveDict(object):
    def __init__(self, dict_of_descriptions: dict):

        self._dict_of_descriptions = dict_of_descriptions

    @property
    def dict_of_descriptions(self) -> dict:
        return self._dict_of_descriptions

    def list_of_menu_options_including_no_change(self) -> list:
        menu_options = [NO_CHANGES] + self.list_of_menu_options()
        return menu_options

    def list_of_menu_options(self) -> list:
        return list(self.dict_of_descriptions.values())

    def list_of_menu_keys(self) -> list:
        return list(self.dict_of_descriptions.keys())

    def menu_choice_is_no_change(self, choice) -> bool:
        return choice == NO_CHANGES

    def key_of_chosen_option(self, choice: str) -> str:
        list_of_options = self.list_of_menu_options()
        index_of_option = list_of_options.index(choice)
        list_of_keys = self.list_of_menu_keys()
        return list_of_keys[index_of_option]


def report_options_as_dict_of_str(
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> dict:

    ## print options
    landscape_str = (
        "Alignment: Landscape"
        if report_options.print_options.landscape
        else "Alignment: Portrait"
    )
    font_str = "Font: %s" % report_options.print_options.font
    page_size_str = "Page size: %s" % report_options.print_options.page_size
    equalise_column_width = (
        "Equalise column widths"
        if report_options.print_options.equalise_column_width
        else "Size columns differently"
    )
    title_str = "Title: %s" % report_options.print_options.title_str
    output_file_str = (
        "Output to path & file: %s" % report_options.print_options.path_and_filename
    )

    group_order = "Include groups in following order: %s" % str(
        report_options.marked_up_list_from_df.actual_group_order
    )

    order_of_columns = report_options.describe_arrange_groups()

    include_group_as_header_str = (
        "Put group name as header"
        if report_options.marked_up_list_from_df.include_group_as_header
        else "Do not put group name as header over group"
    )
    prepend_group_name = (
        "Prepend group name to all entries"
        if report_options.marked_up_list_from_df.prepend_group_name
        else "Do not prepend group name"
    )
    first_value_in_group_is_key = (
        "Highlight first value in group"
        if report_options.marked_up_list_from_df.first_value_in_group_is_key
        else "Do not highlight first value in group"
    )

    return {
        "landscape": landscape_str,
        "font": font_str,
        "page_size": page_size_str,
        "equalise_column_width": equalise_column_width,
        "title_str": title_str,
        "path_and_filename": output_file_str,
        "group_order": group_order,
        "order_of_columns": order_of_columns,
        "include_group_as_header": include_group_as_header_str,
        "prepend_group_name": prepend_group_name,
        "first_value_in_group_is_key": first_value_in_group_is_key,
    }


def modify_a_single_reporting_option(
    report_options: ReportingOptionsForSpecificGroupsInReport,
    key_of_option_chosen: str,
    data_and_interface: DataAndInterface,
):
    ## TERRIBLE HACKY, KEYS MUST MATCH KEYS RETURNED ABOVE
    interface = data_and_interface.interface
    if key_of_option_chosen == "landscape":
        report_options.print_options.landscape = interface.return_true_if_answer_is_yes(
            "Landscape report (say no for portrait?)"
        )
    elif key_of_option_chosen == "font":
        report_options.print_options.font = interface.get_choice_from_adhoc_menu(
            ALL_FONTS, prompt="Choose font"
        )
    elif key_of_option_chosen == "page_size":
        report_options.print_options.page_size = interface.get_choice_from_adhoc_menu(
            ALL_PAGESIZE, prompt="Page size?"
        )
    elif key_of_option_chosen == "equalise_column_width":
        report_options.print_options.equalise_column_width = (
            interface.return_true_if_answer_is_yes("Equalise column widths?")
        )
    elif key_of_option_chosen == "title_str":
        report_options.print_options.title_str = (
            interface.get_input_from_user_and_convert_to_type(
                "Report title", type_expected=str
            )
        )

    elif key_of_option_chosen == "path_and_filename":
        path_name = interface.select_path("Select path for report")
        file_name = interface.get_input_from_user_and_convert_to_type(
            "Enter filename including .pdf suffix: ", type_expected=str
        )
        report_options.print_options.path_and_filename = os.path.join(
            path_name, file_name
        )
    elif key_of_option_chosen == "group_order":
        ordered_groups = report_options.marked_up_list_from_df.actual_group_order
        new_order = interface.put_items_in_order(
            ordered_groups, prompt="Put groups in desired order"
        )
        report_options.marked_up_list_from_df.actual_group_order = new_order

    elif key_of_option_chosen == "order_of_columns":
        dict_of_arrangements_and_descriptions = (
            get_dict_of_arrangements_and_descriptions()
        )
        interactive_options = OptionsInteractiveDict(
            dict_of_arrangements_and_descriptions
        )
        chosen_arrangement_description = interface.get_choice_from_adhoc_menu(
            interactive_options.list_of_menu_options(),
            prompt="How to layout columns on page?",
        )
        chosen_arrangement = interactive_options.key_of_chosen_option(
            chosen_arrangement_description
        )
        if chosen_arrangement is ARRANGE_PASSED_LIST:
            interface.message("Can't do this yet not implemented")
            return  # no change
            # ordered_groups = report_options.marked_up_list_from_df.actual_group_order
            # new_order = interface.create_nested_list_from_items(ordered_groups, prompt="Put groups in desired order")
            ## NOTE: the order is indicies, not group names!
            # report_options.arrange_groups.force_order_of_columns_list_of_indices = new_order
        report_options.arrange_groups.arrangement = chosen_arrangement

    elif key_of_option_chosen == "include_group_as_header":
        report_options.marked_up_list_from_df.include_group_as_header = (
            interface.return_true_if_answer_is_yes("Include name as group as header?")
        )
    elif key_of_option_chosen == "prepend_group_name":
        report_options.marked_up_list_from_df.prepend_group_name = (
            interface.return_true_if_answer_is_yes(
                "Prepend group name before each entry?"
            )
        )
    elif key_of_option_chosen == "first_value_in_group_is_key":
        report_options.marked_up_list_from_df.first_value_in_group_is_key = (
            interface.return_true_if_answer_is_yes(
                "Highlight first entry in each group?"
            )
        )
    else:
        raise Exception(
            "Key %s not recognised as reporting option" % key_of_option_chosen
        )


def get_dict_of_arrangements_and_descriptions():
    return dict(
        [
            (arrangement, describe_arrangement(arrangement))
            for arrangement in POSSIBLE_ARRANGEMENTS
        ]
    )
