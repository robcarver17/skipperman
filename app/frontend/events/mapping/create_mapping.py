import pandas as pd

from app.OLD_backend.wa_import.map_wa_fields import temp_mapping_file_name
from app.OLD_backend.wa_import.load_wa_file import (
    get_staged_file_raw_event_filename,
    load_raw_wa_file,
)
from app.data_access.configuration.field_list_groups import ALL_FIELDS_AS_PD_SERIES
from app.frontend.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.frontend.events.constants import UPLOAD_MAPPING_BUTTON_LABEL
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.mapping.download_template_field_mapping import (
    display_form_for_download_template_field_mapping,
)
from app.frontend.events.mapping.upload_field_mapping import (
    display_form_for_upload_custom_field_mapping,
)
from app.objects_OLD.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
    BACK_BUTTON_LABEL,
)
from app.objects_OLD.abstract_objects.abstract_form import Form, NewForm, File
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________

DOWNLOAD_MAPPING_BUTTON_LABEL = (
    "Download a mapping .csv file to edit (which you can then upload)"
)
DOWNLOAD_FIELD_NAMES_BUTTON_LANEL = (
    "Download a .csv file of field names to use in creating a mapping file"
)
DOWNLOAD_DEFINED_LIST_BUTTON_LABEL = "Download a .csv file of WA field names used in the current event file waiting for import"


def display_form_for_create_custom_field_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    wa_field_button = get_wa_field_download_button(interface)
    contents_of_form = ListOfLines(
        [
            "Tools to create mapping for event %s" % str(event),
            _______________,
            ButtonBar(
                [
                    back_menu_button,
                    Button(DOWNLOAD_MAPPING_BUTTON_LABEL, nav_button=True),
                    Button(DOWNLOAD_FIELD_NAMES_BUTTON_LANEL, nav_button=True),
                    wa_field_button,
                    Button(UPLOAD_MAPPING_BUTTON_LABEL, nav_button=True),
                ]
            ),
        ]
    )

    return Form(contents_of_form)


def get_wa_field_download_button(interface: abstractInterface):
    try:
        get_wa_file_from_staging(interface)
        return Button(DOWNLOAD_DEFINED_LIST_BUTTON_LABEL, nav_button=True)
    except:
        ## There is no WA file imported
        return ""


def post_form_for_create_custom_field_mapping(
    interface: abstractInterface,
):
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == DOWNLOAD_MAPPING_BUTTON_LABEL:
        return download_template_form(interface)

    elif last_button_pressed == DOWNLOAD_FIELD_NAMES_BUTTON_LANEL:
        return download_field_names_form()

    elif last_button_pressed == DOWNLOAD_DEFINED_LIST_BUTTON_LABEL:
        return download_WA_event_field_names_form(interface)

    elif last_button_pressed == UPLOAD_MAPPING_BUTTON_LABEL:
        return custom_mapping_form(interface)

    elif last_button_pressed == BACK_BUTTON_LABEL:
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
        wa_as_df = get_wa_file_from_staging(interface)
        df_of_fields = pd.Series(list(wa_as_df.columns))
    except:
        df_of_fields = pd.Series("No WA file: must have already been imported")
    filename = temp_mapping_file_name()
    df_of_fields.to_csv(filename, index=False)

    return File(filename)


def get_wa_file_from_staging(interface: abstractInterface):
    event = get_event_from_state(interface)
    filename = get_staged_file_raw_event_filename(event.id)
    wa_as_df = load_raw_wa_file(filename)

    return wa_as_df
