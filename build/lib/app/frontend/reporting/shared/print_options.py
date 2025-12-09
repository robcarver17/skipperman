from typing import Union

from app.backend.reporting.options_and_parameters.get_and_update_print_options import (
    get_print_options,
    reset_print_options_to_default,
    update_print_options,
)
from app.backend.reporting.options_and_parameters.print_options import (
    PrintOptions,
    default_report_title_and_filename,
    get_default_filename_for_report,
)
from app.backend.reporting.process_stages.create_file_from_list_of_columns import (
    web_pathname_of_public_version_of_local_report_file,
)
from app.data_access.configuration.fixed import ALL_PAGESIZE, ALL_FONTS
from app.frontend.forms.form_utils import is_radio_yes_or_no
from app.frontend.shared.events_state import get_event_from_state
from app.backend.reporting.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import (
    yes_no_radio,
    textInput,
    radioInput,
    intInput,
    Link,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_text import bold, Heading
from app.frontend.reporting.shared.constants import (
    REPORT_TITLE,
    REPORT_FILENAME,
    PAGE_ALIGNMENT,
    FONT,
    PAGE_SIZE,
    EQUALISE_COLUMN_WIDTHS,
    GROUP_NAME_AS_HEADER,
    FIRST_VALUE_IN_GROUP_IS_KEY,
    PREPEND_GROUP_NAME,
    OUTPUT_PDF,
    PUBLIC,
    IF_HEADER_INCLUDE_SIZE,
    FONT_SIZE, INCLUDE_ROW_NUMBER, DROP_GROUP_NAME_FROM_COLUMNS,
)
from app.objects.utilities.exceptions import missing_data, MISSING_FROM_FORM


def override_print_options_with_new_values(
    print_options: PrintOptions, publish_to_public=False, **kwargs
) -> PrintOptions:
    kwargs["publish_to_public"] = publish_to_public
    for key, value in kwargs.items():
        setattr(print_options, key, value)

    return print_options


def get_saved_print_options(
    report_type: str,
    interface: abstractInterface,
    ignore_stored_values_and_use_default: bool = False,
) -> PrintOptions:
    print_options = get_print_options(
        object_store=interface.object_store,
        report_name=report_type,
        ignore_stored_values_and_use_default=ignore_stored_values_and_use_default,
    )
    print_options.title_str = get_report_title_from_storage_or_use_default(
        report_type=report_type,
        interface=interface,
        ignore_stored_values_and_use_default=ignore_stored_values_and_use_default,
    )
    print_options.filename = get_report_filename_from_storage_or_use_default(
        report_title=print_options.title_str,
        interface=interface,
        ignore_stored_values_and_use_default=ignore_stored_values_and_use_default,
    )

    print("Loaded saved print shared %s" % str(print_options))
    return print_options


def get_report_title_from_storage_or_use_default(
    report_type: str,
    interface: abstractInterface,
    ignore_stored_values_and_use_default: bool = False,
) -> str:
    title = interface.get_persistent_value(REPORT_TITLE)
    if title is missing_data or ignore_stored_values_and_use_default:
        event = get_event_from_state(interface)
        title = default_report_title_and_filename(event=event, report_type=report_type)
        interface.set_persistent_value(REPORT_TITLE, title)

    return title


def get_report_filename_from_storage_or_use_default(
    report_title: str,
    interface: abstractInterface,
    ignore_stored_values_and_use_default: bool = False,
) -> str:
    filename = interface.get_persistent_value(REPORT_FILENAME)
    if filename is missing_data or ignore_stored_values_and_use_default:
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
    update_print_options(
        object_store=interface.object_store,
        report_name=report_type,
        print_options=print_options,
    )


def report_print_options_as_list_of_lines(print_options: PrintOptions) -> ListOfLines:
    landscape_str = "Landscape" if print_options.landscape else "Portrait"
    output_pdf = print_options.output_pdf
    output_pdf_str = "Output to .pdf file" if output_pdf else "Output to .csv file"
    public_str = get_url_or_keep_private(print_options)

    publish_to_public = print_options.publish_to_public
    use_qr_button = qr_button if publish_to_public else ""

    output_pdf_line = Line(output_pdf_str)
    public_pdf_line = Line([public_str, use_qr_button])

    if print_options.auto_font_size:
        font_size = "Automatic"
    else:
        font_size = print_options.auto_font_size

    if output_pdf:
        pdf_only = ListOfLines(
            [
                "Alignment: %s" % landscape_str,
                "Font: %s" % print_options.font,
                "Font size: %s" % font_size,
                "Page size: %s" % print_options.page_size,
                "Equalise column widths: %s" % print_options.equalise_column_width,
                "Report title: %s" % print_options.title_str,
                "Highlight first value in group: %s"
                % print_options.first_value_in_group_is_key,
            ]
        )
    else:
        pdf_only = ListOfLines([])

    generic = ListOfLines(
        [
            "Filename: %s" % print_options.filename_with_extension,
            "Put group name as header: %s" % print_options.include_group_as_header,
            "Prepend group name to all entries: %s" % print_options.prepend_group_name,
            "If prepending, include size of group: %s"
            % print_options.include_size_of_group_if_header,
            "Include row number: %s" % print_options.include_row_count,
            "Drop group name from columns: %s" % print_options.drop_group_from_columns
        ]
    )
    output = ListOfLines(output_pdf_line + public_pdf_line + pdf_only + generic)

    return output.add_Lines()


def get_url_or_keep_private(print_options: PrintOptions):
    publish_to_public = print_options.publish_to_public
    if publish_to_public:
        web_path_of_file = web_pathname_of_public_version_of_local_report_file(
            print_options
        )

        text = "Output to public directory with shareable web link: "
        return Line(
            [
                text,
                Link(
                    url=web_path_of_file,
                    string=web_path_of_file,
                    open_new_window=True,
                ),
            ]
        )
    else:
        return "Save in private directory"


qr_button = Button(
    "Get QR code for report",
)


def get_print_options_from_main_option_form_fields(
    interface: abstractInterface,
) -> PrintOptions:
    ## doesn't get order or arrangement
    print("Getting print shared")
    page_alignment = interface.value_from_form(
        PAGE_ALIGNMENT, default=MISSING_FROM_FORM
    )
    output_to = interface.value_from_form(OUTPUT_PDF, default=MISSING_FROM_FORM)
    font = interface.value_from_form(FONT, default=MISSING_FROM_FORM)
    font_size = interface.value_from_form(FONT_SIZE, default=MISSING_FROM_FORM)
    page_size = interface.value_from_form(PAGE_SIZE, default=MISSING_FROM_FORM)
    equalise_column_widths = is_radio_yes_or_no(
        interface, EQUALISE_COLUMN_WIDTHS, default=MISSING_FROM_FORM
    )
    title = interface.value_from_form(REPORT_TITLE, default=MISSING_FROM_FORM)
    filename = interface.value_from_form(REPORT_FILENAME, default=MISSING_FROM_FORM)
    group_name_as_header = is_radio_yes_or_no(
        interface, GROUP_NAME_AS_HEADER, default=MISSING_FROM_FORM
    )
    highlight_first_value_as_key = is_radio_yes_or_no(
        interface, FIRST_VALUE_IN_GROUP_IS_KEY, default=MISSING_FROM_FORM
    )
    prepend_group_name = is_radio_yes_or_no(
        interface, PREPEND_GROUP_NAME, default=MISSING_FROM_FORM
    )
    include_size_of_group_if_header = is_radio_yes_or_no(
        interface, IF_HEADER_INCLUDE_SIZE, default=MISSING_FROM_FORM
    )
    include_row_number = is_radio_yes_or_no(interface, INCLUDE_ROW_NUMBER, default=MISSING_FROM_FORM)
    drop_column_group = is_radio_yes_or_no(interface, DROP_GROUP_NAME_FROM_COLUMNS, default=MISSING_FROM_FORM)
    public = is_radio_yes_or_no(interface, PUBLIC, default=MISSING_FROM_FORM)

    if MISSING_FROM_FORM in [
        drop_column_group,
        include_row_number,
        page_alignment,
        output_to,
        font,
        font_size,
        page_size,
        equalise_column_widths,
        title,
        filename,
        group_name_as_header,
        highlight_first_value_as_key,
        prepend_group_name,
        include_size_of_group_if_header,
        public,
    ]:
        return MISSING_FROM_FORM

    print_options = PrintOptions()

    print_options.landscape = page_alignment == LANDSCAPE
    print_options.output_pdf = output_to == PDF
    print_options.font = font
    print_options.page_size = page_size
    print_options.equalise_column_width = equalise_column_widths
    print_options.title_str = title
    print_options.filename = filename
    print_options.include_group_as_header = group_name_as_header
    print_options.prepend_group_name = prepend_group_name
    print_options.first_value_in_group_is_key = highlight_first_value_as_key
    print_options.publish_to_public = public
    print_options.include_size_of_group_if_header = include_size_of_group_if_header
    print_options.font_size = int(font_size)
    print_options.include_row_count = include_row_number
    print_options.drop_group_from_columns = drop_column_group

    print("Print shared from form %s" % str(print_options))
    return print_options


def report_print_options_as_form_contents(print_options: PrintOptions) -> ListOfLines:
    landscape_str = LANDSCAPE if print_options.landscape else PORTRAIT
    output_to_str = PDF if print_options.output_pdf else CSV

    print_options_form = ListOfLines(
        [
            _______________,
            radioInput(
                input_label="Output to:",
                input_name=OUTPUT_PDF,
                dict_of_options={PDF: PDF, CSV: CSV},
                default_label=output_to_str,
            ),
            _______________,
            yes_no_radio(
                input_label="Output to public with shareable web link (ensure no private information!)",
                input_name=PUBLIC,
                default_is_yes=print_options.publish_to_public
            ),
            _______________,
            _______________,
            bold("Following only apply to .pdf files"),
            _______________,
            radioInput(
                input_label="Alignment",
                input_name=PAGE_ALIGNMENT,
                dict_of_options={LANDSCAPE: LANDSCAPE, PORTRAIT: PORTRAIT},
                default_label=landscape_str,
            ),
            intInput(
                input_label="Font size (Set to zero for automatic sizing)",
                input_name=FONT_SIZE,
                value=print_options.font_size,
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
                input_label="Output to public with shareable web link (ensure no private information!)",
                input_name=PUBLIC,
            ),

            yes_no_radio(
                input_label="If group name is header, include size of group",
                input_name=IF_HEADER_INCLUDE_SIZE,
                default_is_yes=print_options.include_size_of_group_if_header,
            ),
            yes_no_radio(
                input_label="Prepend group name to all entries",
                input_name=PREPEND_GROUP_NAME,
                default_is_yes=print_options.prepend_group_name,
            ),
            yes_no_radio(
                input_label="Include row number",
                input_name=INCLUDE_ROW_NUMBER,
                default_is_yes=print_options.include_row_count
            ),
            yes_no_radio(
                input_label="Drop group name from columns",
                input_name=DROP_GROUP_NAME_FROM_COLUMNS,
                default_is_yes=print_options.drop_group_from_columns
            ),

            _______________,
        ]
    )
    return print_options_form.add_Lines()


def get_saved_print_options_and_create_form(
    interface: abstractInterface, report_type: str, report_for: str = ""
) -> ListOfLines:
    print_options = get_saved_print_options(
        report_type=report_type, interface=interface
    )
    report_options_within_form = report_print_options_as_form_contents(print_options)

    return ListOfLines(
        [
            Heading(
                "%s: Select additional parameters for %s" % (report_type, report_for),
                centred=False,
                size=5,
            ),
            report_options_within_form,
        ]
    ).add_Lines()


all_pagesize_as_dict = dict([(pagesize, pagesize) for pagesize in ALL_PAGESIZE])
all_fonts_as_dict = dict([(font, font) for font in ALL_FONTS])
LANDSCAPE = "Landscape"
PORTRAIT = "Portrait"

PDF = "pdf"
CSV = "csv"


def reset_print_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    reset_print_options_to_default(
        object_store=interface.object_store, report_name=report_generator.report_type
    )
    interface.clear_persistent_value(REPORT_TITLE)
    interface.clear_persistent_value(REPORT_FILENAME)


def save_print_options_from_form(
    interface: abstractInterface, report_generator: ReportGenerator
):
    specific_parameters_for_type_of_report = (
        report_generator.specific_parameters_for_type_of_report
    )

    print_options = get_print_options_from_main_option_form_fields(interface)
    if print_options is MISSING_FROM_FORM:
        interface.log_error("Couldn't get print options from form")
        return

    
    save_print_options(
        report_type=specific_parameters_for_type_of_report.report_type,
        print_options=print_options,
        interface=interface,
    )
    interface.flush_and_clear()
