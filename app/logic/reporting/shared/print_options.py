from app.data_access.configuration.fixed import ALL_PAGESIZE, ALL_FONTS
from app.data_access.data import data
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import (
    yes_no_radio, textInput, radioInput,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_text import bold, Heading
from app.logic.reporting.constants import (
    REPORT_TITLE,
    REPORT_FILENAME,
    PAGE_ALIGNMENT,
    FONT,
    PAGE_SIZE,
    EQUALISE_COLUMN_WIDTHS,
    GROUP_NAME_AS_HEADER,
    FIRST_VALUE_IN_GROUP_IS_KEY,
    PREPEND_GROUP_NAME, OUTPUT_PDF,
PUBLIC
)
from app.objects.constants import missing_data
from app.backend.reporting.options_and_parameters.print_options import PrintOptions, default_report_title_and_filename, \
    get_default_filename_for_report


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

    print("Loaded saved print shared %s" % str(print_options))
    return print_options


def get_report_title_from_storage_or_use_default(
    report_type: str, interface: abstractInterface
) -> str:
    title = interface.get_persistent_value(REPORT_TITLE)
    if title is missing_data:
        event = get_event_from_state(interface)
        title = default_report_title_and_filename(event=event, report_type=report_type)
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
    print("Saving print shared %s" % str(print_options))
    interface.set_persistent_value(REPORT_TITLE, print_options.title_str)
    interface.set_persistent_value(REPORT_FILENAME, print_options.filename)

    ## although title and filename are written here as well they are never used
    data.data_print_options.write_for_report(
        report_name=report_type, print_options=print_options
    )


def report_print_options_as_list_of_lines(print_options: PrintOptions) -> ListOfLines:
    landscape_str = "Landscape" if print_options.landscape else "Portrait"
    output_pdf = print_options.output_pdf
    output_pdf_str = "Output to .pdf file" if output_pdf else "Output to .csv file"
    public = print_options.publish_to_public
    public_str = "Output to public directory with shareable web link" if public else "Save in private directory"
    output_pdf_line = Line(output_pdf_str)
    public_pdf_line = Line(public_str)

    if output_pdf:
        pdf_only = ListOfLines(
            [
                "Alignment: %s" % landscape_str,
                "Font: %s" % print_options.font,
                "Page size: %s" % print_options.page_size,
                "Equalise column widths: %s" % print_options.equalise_column_width,
                "Report title: %s" % print_options.title_str,
                "Highlight first value in group: %s"
                % print_options.first_value_in_group_is_key,
            ])
    else:
        pdf_only = ListOfLines([])

    generic = ListOfLines(
        [
            "Filename: %s" % print_options.filename_with_extension,
            "Put group name as header: %s" % print_options.include_group_as_header,
            "Prepend group name to all entries: %s" % print_options.prepend_group_name,
        ]
    )
    output = ListOfLines(
        output_pdf_line+
        public_pdf_line+
        pdf_only+
        generic
    )

    return  output.add_Lines()



def get_print_options_from_main_option_form_fields(
    interface: abstractInterface,
) -> PrintOptions:
    ## doesn't get order or arrangement
    print("Getting print shared")
    page_alignment = interface.value_from_form(PAGE_ALIGNMENT)
    output_to = interface.value_from_form(OUTPUT_PDF)
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
    public = interface.true_if_radio_was_yes(PUBLIC)
    print_options = PrintOptions()

    print_options.landscape = page_alignment == LANDSCAPE
    print_options.output_pdf = output_to ==PDF
    print_options.font = font
    print_options.page_size = page_size
    print_options.equalise_column_width = equalise_column_widths
    print_options.title_str = title
    print_options.filename = filename
    print_options.include_group_as_header = group_name_as_header
    print_options.prepend_group_name = prepend_group_name
    print_options.first_value_in_group_is_key = highlight_first_value_as_key
    print_options.publish_to_public = public

    print("Print shared from form %s" % str(print_options))
    return print_options


def report_print_options_as_form_contents(print_options: PrintOptions) -> ListOfLines:
    landscape_str = LANDSCAPE if print_options.landscape else PORTRAIT
    output_to_str = PDF if print_options.output_pdf else CSV

    print_options_form =  ListOfLines(
        [
            _______________,

            radioInput(
                input_label="Output to:",
                input_name=OUTPUT_PDF,
                dict_of_options={PDF:PDF, CSV: CSV},
                default_label=output_to_str,
            ),
            _______________,

            yes_no_radio(
                input_label="Output to public with shareable web link (ensure no private information!)",
                input_name=PUBLIC
            ),
            _______________,
            _______________,
            bold("Following only apply to .pdf files"),
            _______________,
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
            yes_no_radio(
                input_label="Highlight first value in group",
                input_name=FIRST_VALUE_IN_GROUP_IS_KEY,
                default_is_yes=print_options.first_value_in_group_is_key,
            ),

            _______________,
            _______________,
            bold("Following apply to all types of output:"),
            _______________,
            textInput(
                input_label="Filename (without .pdf or .csv extension)",
                input_name=REPORT_FILENAME,
                value=print_options.filename,
            ),
            yes_no_radio(
                input_label="Put group name as header",
                input_name=GROUP_NAME_AS_HEADER,
                default_is_yes=print_options.include_group_as_header,
            ),
            yes_no_radio(
                input_label="Prepend group name to all entries",
                input_name=PREPEND_GROUP_NAME,
                default_is_yes=print_options.prepend_group_name,
            ),
            _______________,

        ]
    )
    return print_options_form.add_Lines()


def get_saved_print_options_and_create_form(
    interface: abstractInterface, report_type: str, report_for: str = ""
) -> ListOfLines:
    print_options = get_saved_print_options(report_type=report_type, interface=interface)
    report_options_within_form = report_print_options_as_form_contents(print_options)

    return ListOfLines(
        [
            Heading("%s: Select additional parameters for %s" % (report_type, report_for), centred=False,
                    size=5),
            report_options_within_form,
        ]
    ).add_Lines()


all_pagesize_as_dict = dict([(pagesize, pagesize) for pagesize in ALL_PAGESIZE])
all_fonts_as_dict = dict([(font, font) for font in ALL_FONTS])
LANDSCAPE = "Landscape"
PORTRAIT = "Portrait"

PDF = "pdf"
CSV = "csv"


