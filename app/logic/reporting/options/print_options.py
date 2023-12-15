from app.data_access.configuration.configuration import ALL_PAGESIZE, ALL_FONTS
from app.data_access.data import data
from app.logic.events.utilities import get_event_from_state
from app.logic.forms_and_interfaces.abstract_form import (
    ListOfLines,
    yes_no_radio, _______________, textInput, radioInput,
)
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.reporting.constants import (
    REPORT_TITLE,
    REPORT_FILENAME,
    PAGE_ALIGNMENT,
    FONT,
    PAGE_SIZE,
    EQUALISE_COLUMN_WIDTHS,
    GROUP_NAME_AS_HEADER,
    FIRST_VALUE_IN_GROUP_IS_KEY,
    PREPEND_GROUP_NAME,
)
from app.objects.constants import missing_data
from app.reporting.options_and_parameters.print_options import PrintOptions, get_default_filename_for_report


def get_saved_print_options(
    report_type: str, interface: abstractInterface
) -> PrintOptions:
    print_options = data.data_print_options.read_for_report(report_type)
    print_options.title_str = get_report_title_from_storage_or_use_default(
        report_type=report_type, interface=interface
    )
    print_options.filename = get_report_filename_from_storage_or_use_default(
        report_title=print_options.title_str, interface=interface
    )

    print("Loaded saved print options %s" % str(print_options))
    return print_options


def get_report_title_from_storage_or_use_default(
    report_type: str, interface: abstractInterface
) -> str:
    title = interface.get_persistent_value(REPORT_TITLE)
    if title is missing_data:
        event_name = get_event_from_state(interface)
        title = "%s: %s" % (report_type, event_name)
        interface.set_persistent_value(REPORT_TITLE, title)

    return title


def get_report_filename_from_storage_or_use_default(
    report_title: str, interface: abstractInterface
) -> str:
    filename = interface.get_persistent_value(REPORT_FILENAME)
    if filename is missing_data:
        filename = get_default_filename_for_report(report_title)
        interface.set_persistent_value(REPORT_FILENAME, filename)

    return filename


def save_print_options(
    report_type: str, interface: abstractInterface, print_options: PrintOptions
):
    print("Saving print options %s" % str(print_options))
    interface.set_persistent_value(REPORT_TITLE, print_options.title_str)
    interface.set_persistent_value(REPORT_FILENAME, print_options.filename)

    ## although title and filename are written here as well they are never used
    data.data_print_options.write_for_report(
        report_name=report_type, print_options=print_options
    )


def report_print_options_as_list_of_lines(print_options: PrintOptions) -> ListOfLines:
    landscape_str = "Landscape" if print_options.landscape else "Portrait"

    return ListOfLines(
        [
            "Alignment: %s" % landscape_str,
            "Font: %s" % print_options.font,
            "Page size: %s" % print_options.page_size,
            "Equalise column widths: %s" % print_options.equalise_column_width,
            "Report title: %s" % print_options.title_str,
            "Filename: %s" % print_options.filename,
            "Put group name as header: %s" % print_options.include_group_as_header,
            "Highlight first value in group: %s"
            % print_options.first_value_in_group_is_key,
            "Prepend group name to all entries: %s" % print_options.prepend_group_name,
        ]
    )


def get_print_options_from_main_option_form_fields(
    interface: abstractInterface,
) -> PrintOptions:
    ## doesn't get order or arrangement
    print("Getting print options")
    page_alignment = interface.value_from_form(PAGE_ALIGNMENT)
    font = interface.value_from_form(FONT)
    page_size = interface.value_from_form(PAGE_SIZE)
    equalise_column_widths = interface.true_if_radio_was_yes(EQUALISE_COLUMN_WIDTHS)
    title = interface.value_from_form(REPORT_TITLE)
    filename = interface.value_from_form(REPORT_FILENAME)
    group_name_as_header = interface.true_if_radio_was_yes(GROUP_NAME_AS_HEADER)
    highlight_first_value_as_key = interface.true_if_radio_was_yes(
        FIRST_VALUE_IN_GROUP_IS_KEY
    )
    prepend_group_name = interface.true_if_radio_was_yes(PREPEND_GROUP_NAME)

    print_options = PrintOptions()

    print_options.landscape = page_alignment == LANDSCAPE
    print_options.font = font
    print_options.page_size = page_size
    print_options.equalise_column_width = equalise_column_widths
    print_options.title_str = title
    print_options.filename = filename
    print_options.include_group_as_header = group_name_as_header
    print_options.prepend_group_name = prepend_group_name
    print_options.first_value_in_group_is_key = highlight_first_value_as_key

    print("Print options from form %s" % str(print_options))
    return print_options


def report_print_options_as_form_contents(print_options: PrintOptions) -> ListOfLines:
    landscape_str = LANDSCAPE if print_options.landscape else PORTRAIT

    return ListOfLines(
        [
            radioInput(
                input_label="Alignment",
                input_name=PAGE_ALIGNMENT,
                dict_of_options={LANDSCAPE:LANDSCAPE, PORTRAIT:PORTRAIT},
                default_label=landscape_str,
            ),
            radioInput(
                input_label="Font",
                input_name=FONT,
                dict_of_options=all_fonts_as_dict,
                default_label=print_options.font,
            ),
            radioInput(
                input_label="Page size",
                input_name=PAGE_SIZE,
                dict_of_options=all_pagesize_as_dict,
                default_label=print_options.page_size,
            ),
            yes_no_radio(
                input_label="Equalise column widths",
                input_name=EQUALISE_COLUMN_WIDTHS,
                default_is_yes=print_options.equalise_column_width,
            ),
            textInput(
                input_label="Report title",
                input_name=REPORT_TITLE,
                value=print_options.title_str,
            ),
            textInput(
                input_label="Filename",
                input_name=REPORT_FILENAME,
                value=print_options.filename,
            ),
            yes_no_radio(
                input_label="Put group name as header",
                input_name=GROUP_NAME_AS_HEADER,
                default_is_yes=print_options.include_group_as_header,
            ),
            yes_no_radio(
                input_label="Highlight first value in group",
                input_name=FIRST_VALUE_IN_GROUP_IS_KEY,
                default_is_yes=print_options.first_value_in_group_is_key,
            ),
            yes_no_radio(
                input_label="Prepend group name to all entries",
                input_name=PREPEND_GROUP_NAME,
                default_is_yes=print_options.prepend_group_name,
            ),
        ]
    )


def get_saved_print_options_and_create_form(
    interface: abstractInterface, report_type: str, report_for: str = ""
) -> ListOfLines:
    print_options = get_saved_print_options(report_type=report_type, interface=interface)
    report_options_within_form = report_print_options_as_form_contents(print_options)

    return ListOfLines(
        [
            "%s: Select print options for %s" % (report_type, report_for),
            _______________,
            report_options_within_form,
        ]
    )


all_pagesize_as_dict = dict([(pagesize, pagesize) for pagesize in ALL_PAGESIZE])
all_fonts_as_dict = dict([(font, font) for font in ALL_FONTS])
LANDSCAPE = "Landscape"
PORTRAIT = "Portrait"
