import pandas as pd
from app.objects.events import Event

from app.backend.mapping.list_of_field_mappings import temp_mapping_file_name
from app.backend.wild_apricot.load_wa_file import (
    get_staged_file_raw_event_filename,
    does_raw_event_file_exist,
)
from app.backend.file_handling import load_spreadsheet_file_and_clear_nans
from app.data_access.configuration.field_list_groups import ALL_FIELDS_AS_PD_SERIES
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.mapping.download_template_field_mapping import (
    display_form_for_download_template_field_mapping,
)
from app.frontend.events.mapping.upload_field_mapping import (
    display_form_for_upload_custom_field_mapping,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________


def display_form_for_create_custom_field_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    buttons = get_buttons_for_custom_mapping(interface=interface)
    contents_of_form = ListOfLines(
        ["Tools to create mapping for event %s" % str(event), _______________, buttons]
    )

    return Form(contents_of_form)


def get_buttons_for_custom_mapping(interface: abstractInterface):

    wa_field_button = get_wa_field_download_button(interface)

    bar = \
        [
            back_menu_button,
            help_button,
            upload_new_mapping_button,
            download_mapping_button,
            download_field_names_button,
            wa_field_button,
        ]


    return ButtonBar(bar)


def get_wa_field_download_button(interface: abstractInterface):
    try:
        event = get_event_from_state(interface)
        get_wa_file_from_staging(event)
        return download_defined_list_button
    except:
        ## There is no WA file imported
        return ""


def post_form_for_create_custom_field_mapping(
    interface: abstractInterface,
):
    last_button_pressed = interface.last_button_pressed()

    if download_mapping_button.pressed(last_button_pressed):
        return download_template_form(interface)

    elif download_field_names_button.pressed(last_button_pressed):
        return download_field_names_form()

    elif download_defined_list_button.pressed(last_button_pressed):
        return download_WA_event_field_names_form(interface)

    elif upload_new_mapping_button.pressed(last_button_pressed):
        return custom_mapping_form(interface)

    elif back_menu_button.pressed(last_button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)  #


def custom_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_upload_custom_field_mapping
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_for_create_custom_field_mapping
    )


def download_template_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_for_download_template_field_mapping
    )


def download_field_names_form():
    df_of_fields = ALL_FIELDS_AS_PD_SERIES
    filename = temp_mapping_file_name()
    df_of_fields.to_csv(filename, index=False)

    return File(filename)


def download_WA_event_field_names_form(interface: abstractInterface):
    try:
        event = get_event_from_state(interface)
        wa_as_df = get_wa_file_from_staging(event)
        df_of_fields = pd.Series(list(wa_as_df.columns))
    except:
        df_of_fields = pd.Series("No WA file: must have already been imported")

    filename = temp_mapping_file_name()
    df_of_fields.to_csv(filename, index=False)

    return File(filename)


def get_wa_file_from_staging(event: Event):
    filename = get_staged_file_raw_event_filename(event)
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)

    return wa_as_df


DOWNLOAD_MAPPING_BUTTON_LABEL = (
    "Download a mapping .csv file to edit (which you can then upload)"
)
download_mapping_button = Button(DOWNLOAD_MAPPING_BUTTON_LABEL, nav_button=True)

DOWNLOAD_FIELD_NAMES_BUTTON_LANEL = (
    "Download a .csv file of Skipperman fields to use in creating a mapping file"
)
download_field_names_button = Button(DOWNLOAD_FIELD_NAMES_BUTTON_LANEL, nav_button=True)

DOWNLOAD_DEFINED_LIST_BUTTON_LABEL = "Download a .csv file of WA field names used in the current uploaded event file"
download_defined_list_button = Button(
    DOWNLOAD_DEFINED_LIST_BUTTON_LABEL, nav_button=True
)

UPLOAD_MAPPING_BUTTON_LABEL = "Upload new mapping .csv file"
upload_new_mapping_button = Button(UPLOAD_MAPPING_BUTTON_LABEL, nav_button=True)


help_button = HelpButton("create_mapping_template")
