from app.objects.constants import (
    missing_data,
    NoFileUploaded,
    FileError,
    arg_not_passed,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    YES, NO,
)
from app.objects.abstract_objects.abstract_buttons import FINISHED_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________


finished_button = Button(FINISHED_BUTTON_LABEL)

class abstractInterface(object):
    def log_error(self, error_message: str):
        raise NotImplemented

    def log_message(self, log_message: str):
        raise NotImplemented

    def print_logs(self) -> ListOfLines:
        raise NotImplemented

    def set_where_finished_button_should_lead_to(self, stage_name: str):
        self.set_persistent_value(FINISHED_BUTTON_LABEL, stage_name)

    def get_where_finished_button_should_lead_to(self, default: str)-> str:
        return self.get_persistent_value(FINISHED_BUTTON_LABEL, default=default)

    def clear_where_finished_button_should_lead_to(self):
        return self.clear_persistent_value(FINISHED_BUTTON_LABEL)

    def get_persistent_value(self, key, default=missing_data):
        return self.persistent_store.get(key, default)

    def set_persistent_value(self, key, value):
        self.persistent_store[key] = value

    def clear_persistent_value(self, key):
        del(self.persistent_store[key])

    @property
    def persistent_store(self) -> dict:
        raise NotImplemented

    @property
    def is_initial_stage_form(self) -> bool:
        raise NotImplemented

    def reset_to_initial_stage_form(self):
        raise NotImplemented

    @property
    def form_name(self) -> str:
        raise NotImplemented

    @form_name.setter
    def form_name(self, new_stage):
        raise NotImplemented

    def clear_persistent_data_for_action_and_reset_to_initial_stage_form(self):
        raise NotImplemented

    def clear_persistent_data_except_specified_fields(self, specified_fields: list):
        raise NotImplemented

    @property
    def is_posted_form(self) -> bool:
        raise NotImplemented

    def value_from_form(self, key: str, value_is_date: bool = False):
        raise NotImplemented

    def value_of_multiple_options_from_form(self, key: str) -> list:
        raise NotImplemented

    def true_if_radio_was_yes(self, input_label: str) -> bool:
        value = self.value_from_form(input_label)
        if value == YES:
            return True
        elif value == NO:
            return False
        else:
            raise Exception("Value %s is not a yes or no option!" % str(value))

    def last_button_pressed(self, button_name: str = arg_not_passed) -> str:
        raise NotImplemented

    def uploaded_file(self, input_name: str = "file"):
        raise NoFileUploaded


def get_file_from_interface(file_label: str, interface: abstractInterface):
    try:
        file = interface.uploaded_file(file_label)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    return file


def form_with_message_and_finished_button(
    message: str, interface: abstractInterface,
        button: Button = finished_button,
        set_stage_name_to_go_to_on_button_press: str = arg_not_passed,
        log_error: str = arg_not_passed,
        log_msg: str = arg_not_passed

) -> Form:
    if log_error is not arg_not_passed:
        interface.log_error(log_error)
    elif log_msg is not arg_not_passed:
        interface.log_message(log_msg)

    if set_stage_name_to_go_to_on_button_press is not arg_not_passed:
        interface.set_where_finished_button_should_lead_to(set_stage_name_to_go_to_on_button_press)
    else:
        interface.clear_where_finished_button_should_lead_to()

    return form_with_content_and_finished_button(content = Line(message), interface=interface, button=button)

def form_with_content_and_finished_button(
    content, interface: abstractInterface,
        button: Button = finished_button
) -> Form:
    return Form(
        ListOfLines(
            [
                interface.print_logs(),
                _______________,
                content,
                _______________,
                Line(button),
            ]
        )
    )

