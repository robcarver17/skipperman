import datetime

import pandas as pd

from app.data_access.configuration.configuration import ALL_PAGESIZE, ALL_FONTS
from app.logic.events.utilities import get_event_from_state
from app.data_access.data import data
from app.logic.forms_and_interfaces.abstract_form import ListOfLines, radioInput, yes_no_radio, textInput
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.reporting.backend.reporting_options import ReportingOptionsForSpecificGroupsInReport, ReportingOptions, \
    adjust_reporting_options_to_reflect_passed_dataframe, get_list_of_natural_groups_from_df
from app.objects.reporting_options import PrintOptions, MarkedUpListFromDfParameters, ArrangeGroupsOptions, DEFAULT_ARRANGEMENT_NAME, ArrangementMethod
from app.logic.reporting.constants import *
from app.objects.constants import missing_data, arg_not_passed


def get_saved_report_options_bespoke_for_df(df: pd.DataFrame, report_type: str,
                                            default_markuplist_from_df_options: MarkedUpListFromDfParameters) -> ReportingOptionsForSpecificGroupsInReport:

    print_options = data.data_print_options.read_for_report(report_type)

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


def get_saved_print_options(report_type: str,interface: abstractInterface) -> PrintOptions:
    print_options = data.data_print_options.read_for_report(report_type)
    print_options.title_str = get_report_title(report_type=report_type,interface=interface)
    print_options.filename = get_report_filename(report_title=print_options.title_str, interface=interface)

    return print_options

def get_report_title(report_type: str,interface: abstractInterface)->str:
    title = interface.get_persistent_value(REPORT_TITLE)
    if title is missing_data:
        event_name = get_event_from_state(interface)
        title = "%s: %s" % (report_type, event_name)
        interface.set_persistent_value(REPORT_TITLE, title)

    return title

def get_report_filename(report_title: str,interface: abstractInterface)->str:
    filename = interface.get_persistent_value(REPORT_FILENAME)
    if filename is missing_data:
        filename = get_default_filename_for_report(report_title)
        interface.set_persistent_value(REPORT_FILENAME, filename)

    return filename

def save_print_options(report_type: str, interface: abstractInterface, print_options: PrintOptions):
    interface.set_persistent_value(REPORT_TITLE, print_options.title_str)
    interface.set_persistent_value(REPORT_FILENAME, print_options.filename)

    ## although title and filename are written they are never used
    data.data_print_options.write_for_report(report_name=report_type, print_options=print_options)

def get_default_filename_for_report(default_title: str) -> str:

    default_file_name = default_title.replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    default_file_name = "%s_%s.pdf" % (default_file_name, timestamp)

    return default_file_name


all_pagesize_as_dict = dict([(pagesize, pagesize) for pagesize in ALL_PAGESIZE])
all_fonts_as_dict = dict([(font, font) for font in ALL_FONTS])


def report_print_options_as_form_contents(
    print_options: PrintOptions
) -> ListOfLines:

    landscape_str = (
        "Landscape"
        if print_options.landscape
        else "Portrait"
    )

    return ListOfLines(
        [
        radioInput(input_label="Alignment", input_name=PAGE_ALIGNMENT, dict_of_options=dict(Landscape ='Landscape', portrait ='Portrait'), default_label=landscape_str),
        radioInput(input_label="Font", input_name=FONT, dict_of_options=all_fonts_as_dict, default_label=print_options.font),
        radioInput(input_label="Page size", input_name=PAGE_SIZE, dict_of_options=all_pagesize_as_dict, default_label=print_options.page_size),
        yes_no_radio(input_label="Equalise column widths", input_name=EQUALISE_COLUMN_WIDTHS, default_is_yes=print_options.equalise_column_width),
        textInput(input_label="Report title", input_name=REPORT_TITLE, value=print_options.title_str),
        textInput(input_label="Filename", input_name=REPORT_FILENAME, value = print_options.filename),
        yes_no_radio(input_label="Put group name as header", input_name=GROUP_NAME_AS_HEADER, default_is_yes=print_options.include_group_as_header),
        yes_no_radio(input_label="Highlight first value in group", input_name=FIRST_VALUE_IN_GROUP_IS_KEY, default_is_yes=print_options.first_value_in_group_is_key),
        yes_no_radio(input_label="Prepend group name to all entries", input_name=PREPEND_GROUP_NAME, default_is_yes=print_options.prepend_group_name),

        ]
    )

