from dataclasses import dataclass
from typing import Callable

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.store.data_access import DataLayer
from app.data_access.store.object_store import ObjectStore

from app.objects.exceptions import (
    missing_data,
    NoFileUploaded,
    FileError,
    arg_not_passed,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    YES,
    NO,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import FINISHED_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
)

finished_button = Button(FINISHED_BUTTON_LABEL)
DISPLAY = "DISPFLAG_%s"
SET = "1"


def finished_button_with_custom_label(label: str):
    return Button(value=FINISHED_BUTTON_LABEL, label=label)


@dataclass
class abstractInterface:
    data: DataLayer
    object_store: ObjectStore
    display_and_post_form_function_maps: DisplayAndPostFormFunctionMaps = arg_not_passed
    action_name: str = ""

    def make_backup_of_data(self):
        self.data.ba

    def delete_all_data(self, are_you_sure: bool = False):
        self.data.delete_all_data(are_you_sure=are_you_sure)

    ## SHOULD BE DONE ON NEW PAGE DISPLAY?? AND A MESS!
    def flush_cache_to_store(self):
        self.object_store.flush_store()
        self._save_data_store_cache() ## FIXME REMOVE EVENTUALLY
        self._clear_data_store_cache() ## FIXME REMOVE EVENTUALLY
        self._clear_adhoc_cache() ## ## FIXME REMOVE EVENTUALLY

    def clear_cache(self):
        self.object_store.clear_store()

    def _clear_data_store_cache(self):
        self.data.clear_stored_items()

    def _save_data_store_cache(self):
        if self.read_only:
            self.log_error("Read only mode - not saving changes")
            return
        self.data.save_stored_items()

    def _clear_adhoc_cache(self):
        try:
            del(self._cache)
        except:
            pass

    def log_error(self, error_message: str):
        raise NotImplemented

    def set_where_finished_button_should_lead_to(self, stage_name: str):
        self.set_persistent_value(FINISHED_BUTTON_LABEL, stage_name)

    def get_where_finished_button_should_lead_to(self, default: str) -> str:
        return self.get_persistent_value(FINISHED_BUTTON_LABEL, default=default)

    def clear_where_finished_button_should_lead_to(self):
        return self.clear_persistent_value(FINISHED_BUTTON_LABEL)

    def get_persistent_value(self, key, default=missing_data):
        raise NotImplemented

    def set_persistent_value(self, key, value):
        raise NotImplemented

    def clear_persistent_value(self, key):
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
        self.reset_to_initial_stage_form()  ## this should happen anyway, but belt and braces
        self.clear_persistent_data_for_action()

    def clear_persistent_data_for_action(self):
        raise NotImplemented

    def clear_persistent_data_except_specified_fields(self, specified_fields: list):
        raise NotImplemented

    @property
    def is_posted_form(self) -> bool:
        raise NotImplemented

    def value_from_form(self, key: str, value_is_date: bool = False):
        raise NotImplemented

    def value_of_multiple_options_from_form(
        self, key: str, default=arg_not_passed
    ) -> list:
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
        form_name = self.display_and_post_form_function_maps.get_form_name_for_function(
            func
        )
        return NewForm(form_name)

    def get_new_display_form_for_parent_of_function(self, func: Callable) -> NewForm:
        form_name = self.display_and_post_form_function_maps.get_display_form_name_for_parent_of_function(
            func
        )
        return NewForm(form_name)


    def get_current_logged_in_username(self) -> str:
        raise NotImplemented

    @property
    def read_only(self):
        raise NotImplemented

    @property
    def cache(self) -> AdHocCache:
        cache = getattr(self, '_cache', None)
        if cache is None:
            cache = self._cache = AdHocCache(self.data)

        return cache

def get_file_from_interface(file_label: str, interface: abstractInterface):
    try:
        file = interface.uploaded_file(file_label)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    return file


def form_with_message_and_finished_button(
    message: str,
    interface: abstractInterface,
    button: Button = finished_button,
    function_whose_parent_go_to_on_button_press: Callable = arg_not_passed,
    log_error: str = arg_not_passed,
    log_msg: str = arg_not_passed,
) -> Form:
    if log_error is not arg_not_passed:
        interface.log_error(log_error)
    elif log_msg is not arg_not_passed:
        interface.log_error(log_msg)

    if function_whose_parent_go_to_on_button_press is not arg_not_passed:
        stage_name = interface.get_new_display_form_for_parent_of_function(
            function_whose_parent_go_to_on_button_press
        )
        interface.set_where_finished_button_should_lead_to(stage_name.form_name)
    else:
        interface.clear_where_finished_button_should_lead_to()

    return form_with_content_and_finished_button(
        content=Line(message),  button=button
    )


def form_with_content_and_finished_button(
    content,  button: Button = finished_button
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


@dataclass
class UrlsOfInterest:
    current_url_for_action: str = arg_not_passed
    image_directory: str = arg_not_passed
