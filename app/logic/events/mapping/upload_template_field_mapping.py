from app.logic.events.constants import TEMPLATE_NAME, MAPPING_FILE, UPLOAD_FILE_BUTTON_LABEL
from app.backend.wa_import.map_wa_fields import write_template, read_mapping_from_csv_file_object,get_list_of_template_names
from app.objects.abstract_objects.abstract_form import textInput, fileInput, Form
from app.objects.abstract_objects.abstract_buttons import  Button, ButtonBar, cancel_menu_button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import abstractInterface, get_file_from_interface, \
    form_with_message_and_finished_button

empty_name = ""


def display_form_for_upload_template_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons_for_template()
    template_name_field = textInput(
        input_name=TEMPLATE_NAME, input_label="Enter template name", value=empty_name
    )
    file_select_field = fileInput(input_name=MAPPING_FILE, accept=".csv")
    list_of_template_names = get_list_of_template_names(interface.data)


    if len(list_of_template_names)>0:
        list_of_template_names_str = ", ".join(list_of_template_names)
        existing_names_line = Line("Enter a new name, or an existing template name to overwrite: %s" % list_of_template_names_str)
    else:
        existing_names_line = ''

    list_of_lines = ListOfLines(
        [
            Line("Choose .csv file to upload as a mapping template, providing template name"),
            existing_names_line,
            Line(template_name_field),
            Line(file_select_field),
            buttons,
        ]
    )

    return Form(list_of_lines)


def get_upload_buttons_for_template():

    return ButtonBar([cancel_menu_button, upload_button])


upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)

def post_form_for_upload_template_field_mapping(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(display_form_for_upload_template_field_mapping)
    if last_button == cancel_menu_button.name:
        return previous_form

    template_name = interface.value_from_form(TEMPLATE_NAME)
    if len(template_name) < 4:
        interface.log_error("Template name needs to be longer")
        return display_form_for_upload_template_field_mapping(interface)
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
    except Exception as e:
        interface.log_error("Something went wrong uploading file: error %s" % str(e))
        return display_form_for_upload_template_field_mapping(interface)

    print("template name %s, mapping %s" % (template_name, str(mapping)))
    write_template(template_name=template_name, new_mapping=mapping, data_layer=interface.data)
    interface.flush_cache_to_store()


    return form_with_message_and_finished_button("Uploaded new template %s" % (template_name), interface=interface,
                                                 function_whose_parent_go_to_on_button_press=display_form_for_upload_template_field_mapping)
