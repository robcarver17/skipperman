from app.backend.mapping.list_of_field_mappings import (
    save_field_mapping_template,
    get_list_of_field_mapping_template_names,
)
from app.data_access.csv.wa_field_mapping import read_mapping_from_csv_file_object
from app.objects.abstract_objects.abstract_form import textInput, fileInput, Form
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
    get_file_from_interface,
)

empty_name = ""


def display_form_for_upload_template_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons_for_template()
    template_name_field = textInput(
        input_name=TEMPLATE_NAME, input_label="Enter template name", value=empty_name
    )
    file_select_field = fileInput(input_name=MAPPING_FILE, accept=".csv")
    list_of_template_names = get_list_of_field_mapping_template_names(
        interface.object_store
    )

    if len(list_of_template_names) > 0:
        list_of_template_names_str = ", ".join(list_of_template_names)
        existing_names_line = Line(
            "Enter a new name, or an existing template name to overwrite: %s"
            % list_of_template_names_str
        )
    else:
        existing_names_line = ""

    list_of_lines = ListOfLines(
        [
            Line(
                "Choose .csv file to upload as a mapping template, providing template name"
            ),
            existing_names_line,
            Line(template_name_field),
            Line(file_select_field),
            buttons,
        ]
    )

    return Form(list_of_lines)


def get_upload_buttons_for_template():
    return ButtonBar([cancel_menu_button, upload_button])


def post_form_for_upload_template_field_mapping(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(
        display_form_for_upload_template_field_mapping
    )
    if last_button == cancel_menu_button.name:
        return previous_form

    template_name = interface.value_from_form(TEMPLATE_NAME)
    if len(template_name) < 4:
        interface.log_error("Template name needs to be longer")
        return display_form_for_upload_template_field_mapping(interface)
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        template = read_mapping_from_csv_file_object(file)
    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_for_upload_template_field_mapping(interface)

    save_field_mapping_template(
        template_name=template_name,
        object_store=interface.object_store,
        template=template,
    )
    interface.flush_cache_to_store()

    return form_with_message_and_finished_button(
        "Uploaded new template %s" % (template_name),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_upload_template_field_mapping,
    )


MAPPING_FILE = "file"
TEMPLATE_NAME = "template_name"

UPLOAD_FILE_BUTTON_LABEL = "Upload selected file"
upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("upload_template_file_help")
