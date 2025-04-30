import datetime
from typing import Union

from app.backend.volunteers.refresh_skills_from_csv_import import (
    create_skills_refresh_file,
)
from app.data_access.configuration.configuration import (
    ALLOWED_UPLOAD_FILE_TYPES,
    IMPORT_SKILLS_CONFIG,
    WEBLINK_FOR_QUALIFICATIONS,
)
from app.frontend.volunteers.iterate_over_imported_volunteer_skills import (
    begin_iteration_over_rows_in_temp_volunteer_file,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm, fileInput
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

UPLOAD_FILE_BUTTON_LABEL = "Upload file"

import_skills_config = IMPORT_SKILLS_CONFIG  ## caps are nasty


def display_form_refresh_volunteer_skills(
    interface: abstractInterface,  ## unused but always passed
) -> Union[Form, NewForm]:
    header_bar = ButtonBar([HelpButton("import_membership_list_help")])

    description = ListOfLines(
        [
            "Refresh key skills held by volunteers according to imported skills file with expiry",
            _______________,
            "Get the file from %s, and export the first page to .csv"
            % WEBLINK_FOR_QUALIFICATIONS,
        ]
    ).add_Lines()
    prompt = Line(
        "File to upload (must be a csv or xls with following columns: %s with date in format eg %s)"
        % (import_skills_config.all_columns_from_csv(), EXAMPLE_DATE_FORMAT)
    )
    buttons = ButtonBar([back_menu_button, upload_button])
    input_field = Line(fileInput(input_name=FILENAME, accept=ALLOWED_UPLOAD_FILE_TYPES))

    list_of_lines = ListOfLines(
        [
            header_bar,
            _______________,
            description,
            _______________,
            prompt,
            input_field,
            buttons,
        ]
    )

    return Form(list_of_lines)


EXAMPLE_DATE_FORMAT = datetime.date.today().strftime(import_skills_config.date_format)

upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)
FILENAME = "filename"


def post_form_refresh_volunteer_skills(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if upload_button.pressed(button_pressed):
        return respond_to_uploaded_file(interface)
    elif back_menu_button.pressed(button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_refresh_volunteer_skills
    )


def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    create_skills_refresh_file(interface=interface, file_marker_name=FILENAME)

    return begin_iteration_over_rows_in_temp_volunteer_file(interface)