"""
        Line(["Groups arranged in the following order: %s " % report_options.marked_up_list_from_df.actual_group_order, Button(
            CHANGE_GROUP_ORDER_BUTTON)]),
            Line([
                "Columns arranged in the following way: %s " %  report_options.describe_arrange_groups(),
                Button(CHANGE_GROUP_ARRANGEMENT_BUTTON)]),
"""

def get_print_options_from_main_option_form_fields(interface: abstractInterface) -> PrintOptions:
    ## doesn't get order or arrangement
    page_alignment = interface.value_from_form(PAGE_ALIGNMENT)
    font = interface.value_from_form(FONT)
    page_size = interface.value_from_form(PAGE_SIZE)
    equalise_column_widths = interface.true_if_radio_was_yes(EQUALISE_COLUMN_WIDTHS)
    title = interface.value_from_form(REPORT_TITLE)
    filename = interface.value_from_form(REPORT_FILENAME)
    group_name_as_header = interface.true_if_radio_was_yes(GROUP_NAME_AS_HEADER)
    highlight_first_value_as_key = interface.true_if_radio_was_yes(FIRST_VALUE_IN_GROUP_IS_KEY)
    prepend_group_name = interface.true_if_radio_was_yes(PREPEND_GROUP_NAME)

    print_options = PrintOptions()

    print_options.landscape = page_alignment
    print_options.font = font
    print_options.page_size = page_size
    print_options.equalise_column_width =equalise_column_widths
    print_options.title_str = title
    print_options.filename = filename
    print_options.include_group_as_header = group_name_as_header
    print_options.prepend_group_name = prepend_group_name
    print_options.first_value_in_group_is_key = highlight_first_value_as_key

    return print_options

def report_print_options_as_list_of_lines(
    print_options: PrintOptions
) -> ListOfLines:

    landscape_str = (
        "Landscape"
        if print_options.landscape
        else "Portrait"
    )

    return ListOfLines(
        [
        "Alignment: %s" % landscape_str,
        "Font: %s" % print_options.font,
        "Page size: %s"  % print_options.page_size,
        "Equalise column widths: %s" % print_options.equalise_column_width,
        "Report title: %s" % print_options.title_str, ## FIXME REPLACE WITH DEFAULT NAME - DYNAMICALLY GENERATE DON'T SAVE??
        "Filename: %s" % print_options.filename, ## FIXME REPLACE WITH DEFAULT NAME
        "Put group name as header: %s" % print_options.include_group_as_header,
        "Highlight first value in group: %s" % print_options.first_value_in_group_is_key,
        "Prepend group name to all entries: %s" % print_options.prepend_group_name,

        ]
    )


def get_list_of_natural_groups( interface: abstractInterface, marked_up_list_from_df_parameters: MarkedUpListFromDfParameters, df: pd.DataFrame,) -> list:
    groups = get_stored_natural_groups(interface)
    if groups is missing_data:
        groups_if_not_stored = get_list_of_natural_groups_from_df(df=df, marked_up_list_from_df_parameters=marked_up_list_from_df_parameters)
        save_list_of_natural_groups(interface=interface, groups_in_order=groups_if_not_stored)
        return groups_if_not_stored
    else:
        return groups

def get_stored_natural_groups(interface: abstractInterface) -> list:
    groups = interface.get_persistent_value(GROUP_ORDER)
    return groups

def save_list_of_natural_groups(interface: abstractInterface, groups_in_order: list):
    interface.set_persistent_value(GROUP_ORDER, groups_in_order)

def get_stored_arrangement(interface: abstractInterface) -> ArrangeGroupsOptions:
    arrangement_method = interface.get_persistent_value(ARRANGE_GROUP_LAYOUT_METHOD)
    if arrangement_method is missing_data:
        arrangement_method = DEFAULT_ARRANGEMENT_NAME
        interface.set_persistent_value(ARRANGE_GROUP_LAYOUT_METHOD, arrangement_method)

    arrangement_order = interface.get_persistent_value(ARRANGE_GROUP_LAYOUT_ORDER)
    if arrangement_order is missing_data:
        arrangement_order = arg_not_passed

    return ArrangeGroupsOptions(arrangement=ArrangementMethod[arrangement_method], force_order_of_columns_list_of_indices=arrangement_order)

def save_arrangement(interface: abstractInterface, arrangement_options: ArrangeGroupsOptions):
    interface.set_persistent_value(ARRANGE_GROUP_LAYOUT_METHOD, arrangement_options.arrangement.name)
    if arrangement_options.force_order_of_columns_list_of_indices is not arg_not_passed:
        interface.set_persistent_value(ARRANGE_GROUP_LAYOUT_ORDER, arrangement_options.force_order_of_columns_list_of_indices)