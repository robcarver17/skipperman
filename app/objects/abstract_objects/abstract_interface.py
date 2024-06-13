from dataclasses import dataclass
from typing import Callable

from app.data_access.storage_layer.api import DataLayer

from app.objects.constants import (
    missing_data,
    NoFileUploaded,
    FileError,
    arg_not_passed,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    YES, NO, NewForm,
)
from app.objects.abstract_objects.abstract_buttons import FINISHED_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.form_function_mapping import DisplayAndPostFormFunctionMaps

finished_button = Button(FINISHED_BUTTON_LABEL)
DISPLAY="DISPFLAG_%s"
SET= "1"

def finished_button_with_custom_label(label:str):
    return Button(value=FINISHED_BUTTON_LABEL, label=label)

@dataclass
class abstractInterface:
    data: DataLayer
    display_and_post_form_function_maps: DisplayAndPostFormFunctionMaps = arg_not_passed
    action_name: str = ""

    def due_for_another_data_backup(self):
        return self.data.due_for_another_data_backup()

    def make_data_backup(self):
        self.data.make_data_backup()

    def clear_stored_items(self):
        self.data.clear_stored_items()

    def save_stored_items(self):
        self.data.save_stored_items()

    def log_error(self, error_message: str):
        raise NotImplemented

    def set_where_finished_button_should_lead_to(self, stage_name: str):
        self.set_persistent_value(FINISHED_BUTTON_LABEL, stage_name)

    def get_where_finished_button_should_lead_to(self, default: str)-> str:
        return self.get_persistent_value(FINISHED_BUTTON_LABEL, default=default)

    def clear_where_finished_button_should_lead_to(self):
        return self.clear_persistent_value(FINISHED_BUTTON_LABEL)

    def display_flag_set(self, flag_key):
        value = self.get_persistent_value(DISPLAY % flag_key, default=False)
        return value == SET

    def set_display_flag(self, flag_key, set_to:bool):
        key = DISPLAY % flag_key
        if set_to:
            self.set_persistent_value(key, SET)
        else:
            self.clear_persistent_value(key)

    def get_persistent_value(self, key, default=missing_data):
        return self.persistent_store.get(key, default)

    def set_persistent_value(self, key, value):
        self.persistent_store[key] = value

    def clear_persistent_value(self, key):
        del(self.persistent_store[key])

    @property
    def persistent_store(self) -> dict:
        store = getattr(self, '_store', None)
        if store is None:
            store = dict()
            self._store = store

        return store

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

    def value_of_multiple_options_from_form(self, key: str, default=arg_not_passed) -> list:
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

    def get_new_form_given_function(self, func: Callable) -> NewForm:
        form_name = self.display_and_post_form_function_maps.get_form_name_for_function(func)
        return NewForm(form_name)

    def get_new_display_form_for_parent_of_function(self, func: Callable) -> NewForm:
        form_name = self.display_and_post_form_function_maps.get_display_form_name_for_parent_of_function(func)
        return NewForm(form_name)

    def url_for_password_reset(self, username: str, new_password: str):
        raise NotImplemented

    def get_current_logged_in_username(self) -> str:
        raise NotImplemented

    @property
    def read_only(self)-> bool:
        return False

    def toggle_read_only(self):
        raise NotImplemented

def get_file_from_interface(file_label: str, interface: abstractInterface):
    try:
        file = interface.uploaded_file(file_label)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    return file


def form_with_message_and_finished_button(message: str, interface: abstractInterface, button: Button = finished_button,
                                          function_whose_parent_go_to_on_button_press: Callable = arg_not_passed,
                                          log_error: str = arg_not_passed, log_msg: str = arg_not_passed) -> Form:
    if log_error is not arg_not_passed:
        interface.log_error(log_error)
    elif log_msg is not arg_not_passed:
        interface.log_error(log_msg)

    if function_whose_parent_go_to_on_button_press is not arg_not_passed:
        stage_name= interface.get_new_display_form_for_parent_of_function(function_whose_parent_go_to_on_button_press)
        interface.set_where_finished_button_should_lead_to(stage_name.form_name)
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
                _______________,
                content,
                _______________,
                Line(button),
            ]
        )
    )

