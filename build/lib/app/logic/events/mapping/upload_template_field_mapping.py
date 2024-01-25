from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import TEMPLATE_NAME, MAPPING_FILE, UPLOAD_FILE_BUTTON_LABEL
from app.backend.read_and_write_mapping_files import read_mapping_from_csv_file_object, write_template
from app.objects.abstract_objects.abstract_form import textInput, fileInput, Form
from app.objects.abstract_objects.abstract_buttons import cancel_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_interface import abstractInterface, get_file_from_interface, \
    form_with_message_and_finished_button

empty_name = ""


def display_form_for_upload_template_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons_for_template()
    template_name_field = textInput(
        input_name=TEMPLATE_NAME, input_label="Enter template name", value=empty_name
    )
    file_select_field = fileInput(input_name=MAPPING_FILE, accept=".csv")

    list_of_lines = ListOfLines(
        [
            "Choose .csv file to upload as a mapping template, providing template name",
            template_name_field,
            file_select_field,
            buttons,
        ]
    )

    return Form(list_of_lines)


def get_upload_buttons_for_template():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)

    return Line([cancel_button, upload])


def post_form_for_upload_template_field_mapping(interface: abstractInterface):
    template_name = interface.value_from_form(TEMPLATE_NAME)
    if len(template_name) < 4:
        interface.log_error("Template name needs to be longer")
        return initial_state_form
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
    except Exception as e:
        interface.log_error("Something went wrong uploading file %s" % str(e))
        return initial_state_form
    print("template name %s, mapping %s" % (template_name, str(mapping)))
    write_template(template_name=template_name, new_mapping=mapping)

    return form_with_message_and_finished_button(
        "Uploaded new template %s" % (template_name), interface=interface
    )
