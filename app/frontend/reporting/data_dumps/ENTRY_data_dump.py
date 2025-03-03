from typing import Union

from app.backend.volunteers.volunteer_data_dump import get_volunteer_data_dump
from app.data_access.init_directories import temp_file_name_in_download_directory
from app.objects.abstract_objects.abstract_text import Heading


from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File,
    NewForm,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
)

dict_of_dump_options_and_functions_to_generate_df = {
    "Volunteer data": get_volunteer_data_dump
}


def display_form_for_data_dump_report(interface: abstractInterface):
    title = Heading("Select data to dump", centred=True, size=4)
    list_of_buttons_as_line = Line(
        [
            button_given_data_name(data_name)
            for data_name in dict_of_dump_options_and_functions_to_generate_df.keys()
        ]
    )
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, back_menu_button]),
            title,
            list_of_buttons_as_line,
        ]
    )

    return Form(contents_of_form)


def post_form_for_data_dump_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return previous_form(interface)

    for data_name in list(dict_of_dump_options_and_functions_to_generate_df.keys()):
        button = button_given_data_name(data_name)
        if button.pressed(last_button):
            func_to_call = dict_of_dump_options_and_functions_to_generate_df.get(
                data_name
            )
            df = func_to_call(object_store=interface.object_store)
            filename = temp_file_name_in_download_directory()

            df.to_csv(filename, index=False)

            return File(filename)

    raise Exception("Uknown button")


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_for_data_dump_report
    )


def button_given_data_name(data_name: str):
    return Button(data_name, tile=True)
